#!/usr/bin/env python3
"""
DLNM Analysis — Temperature, PM2.5 and Hospitalisations in Curitiba
=====================================================================

Implements the full distributed lag non-linear model pipeline:
  1. Data loading + confounders (DOW, holidays, seasonal spline)
  2. Stationarity assessment (ADF + STL detrending)
  3. DLNM for temperature (primary) and PM2.5 (secondary)
  4. Joint model + RERI interaction test
  5. FDR correction across all tests
  6. Sensitivity analyses (lag max, seasonal df, year exclusion)
  7. Model diagnostics (dispersion, ACF, QQ, residual plots)

Usage
-----
    python dlnm_analysis.py --verbose --reri --stationarity --fdr --sensitivity-all
    python dlnm_analysis.py --exposure t_min --verbose
    python dlnm_analysis.py --exposure pm2.5_epa --lag-max 14 --verbose

References
----------
  Gasparrini A. J Stat Softw. 2011;43(8):1-20.
  Gasparrini A, et al. Lancet. 2015;386:369-375.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from scipy import stats as sp_stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import STL
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.multitest import multipletests

# Local cross-basis module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from crossbasis import (
    build_crossbasis, crosspred, crosspred_lag, crosspred_3d, CrossBasisMeta,
    natural_spline_basis, build_spline_meta, eval_spline,
)

# ── Paths ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_BASE = ROOT / "data" / "processed" / "base_dados_completa.csv"
DATA_HEALTH = ROOT / "data" / "raw" / "health" / "morb_mort_freq_2021-2024_cwb.csv"
OUT_DIR = Path(__file__).resolve().parent
FIG_DIR = OUT_DIR / "figures"
TBL_DIR = OUT_DIR / "tables"
REPORT_PATH = OUT_DIR / "dlnm_report.txt"

plt.rcParams.update({
    "font.family": "serif", "font.size": 10,
    "axes.labelsize": 11, "axes.titlesize": 12,
    "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "pdf.fonttype": 42,
})

# ── Brazilian holidays 2022-2024 (Curitiba) ──────────────────────────
HOLIDAYS_BR = [
    # 2022
    "2022-01-01", "2022-02-28", "2022-03-01", "2022-03-02",  # NY, Carnaval
    "2022-03-29",  # Curitiba anniversary
    "2022-04-15", "2022-04-21",  # Good Friday, Tiradentes
    "2022-05-01", "2022-06-16",  # Labour, Corpus Christi
    "2022-09-07", "2022-10-12", "2022-11-02", "2022-11-15",
    "2022-12-25",
    # 2023
    "2023-01-01", "2023-02-20", "2023-02-21", "2023-02-22",
    "2023-03-29",
    "2023-04-07", "2023-04-21",
    "2023-05-01", "2023-06-08",
    "2023-09-07", "2023-10-12", "2023-11-02", "2023-11-15",
    "2023-12-25",
    # 2024
    "2024-01-01", "2024-02-12", "2024-02-13", "2024-02-14",
    "2024-03-29",
    "2024-03-29", "2024-04-21",  # Good Friday same as CWB anniv in 2024
    "2024-05-01", "2024-05-30",
    "2024-09-07", "2024-10-12", "2024-11-02", "2024-11-15",
    "2024-12-25",
]
HOLIDAYS_SET = set(pd.to_datetime(HOLIDAYS_BR).normalize())


# ══════════════════════════════════════════════════════════════════════
# 1. DATA LOADING + CONFOUNDERS
# ══════════════════════════════════════════════════════════════════════

def load_data(verbose: bool = False) -> pd.DataFrame:
    """Load merged dataset with confounders."""
    base = pd.read_csv(DATA_BASE)
    base["date"] = pd.to_datetime(base["time_stamp"]).dt.normalize()

    health = pd.read_csv(DATA_HEALTH)
    health["date"] = pd.to_datetime(health["DATE"]).dt.normalize()

    df = base.merge(health[["date", "Hospitalizations"]], on="date", how="left")

    # Use freq_internacao_abs as primary (from base), fallback to Health file
    df["hosp"] = df["freq_internacao_abs"]
    mask_miss = df["hosp"].isna()
    if mask_miss.any():
        df.loc[mask_miss, "hosp"] = df.loc[mask_miss, "Hospitalizations"]
    df["hosp"] = df["hosp"].fillna(0).astype(int)

    # Day-of-week dummies (reference = Monday = 0)
    df["dow"] = df["date"].dt.dayofweek
    for d in range(1, 7):
        df[f"dow_{d}"] = (df["dow"] == d).astype(int)

    # Holiday indicator
    df["holiday"] = df["date"].isin(HOLIDAYS_SET).astype(int)

    # Time index (days since start) for seasonal spline
    df["time_idx"] = (df["date"] - df["date"].min()).dt.days

    df = df.sort_values("date").reset_index(drop=True)

    if verbose:
        print(f"  Loaded {len(df)} days ({df['date'].min().date()} to "
              f"{df['date'].max().date()})")
        print(f"  t_min valid: {df['t_min'].notna().sum()}, "
              f"pm2.5_epa valid: {df['pm2.5_epa'].notna().sum()}")
        print(f"  Hospitalizations: mean={df['hosp'].mean():.1f}, "
              f"range=[{df['hosp'].min()}, {df['hosp'].max()}]")

    return df


def _confounder_matrix(df: pd.DataFrame, seasonal_df: int = 21) -> np.ndarray:
    """Build confounder design matrix: DOW + holiday + seasonal ns()."""
    dow_cols = [f"dow_{d}" for d in range(1, 7)]
    X_conf = df[dow_cols + ["holiday"]].values.astype(float)

    # Seasonal spline on time index
    time_vals = df["time_idx"].values.astype(float)
    B_time = natural_spline_basis(time_vals, df=seasonal_df)

    return np.hstack([X_conf, B_time])


# ══════════════════════════════════════════════════════════════════════
# 2. STATIONARITY + DETRENDING
# ══════════════════════════════════════════════════════════════════════

def stationarity_analysis(df: pd.DataFrame, verbose: bool = False) -> dict:
    """ADF test + STL decomposition for hospitalisations."""
    hosp = df["hosp"].values.astype(float)

    # ADF on raw series
    adf_raw = adfuller(hosp, maxlag=14, autolag="AIC")

    # STL decomposition (period=365)
    # Need at least 2 full cycles; we have ~1096 days ≈ 3 years
    stl = STL(hosp, period=365, robust=True)
    stl_result = stl.fit()
    residuals = stl_result.resid

    # ADF on STL residuals
    adf_detrend = adfuller(residuals, maxlag=14, autolag="AIC")

    # Lag correlations on raw vs detrended
    raw_corrs = []
    det_corrs = []
    t_min = df["t_min"].values
    for lag in range(29):
        # Raw
        if lag == 0:
            h_shift = hosp
            t_shift = t_min
        else:
            h_shift = hosp[lag:]
            t_shift = t_min[:-lag]
        valid = ~(np.isnan(h_shift) | np.isnan(t_shift))
        if valid.sum() > 30:
            r, p = sp_stats.pearsonr(t_shift[valid], h_shift[valid])
            raw_corrs.append({"lag": lag, "r": r, "p": p})
        # Detrended
        if lag == 0:
            r_shift = residuals
        else:
            r_shift = residuals[lag:]
        valid2 = ~(np.isnan(r_shift) | np.isnan(t_shift))
        if valid2.sum() > 30:
            r2, p2 = sp_stats.pearsonr(t_shift[valid2], r_shift[valid2])
            det_corrs.append({"lag": lag, "r": r2, "p": p2})

    results = {
        "adf_raw": {"stat": adf_raw[0], "p": adf_raw[1], "lags": adf_raw[2]},
        "adf_detrend": {"stat": adf_detrend[0], "p": adf_detrend[1],
                        "lags": adf_detrend[2]},
        "stl_result": stl_result,
        "raw_corrs": pd.DataFrame(raw_corrs),
        "detrend_corrs": pd.DataFrame(det_corrs),
    }

    if verbose:
        print(f"\n  ADF raw hospitalisations: stat={adf_raw[0]:.3f}, "
              f"p={adf_raw[1]:.4f} ({'stationary' if adf_raw[1] < 0.05 else 'non-stationary'})")
        print(f"  ADF STL residuals:       stat={adf_detrend[0]:.3f}, "
              f"p={adf_detrend[1]:.4f} ({'stationary' if adf_detrend[1] < 0.05 else 'non-stationary'})")

    return results


def plot_stationarity(stl_result, adf_raw: dict, adf_det: dict,
                      raw_corrs: pd.DataFrame, det_corrs: pd.DataFrame):
    """4-panel figure: STL decomposition + ADF results."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel (a): STL decomposition
    ax = axes[0, 0]
    ax.plot(stl_result.observed, lw=0.5, color="black", alpha=0.7)
    ax.plot(stl_result.trend, lw=1.5, color="#d62728", label="Trend")
    ax.set_title("(a) Observed + STL trend")
    ax.set_ylabel("Hospitalisations")
    ax.legend(fontsize=8)

    # Panel (b): Seasonal + residual
    ax = axes[0, 1]
    ax.plot(stl_result.seasonal, lw=0.5, color="#2ca02c", alpha=0.7,
            label="Seasonal")
    ax.set_title("(b) STL seasonal component")
    ax.set_ylabel("Seasonal")
    ax.legend(fontsize=8)

    # Panel (c): Residual series
    ax = axes[1, 0]
    ax.plot(stl_result.resid, lw=0.5, color="#1f77b4", alpha=0.7)
    ax.axhline(0, ls="--", color="grey", lw=0.5)
    ax.set_title(f"(c) STL residuals (ADF p={adf_det['p']:.4f})")
    ax.set_ylabel("Residual")
    ax.set_xlabel("Day index")

    # Panel (d): Raw vs detrended correlations
    ax = axes[1, 1]
    if len(raw_corrs) > 0:
        ax.plot(raw_corrs["lag"], raw_corrs["r"], "o-", ms=3, lw=1,
                color="#d62728", label="Raw", alpha=0.7)
    if len(det_corrs) > 0:
        ax.plot(det_corrs["lag"], det_corrs["r"], "s-", ms=3, lw=1,
                color="#1f77b4", label="Detrended", alpha=0.7)
    ax.axhline(0, ls="--", color="grey", lw=0.5)
    ax.set_title("(d) Lag correlations: Tmin vs Hosp")
    ax.set_xlabel("Lag (days)")
    ax.set_ylabel("Pearson r")
    ax.legend(fontsize=8)

    fig.tight_layout()
    path = FIG_DIR / "fig_stationarity.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════
# 3. DLNM MODEL FITTING
# ══════════════════════════════════════════════════════════════════════

def fit_dlnm(
    df: pd.DataFrame,
    exposure_col: str,
    lag_max: int,
    exposure_df: int = 4,
    lag_df: int = 5,
    seasonal_df: int = 21,
    exposure_knots: np.ndarray | None = None,
    verbose: bool = False,
) -> dict:
    """Fit a quasi-Poisson DLNM for a single exposure.

    Returns dict with model, coefficients, vcov, meta, fitted dataframe.
    """
    # Subset to valid exposure rows
    sub = df.dropna(subset=[exposure_col]).copy()
    sub = sub.reset_index(drop=True)
    n_total = len(sub)

    # Build cross-basis
    exposure = sub[exposure_col].values
    CB, meta = build_crossbasis(
        exposure, lag_max=lag_max, exposure_df=exposure_df, lag_df=lag_df,
        exposure_knots=exposure_knots,
    )

    # Valid rows (no NaN in CB — first lag_max rows may have NaN propagation)
    valid_rows = ~np.isnan(CB).any(axis=1)
    n_valid = valid_rows.sum()

    # Confounders
    X_conf = _confounder_matrix(sub, seasonal_df=seasonal_df)

    # Full design matrix
    X = np.hstack([np.ones((n_total, 1)), CB, X_conf])
    y = sub["hosp"].values.astype(float)

    # Apply valid mask
    X_fit = X[valid_rows]
    y_fit = y[valid_rows]

    if verbose:
        print(f"\n  Fitting DLNM: {exposure_col}, lag_max={lag_max}")
        print(f"  N total={n_total}, N valid={n_valid}, "
              f"CB columns={CB.shape[1]}, total predictors={X_fit.shape[1]}")

    # Fit GLM Poisson
    model = sm.GLM(y_fit, X_fit, family=sm.families.Poisson())
    result = model.fit(scale="X2")  # quasi-Poisson via Pearson chi2 scaling

    # Extract CB coefficients (columns 1 .. n_basis)
    n_basis = meta.n_basis
    cb_coefs = result.params[1:1 + n_basis]
    cb_vcov = result.cov_params()[1:1 + n_basis, 1:1 + n_basis]

    phi = result.scale
    deviance = result.deviance
    df_resid = result.df_resid

    if verbose:
        print(f"  Dispersion phi={phi:.3f}, deviance={deviance:.1f}, "
              f"df_resid={df_resid}")

    return {
        "result": result,
        "meta": meta,
        "cb_coefs": cb_coefs,
        "cb_vcov": cb_vcov,
        "phi": phi,
        "deviance": deviance,
        "df_resid": df_resid,
        "n_valid": n_valid,
        "exposure_col": exposure_col,
        "lag_max": lag_max,
        "exposure": exposure[valid_rows],
        "y_fit": y_fit,
        "X_fit": X_fit,
        "valid_mask": valid_rows,
        "sub_df": sub,
    }


def find_mmt(fit: dict, n_grid: int = 200, verbose: bool = False) -> float:
    """Find the minimum mortality temperature (MMT) via grid search."""
    meta = fit["meta"]
    exp_min, exp_max = meta.exposure_range
    grid = np.linspace(exp_min, exp_max, n_grid)

    # Use an arbitrary centering just for comparison (median)
    centering = np.median(fit["exposure"])
    pred = crosspred(fit["cb_coefs"], fit["cb_vcov"], meta, grid, centering)

    mmt_idx = np.argmin(pred["rr"])
    mmt = grid[mmt_idx]

    if verbose:
        print(f"  MMT = {mmt:.1f}°C (grid search in [{exp_min:.1f}, {exp_max:.1f}])")

    return mmt


# ══════════════════════════════════════════════════════════════════════
# 4. RERI — INTERACTION ON ADDITIVE SCALE
# ══════════════════════════════════════════════════════════════════════

def fit_joint_model(
    df: pd.DataFrame,
    temp_lag_max: int = 21,
    pm25_lag_max: int = 14,
    temp_exp_df: int = 4,
    temp_lag_df: int = 5,
    pm25_exp_df: int = 4,
    pm25_lag_df: int = 4,
    seasonal_df: int = 21,
    verbose: bool = False,
) -> dict:
    """Fit joint DLNM with both temperature and PM2.5 cross-bases."""
    sub = df.dropna(subset=["t_min", "pm2.5_epa"]).copy().reset_index(drop=True)
    n_total = len(sub)

    # Build cross-bases
    CB_temp, meta_temp = build_crossbasis(
        sub["t_min"].values, lag_max=temp_lag_max,
        exposure_df=temp_exp_df, lag_df=temp_lag_df,
    )
    CB_pm25, meta_pm25 = build_crossbasis(
        sub["pm2.5_epa"].values, lag_max=pm25_lag_max,
        exposure_df=pm25_exp_df, lag_df=pm25_lag_df,
    )

    # Valid rows
    valid = (~np.isnan(CB_temp).any(axis=1)) & (~np.isnan(CB_pm25).any(axis=1))
    n_valid = valid.sum()

    # Confounders
    X_conf = _confounder_matrix(sub, seasonal_df=seasonal_df)

    # Design matrix: intercept + CB_temp + CB_pm25 + confounders
    X = np.hstack([np.ones((n_total, 1)), CB_temp, CB_pm25, X_conf])
    y = sub["hosp"].values.astype(float)

    X_fit = X[valid]
    y_fit = y[valid]

    if verbose:
        print(f"\n  Joint model: N valid={n_valid}, "
              f"CB_temp={CB_temp.shape[1]}, CB_pm25={CB_pm25.shape[1]}, "
              f"total predictors={X_fit.shape[1]}")

    model = sm.GLM(y_fit, X_fit, family=sm.families.Poisson())
    result = model.fit(scale="X2")

    n_temp = meta_temp.n_basis
    n_pm25 = meta_pm25.n_basis

    # Coefficient slicing: [intercept, CB_temp..., CB_pm25..., confounders...]
    temp_coefs = result.params[1:1 + n_temp]
    temp_vcov = result.cov_params()[1:1 + n_temp, 1:1 + n_temp]

    pm25_start = 1 + n_temp
    pm25_coefs = result.params[pm25_start:pm25_start + n_pm25]
    pm25_vcov = result.cov_params()[pm25_start:pm25_start + n_pm25,
                                     pm25_start:pm25_start + n_pm25]

    if verbose:
        print(f"  Dispersion phi={result.scale:.3f}")

    return {
        "result": result,
        "meta_temp": meta_temp,
        "meta_pm25": meta_pm25,
        "temp_coefs": temp_coefs,
        "temp_vcov": temp_vcov,
        "pm25_coefs": pm25_coefs,
        "pm25_vcov": pm25_vcov,
        "n_valid": n_valid,
        "phi": result.scale,
        "sub_df": sub,
        "valid_mask": valid,
        "y_fit": y_fit,
    }


def compute_reri(
    joint: dict,
    cold_value: float,
    high_pm25: float,
    temp_center: float,
    pm25_center: float,
    verbose: bool = False,
) -> dict:
    """Compute RERI, AP, and S on the additive scale.

    Combinations:
      RR_11: cold + high PM2.5
      RR_10: cold + PM2.5 reference
      RR_01: temp reference + high PM2.5
      RR_00: reference + reference = 1
    """
    from crossbasis import _predict_basis_at_value

    def _cumul_log_rr(coefs, vcov, meta, value, center):
        """Log-RR and variance for cumulative effect at a value."""
        row_val = _predict_basis_at_value(value, meta)
        row_cen = _predict_basis_at_value(center, meta)
        diff = row_val - row_cen
        log_rr = diff @ coefs
        var = diff @ vcov @ diff
        return log_rr, var, diff

    # Temperature RR at cold value
    lr_temp, var_temp, d_temp = _cumul_log_rr(
        joint["temp_coefs"], joint["temp_vcov"],
        joint["meta_temp"], cold_value, temp_center,
    )
    # PM2.5 RR at high value
    lr_pm25, var_pm25, d_pm25 = _cumul_log_rr(
        joint["pm25_coefs"], joint["pm25_vcov"],
        joint["meta_pm25"], high_pm25, pm25_center,
    )

    RR_10 = np.exp(lr_temp)
    RR_01 = np.exp(lr_pm25)
    # Assuming independence in the additive model (no interaction term),
    # RR_11 = RR_10 * RR_01 on the multiplicative scale
    RR_11 = RR_10 * RR_01

    # RERI = RR_11 - RR_10 - RR_01 + 1
    RERI = RR_11 - RR_10 - RR_01 + 1

    # Delta method for RERI CI
    # Partial derivatives w.r.t. log(RR_temp) and log(RR_pm25)
    # RERI = exp(a+b) - exp(a) - exp(b) + 1  where a = lr_temp, b = lr_pm25
    d_reri_da = RR_11 - RR_10
    d_reri_db = RR_11 - RR_01

    # Variance: assumes independence between temp and pm25 coefs
    var_reri = (d_reri_da ** 2) * var_temp + (d_reri_db ** 2) * var_pm25
    se_reri = np.sqrt(var_reri)

    z = sp_stats.norm.ppf(0.975)
    RERI_lo = RERI - z * se_reri
    RERI_hi = RERI + z * se_reri

    # AP = RERI / RR_11
    AP = RERI / RR_11 if RR_11 != 0 else np.nan
    # S = (RR_11 - 1) / ((RR_10 - 1) + (RR_01 - 1))
    denom_s = (RR_10 - 1) + (RR_01 - 1)
    S = (RR_11 - 1) / denom_s if denom_s != 0 else np.nan

    results = {
        "RR_11": RR_11, "RR_10": RR_10, "RR_01": RR_01,
        "RERI": RERI, "RERI_lower": RERI_lo, "RERI_upper": RERI_hi,
        "AP": AP, "S": S,
        "cold_value": cold_value, "high_pm25": high_pm25,
        "temp_center": temp_center, "pm25_center": pm25_center,
    }

    if verbose:
        print(f"\n  RERI Analysis:")
        print(f"    Cold={cold_value:.1f}°C vs MMT={temp_center:.1f}°C: "
              f"RR_10={RR_10:.3f}")
        print(f"    PM2.5={high_pm25:.1f} vs median={pm25_center:.1f}: "
              f"RR_01={RR_01:.3f}")
        print(f"    RR_11={RR_11:.3f}")
        print(f"    RERI = {RERI:.3f} [{RERI_lo:.3f}, {RERI_hi:.3f}]")
        print(f"    AP = {AP:.3f}, S = {S:.3f}")
        sig = "significant (supra-additive)" if RERI_lo > 0 else "not significant"
        print(f"    Interaction: {sig}")

    return results


# ══════════════════════════════════════════════════════════════════════
# 5. FDR CORRECTION
# ══════════════════════════════════════════════════════════════════════

def fdr_correction(pvalues: dict[str, float], verbose: bool = False) -> pd.DataFrame:
    """Apply Benjamini-Hochberg FDR correction to all p-values."""
    names = list(pvalues.keys())
    pvals = np.array([pvalues[k] for k in names])

    reject, pvals_corrected, _, _ = multipletests(pvals, method="fdr_bh")

    fdr_df = pd.DataFrame({
        "test": names,
        "p_original": pvals,
        "p_corrected": pvals_corrected,
        "significant_005": reject,
    })

    if verbose:
        n_sig_orig = (pvals < 0.05).sum()
        n_sig_fdr = reject.sum()
        print(f"\n  FDR correction: {n_sig_orig} → {n_sig_fdr} significant "
              f"(of {len(pvals)} tests)")

    return fdr_df


# ══════════════════════════════════════════════════════════════════════
# 6. SENSITIVITY ANALYSES
# ══════════════════════════════════════════════════════════════════════

def sensitivity_analyses(
    df: pd.DataFrame,
    mmt: float,
    verbose: bool = False,
) -> pd.DataFrame:
    """Run sensitivity analyses varying lag, seasonal df, and year exclusion."""
    records = []
    p10_temp = np.nanpercentile(df["t_min"].dropna(), 10)

    configs = [
        # (label, lag_max, seasonal_df, year_exclude)
        ("Main (lag=21, 7df/yr)", 21, 21, None),
        ("Lag=14", 14, 21, None),
        ("Lag=28", 28, 21, None),
        ("Seasonal 6df/yr", 21, 18, None),
        ("Seasonal 8df/yr", 21, 24, None),
        ("Exclude 2024", 21, 21, 2024),
        ("Exclude 2022", 21, 21, 2022),
    ]

    for label, lag_max, sdf, excl_year in configs:
        if verbose:
            print(f"\n  Sensitivity: {label}")
        sub = df.copy()
        if excl_year is not None:
            sub = sub[sub["date"].dt.year != excl_year].reset_index(drop=True)
            # Recompute time_idx
            sub["time_idx"] = (sub["date"] - sub["date"].min()).dt.days

        try:
            fit = fit_dlnm(sub, "t_min", lag_max=lag_max,
                           seasonal_df=sdf, verbose=False)
            pred = crosspred(fit["cb_coefs"], fit["cb_vcov"], fit["meta"],
                             np.array([p10_temp]), mmt)
            records.append({
                "scenario": label,
                "RR": pred["rr"][0],
                "RR_lower": pred["rr_lower"][0],
                "RR_upper": pred["rr_upper"][0],
                "phi": fit["phi"],
                "N": fit["n_valid"],
            })
            if verbose:
                print(f"    RR(P10)={pred['rr'][0]:.3f} "
                      f"[{pred['rr_lower'][0]:.3f}, {pred['rr_upper'][0]:.3f}], "
                      f"phi={fit['phi']:.2f}, N={fit['n_valid']}")
        except Exception as e:
            if verbose:
                print(f"    FAILED: {e}")
            records.append({
                "scenario": label, "RR": np.nan, "RR_lower": np.nan,
                "RR_upper": np.nan, "phi": np.nan, "N": 0,
            })

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════
# 7. DIAGNOSTICS
# ══════════════════════════════════════════════════════════════════════

def model_diagnostics(fit: dict, verbose: bool = False) -> dict:
    """Compute residual diagnostics for a fitted DLNM."""
    result = fit["result"]
    resid_dev = result.resid_deviance
    resid_pear = result.resid_pearson

    # Dispersion
    phi = fit["phi"]

    # Durbin-Watson
    dw = durbin_watson(resid_dev)

    # Ljung-Box test (lags 1-7)
    try:
        lb = acorr_ljungbox(resid_dev, lags=7, return_df=True)
        lb_p_min = lb["lb_pvalue"].min()
    except Exception:
        lb = None
        lb_p_min = np.nan

    # ACF values
    from statsmodels.tsa.stattools import acf
    acf_vals = acf(resid_dev, nlags=14, fft=True)

    diag = {
        "phi": phi,
        "durbin_watson": dw,
        "ljung_box_min_p": lb_p_min,
        "ljung_box_df": lb,
        "acf_vals": acf_vals,
        "resid_dev": resid_dev,
        "resid_pear": resid_pear,
    }

    if verbose:
        print(f"\n  Diagnostics:")
        print(f"    Dispersion phi = {phi:.3f}")
        print(f"    Durbin-Watson  = {dw:.3f}")
        print(f"    Ljung-Box min p (lags 1-7) = {lb_p_min:.4f}")
        print(f"    ACF lag 1={acf_vals[1]:.3f}, lag 7={acf_vals[7]:.3f}")

    return diag


def plot_diagnostics(fit: dict, diag: dict, label: str = "temp"):
    """4-panel diagnostic figure."""
    resid = diag["resid_dev"]
    acf_v = diag["acf_vals"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # (a) Residuals vs time
    ax = axes[0, 0]
    ax.plot(resid, lw=0.4, color="#1f77b4", alpha=0.7)
    ax.axhline(0, ls="--", color="grey", lw=0.5)
    ax.set_title(f"(a) Deviance residuals vs time ({label})")
    ax.set_xlabel("Observation index")
    ax.set_ylabel("Deviance residual")

    # (b) ACF
    ax = axes[0, 1]
    lags_acf = np.arange(len(acf_v))
    ax.bar(lags_acf, acf_v, color="#1f77b4", alpha=0.7, width=0.6)
    n = len(resid)
    ci_bound = 1.96 / np.sqrt(n)
    ax.axhline(ci_bound, ls="--", color="red", lw=0.8)
    ax.axhline(-ci_bound, ls="--", color="red", lw=0.8)
    ax.axhline(0, color="grey", lw=0.5)
    ax.set_title("(b) ACF of deviance residuals")
    ax.set_xlabel("Lag")
    ax.set_ylabel("ACF")

    # (c) QQ plot
    ax = axes[1, 0]
    sp_stats.probplot(resid, plot=ax)
    ax.set_title("(c) QQ plot of deviance residuals")

    # (d) Residuals vs fitted
    ax = axes[1, 1]
    fitted = fit["result"].fittedvalues
    ax.scatter(fitted, resid, s=3, alpha=0.3, color="#1f77b4")
    ax.axhline(0, ls="--", color="grey", lw=0.5)
    ax.set_title("(d) Residuals vs fitted values")
    ax.set_xlabel("Fitted value")
    ax.set_ylabel("Deviance residual")

    fig.suptitle(f"Model diagnostics — {label}", y=1.01)
    fig.tight_layout()
    path = FIG_DIR / f"fig_diagnostics_{label}.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════
# 8. PLOTTING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def plot_overall_er(pred: dict, exposure_col: str, centering: float,
                    unit: str = "°C"):
    """Cumulative exposure-response curve."""
    fig, ax = plt.subplots(figsize=(8, 5))
    vals = pred["values"]
    ax.plot(vals, pred["rr"], color="#1f77b4", lw=2)
    ax.fill_between(vals, pred["rr_lower"], pred["rr_upper"],
                     alpha=0.2, color="#1f77b4")
    ax.axhline(1, ls="--", color="grey", lw=0.8)
    ax.axvline(centering, ls=":", color="red", lw=0.8,
               label=f"Reference ({centering:.1f}{unit})")
    ax.set_xlabel(f"{exposure_col} ({unit})")
    ax.set_ylabel("Cumulative RR")
    ax.set_title(f"Cumulative exposure-response: {exposure_col}")
    ax.legend(fontsize=9)
    fig.tight_layout()
    tag = "temp" if "t_min" in exposure_col else "pm25"
    path = FIG_DIR / f"fig_dlnm_{tag}_overall.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_lag_response(lag_pred: dict, exposure_value: float,
                      exposure_col: str, label: str, unit: str = "°C"):
    """Lag-response curve at a fixed exposure."""
    fig, ax = plt.subplots(figsize=(8, 5))
    lags = lag_pred["lags"]
    ax.plot(lags, lag_pred["rr"], "o-", ms=4, lw=1.5, color="#d62728")
    ax.fill_between(lags, lag_pred["rr_lower"], lag_pred["rr_upper"],
                     alpha=0.2, color="#d62728")
    ax.axhline(1, ls="--", color="grey", lw=0.8)
    ax.set_xlabel("Lag (days)")
    ax.set_ylabel("RR")
    ax.set_title(f"Lag-response at {label} ({exposure_value:.1f}{unit})")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    fig.tight_layout()
    tag = "temp" if "t_min" in exposure_col else "pm25"
    safe_label = label.lower().replace(" ", "_").replace("(", "").replace(")", "")
    path = FIG_DIR / f"fig_dlnm_{tag}_lag_{safe_label}.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_temp_lag_combined(lag_cold: dict, lag_hot: dict,
                           cold_val: float, hot_val: float):
    """Combined lag-response for cold and heat."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    for ax, pred, val, color, title in [
        (axes[0], lag_cold, cold_val, "#1f77b4", f"(a) Cold extreme (P10={cold_val:.1f}°C)"),
        (axes[1], lag_hot, hot_val, "#d62728", f"(b) Heat extreme (P90={hot_val:.1f}°C)"),
    ]:
        ax.plot(pred["lags"], pred["rr"], "o-", ms=4, lw=1.5, color=color)
        ax.fill_between(pred["lags"], pred["rr_lower"], pred["rr_upper"],
                         alpha=0.2, color=color)
        ax.axhline(1, ls="--", color="grey", lw=0.8)
        ax.set_xlabel("Lag (days)")
        ax.set_ylabel("RR")
        ax.set_title(title.replace("val", f"{val:.1f}"))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.tight_layout()
    path = FIG_DIR / "fig_dlnm_temp_lag.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_3d_surface(surface: dict, exposure_col: str, centering: float,
                    unit: str = "°C"):
    """3D surface or contour plot of RR(exposure, lag)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    vals = surface["values"]
    lags = surface["lags"]
    RR = surface["rr_matrix"]

    # Contour plot
    ax = axes[0]
    V, L = np.meshgrid(vals, lags, indexing="ij")
    levels = np.arange(0.8, 1.5, 0.02)
    cs = ax.contourf(V, L, RR, levels=levels, cmap="RdBu_r", extend="both")
    ax.contour(V, L, RR, levels=[1.0], colors="black", linewidths=1.5)
    plt.colorbar(cs, ax=ax, label="RR")
    ax.axvline(centering, ls=":", color="white", lw=1)
    ax.set_xlabel(f"{exposure_col} ({unit})")
    ax.set_ylabel("Lag (days)")
    ax.set_title("(a) Contour: RR(exposure, lag)")

    # 3D surface
    ax3 = fig.add_subplot(122, projection="3d")
    ax3.plot_surface(V, L, RR, cmap="RdBu_r", alpha=0.8, edgecolor="none")
    ax3.set_xlabel(f"{exposure_col} ({unit})")
    ax3.set_ylabel("Lag (days)")
    ax3.set_zlabel("RR")
    ax3.set_title("(b) 3D surface")
    # Remove the flat subplot
    axes[1].set_visible(False)

    fig.tight_layout()
    tag = "temp" if "t_min" in exposure_col else "pm25"
    path = FIG_DIR / f"fig_dlnm_{tag}_3d.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_reri(reri: dict):
    """Forest plot for RERI, AP, S."""
    fig, ax = plt.subplots(figsize=(8, 4))

    metrics = [
        ("RERI", reri["RERI"], reri["RERI_lower"], reri["RERI_upper"]),
        ("AP", reri["AP"], np.nan, np.nan),
        ("S", reri["S"], np.nan, np.nan),
    ]

    y_pos = [2, 1, 0]
    for i, (name, val, lo, hi) in enumerate(metrics):
        y = y_pos[i]
        ax.plot(val, y, "D", ms=8, color="#1f77b4")
        if not np.isnan(lo):
            ax.plot([lo, hi], [y, y], "-", lw=2, color="#1f77b4")
        ax.text(val + 0.01, y + 0.15, f"{val:.3f}", fontsize=9, ha="center")

    ax.axvline(0, ls="--", color="grey", lw=0.8, label="Null (RERI=0)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(["S", "AP", "RERI"])
    ax.set_xlabel("Estimate")
    ax.set_title("Interaction measures (additive scale)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    path = FIG_DIR / "fig_reri_interaction.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_sensitivity(sens_df: pd.DataFrame):
    """Forest plot comparing RR across sensitivity scenarios."""
    fig, ax = plt.subplots(figsize=(8, 5))

    n = len(sens_df)
    y_pos = np.arange(n)[::-1]
    colors = ["#d62728" if i == 0 else "#1f77b4" for i in range(n)]

    for i, (_, row) in enumerate(sens_df.iterrows()):
        y = y_pos[i]
        if not np.isnan(row["RR"]):
            ax.plot(row["RR"], y, "o", ms=7, color=colors[i])
            ax.plot([row["RR_lower"], row["RR_upper"]], [y, y],
                    "-", lw=2, color=colors[i])

    ax.axvline(1, ls="--", color="grey", lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sens_df["scenario"])
    ax.set_xlabel("Cumulative RR at P10 of Tmin")
    ax.set_title("Sensitivity analysis — Temperature DLNM")
    fig.tight_layout()
    path = FIG_DIR / "fig_sensitivity.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════
# 9. TABLES
# ══════════════════════════════════════════════════════════════════════

def save_rr_table(pred: dict, percentiles: dict[str, float],
                  centering: float, exposure_col: str) -> pd.DataFrame:
    """Save cumulative RR at key percentiles."""
    records = []
    for pct_label, pct_val in sorted(percentiles.items(), key=lambda x: x[1]):
        # Find closest value in pred grid
        idx = np.argmin(np.abs(pred["values"] - pct_val))
        records.append({
            "percentile": pct_label,
            "value": pct_val,
            "RR": pred["rr"][idx],
            "RR_lower": pred["rr_lower"][idx],
            "RR_upper": pred["rr_upper"][idx],
        })
    rr_df = pd.DataFrame(records)
    tag = "temp" if "t_min" in exposure_col else "pm25"
    rr_df.to_csv(TBL_DIR / f"table_dlnm_{tag}_rr.csv", index=False,
                 float_format="%.4f")
    return rr_df


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="DLNM analysis pipeline")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--exposure", default=None,
                        help="Run only one exposure (t_min or pm2.5_epa)")
    parser.add_argument("--lag-max", type=int, default=None,
                        help="Override lag max")
    parser.add_argument("--reri", action="store_true",
                        help="Run RERI interaction analysis")
    parser.add_argument("--stationarity", action="store_true",
                        help="Run stationarity + STL analysis")
    parser.add_argument("--fdr", action="store_true",
                        help="Run FDR correction")
    parser.add_argument("--sensitivity-all", action="store_true",
                        help="Run all sensitivity analyses")
    args = parser.parse_args()
    v = args.verbose

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TBL_DIR.mkdir(parents=True, exist_ok=True)

    report_lines = ["DLNM Analysis Report", "=" * 60, ""]

    # ── Load data ──
    if v:
        print("\n══ Loading data ══")
    df = load_data(verbose=v)

    all_pvalues = {}

    # ── Stationarity ──
    if args.stationarity or args.exposure is None:
        if v:
            print("\n══ Stationarity Analysis ══")
        stat = stationarity_analysis(df, verbose=v)
        all_pvalues["ADF_raw_hosp"] = stat["adf_raw"]["p"]
        all_pvalues["ADF_detrend_hosp"] = stat["adf_detrend"]["p"]

        adf_table = pd.DataFrame([
            {"series": "Raw hospitalisations",
             "ADF_stat": stat["adf_raw"]["stat"],
             "p_value": stat["adf_raw"]["p"],
             "stationary": "Yes" if stat["adf_raw"]["p"] < 0.05 else "No"},
            {"series": "STL residuals",
             "ADF_stat": stat["adf_detrend"]["stat"],
             "p_value": stat["adf_detrend"]["p"],
             "stationary": "Yes" if stat["adf_detrend"]["p"] < 0.05 else "No"},
        ])
        adf_table.to_csv(TBL_DIR / "table_adf_stationarity.csv",
                         index=False, float_format="%.4f")

        p = plot_stationarity(stat["stl_result"], stat["adf_raw"],
                              stat["adf_detrend"], stat["raw_corrs"],
                              stat["detrend_corrs"])
        report_lines.append(f"Stationarity figure: {p}")
        report_lines.append(f"ADF raw p={stat['adf_raw']['p']:.4f}, "
                            f"detrended p={stat['adf_detrend']['p']:.4f}")

    # ── Temperature DLNM (primary) ──
    run_temp = args.exposure is None or args.exposure == "t_min"
    fit_temp = None
    mmt = None
    if run_temp:
        if v:
            print("\n══ DLNM — Temperature ══")
        lag_max_temp = args.lag_max if args.lag_max else 21
        fit_temp = fit_dlnm(df, "t_min", lag_max=lag_max_temp, exposure_df=4,
                            lag_df=5, verbose=v)

        # Find MMT
        mmt = find_mmt(fit_temp, verbose=v)
        report_lines.append(f"\nTemperature MMT = {mmt:.1f}°C")

        # Percentiles
        t_min_vals = df["t_min"].dropna()
        pcts = {
            "P1": np.percentile(t_min_vals, 1),
            "P5": np.percentile(t_min_vals, 5),
            "P10": np.percentile(t_min_vals, 10),
            "P25": np.percentile(t_min_vals, 25),
            "P75": np.percentile(t_min_vals, 75),
            "P90": np.percentile(t_min_vals, 90),
            "P95": np.percentile(t_min_vals, 95),
            "P99": np.percentile(t_min_vals, 99),
        }

        # Cumulative exposure-response
        grid = np.linspace(t_min_vals.min(), t_min_vals.max(), 200)
        pred_temp = crosspred(fit_temp["cb_coefs"], fit_temp["cb_vcov"],
                              fit_temp["meta"], grid, mmt)
        p1 = plot_overall_er(pred_temp, "t_min", mmt, "°C")
        report_lines.append(f"Overall E-R figure: {p1}")

        # RR table
        rr_tab = save_rr_table(pred_temp, pcts, mmt, "t_min")
        if v:
            print("\n  Cumulative RR at key percentiles:")
            print(rr_tab.to_string(index=False, float_format="%.3f"))

        report_lines.append(f"RR at P10={pcts['P10']:.1f}°C: "
                            f"{rr_tab[rr_tab['percentile']=='P10']['RR'].values[0]:.3f}")

        # Lag-response at cold (P10) and heat (P90)
        lag_cold = crosspred_lag(fit_temp["cb_coefs"], fit_temp["cb_vcov"],
                                 fit_temp["meta"], pcts["P10"], mmt)
        lag_hot = crosspred_lag(fit_temp["cb_coefs"], fit_temp["cb_vcov"],
                                fit_temp["meta"], pcts["P90"], mmt)
        p2 = plot_temp_lag_combined(lag_cold, lag_hot, pcts["P10"], pcts["P90"])
        report_lines.append(f"Lag-response figure: {p2}")

        # 3D surface
        surface = crosspred_3d(fit_temp["cb_coefs"], fit_temp["cb_vcov"],
                                fit_temp["meta"], grid, mmt)
        p3 = plot_3d_surface(surface, "t_min", mmt, "°C")
        report_lines.append(f"3D surface figure: {p3}")

        # Diagnostics
        diag_temp = model_diagnostics(fit_temp, verbose=v)
        plot_diagnostics(fit_temp, diag_temp, "temp")

    # ── PM2.5 DLNM (secondary) ──
    run_pm25 = args.exposure is None or args.exposure == "pm2.5_epa"
    fit_pm25 = None
    if run_pm25:
        if v:
            print("\n══ DLNM — PM2.5 ══")
        lag_max_pm = args.lag_max if args.lag_max else 14
        fit_pm25 = fit_dlnm(df, "pm2.5_epa", lag_max=lag_max_pm,
                            exposure_df=4, lag_df=4, verbose=v)

        pm25_vals = df["pm2.5_epa"].dropna()
        pm25_median = np.median(pm25_vals)
        pm25_pcts = {
            "P25": np.percentile(pm25_vals, 25),
            "P50": np.percentile(pm25_vals, 50),
            "P75": np.percentile(pm25_vals, 75),
            "P90": np.percentile(pm25_vals, 90),
            "P95": np.percentile(pm25_vals, 95),
            "P99": np.percentile(pm25_vals, 99),
        }

        grid_pm = np.linspace(pm25_vals.min(), pm25_vals.max(), 200)
        pred_pm25 = crosspred(fit_pm25["cb_coefs"], fit_pm25["cb_vcov"],
                              fit_pm25["meta"], grid_pm, pm25_median)
        p4 = plot_overall_er(pred_pm25, "pm2.5_epa", pm25_median, "µg/m³")
        report_lines.append(f"\nPM2.5 E-R figure: {p4}")

        rr_pm_tab = save_rr_table(pred_pm25, pm25_pcts, pm25_median, "pm2.5_epa")
        if v:
            print("\n  Cumulative RR at key percentiles:")
            print(rr_pm_tab.to_string(index=False, float_format="%.3f"))

        # Lag-response at P90
        lag_pm_high = crosspred_lag(fit_pm25["cb_coefs"], fit_pm25["cb_vcov"],
                                     fit_pm25["meta"], pm25_pcts["P90"],
                                     pm25_median)
        fig_pm_lag, ax = plt.subplots(figsize=(8, 5))
        ax.plot(lag_pm_high["lags"], lag_pm_high["rr"], "o-", ms=4, lw=1.5,
                color="#d62728")
        ax.fill_between(lag_pm_high["lags"], lag_pm_high["rr_lower"],
                         lag_pm_high["rr_upper"], alpha=0.2, color="#d62728")
        ax.axhline(1, ls="--", color="grey", lw=0.8)
        ax.set_xlabel("Lag (days)")
        ax.set_ylabel("RR")
        ax.set_title(f"Lag-response at PM2.5 P90 ({pm25_pcts['P90']:.1f} µg/m³)")
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig_pm_lag.tight_layout()
        p5 = FIG_DIR / "fig_dlnm_pm25_lag.pdf"
        fig_pm_lag.savefig(p5)
        plt.close(fig_pm_lag)
        report_lines.append(f"PM2.5 lag figure: {p5}")

        # Diagnostics
        diag_pm25 = model_diagnostics(fit_pm25, verbose=v)
        plot_diagnostics(fit_pm25, diag_pm25, "pm25")

    # ── RERI ──
    if args.reri and run_temp and run_pm25:
        if v:
            print("\n══ RERI Interaction Analysis ══")
        joint = fit_joint_model(df, verbose=v)

        # Find MMT from joint model
        t_min_vals = df["t_min"].dropna()
        p10_temp = np.percentile(t_min_vals, 10)
        pm25_vals = df["pm2.5_epa"].dropna()
        p75_pm25 = np.percentile(pm25_vals, 75)
        pm25_med = np.median(pm25_vals)

        # Use MMT from primary model
        reri_results = compute_reri(
            joint, cold_value=p10_temp, high_pm25=p75_pm25,
            temp_center=mmt, pm25_center=pm25_med, verbose=v,
        )

        reri_df = pd.DataFrame([{
            "metric": "RERI",
            "estimate": reri_results["RERI"],
            "CI_lower": reri_results["RERI_lower"],
            "CI_upper": reri_results["RERI_upper"],
        }, {
            "metric": "AP",
            "estimate": reri_results["AP"],
            "CI_lower": np.nan, "CI_upper": np.nan,
        }, {
            "metric": "S",
            "estimate": reri_results["S"],
            "CI_lower": np.nan, "CI_upper": np.nan,
        }])
        reri_df.to_csv(TBL_DIR / "table_reri.csv", index=False,
                       float_format="%.4f")

        plot_reri(reri_results)
        report_lines.append(f"\nRERI = {reri_results['RERI']:.3f} "
                            f"[{reri_results['RERI_lower']:.3f}, "
                            f"{reri_results['RERI_upper']:.3f}]")

    # ── Sensitivity ──
    if args.sensitivity_all and fit_temp is not None and mmt is not None:
        if v:
            print("\n══ Sensitivity Analyses ══")
        sens_df = sensitivity_analyses(df, mmt, verbose=v)
        sens_df.to_csv(TBL_DIR / "table_sensitivity.csv", index=False,
                       float_format="%.4f")
        plot_sensitivity(sens_df)
        report_lines.append(f"\nSensitivity: {len(sens_df)} scenarios computed")

    # ── FDR ──
    if args.fdr and all_pvalues:
        if v:
            print("\n══ FDR Correction ══")
        fdr_df = fdr_correction(all_pvalues, verbose=v)
        fdr_df.to_csv(TBL_DIR / "table_fdr.csv", index=False,
                      float_format="%.6f")
        report_lines.append(f"FDR: {fdr_df['significant_005'].sum()} of "
                            f"{len(fdr_df)} tests remain significant")

    # ── Model summary table ──
    summary_rows = []
    if fit_temp is not None:
        summary_rows.append({
            "model": "Temperature",
            "N": fit_temp["n_valid"],
            "phi": fit_temp["phi"],
            "deviance": fit_temp["deviance"],
            "df_resid": fit_temp["df_resid"],
            "lag_max": fit_temp["lag_max"],
            "CB_columns": fit_temp["meta"].n_basis,
        })
    if fit_pm25 is not None:
        summary_rows.append({
            "model": "PM2.5",
            "N": fit_pm25["n_valid"],
            "phi": fit_pm25["phi"],
            "deviance": fit_pm25["deviance"],
            "df_resid": fit_pm25["df_resid"],
            "lag_max": fit_pm25["lag_max"],
            "CB_columns": fit_pm25["meta"].n_basis,
        })
    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(TBL_DIR / "table_dlnm_model_summary.csv",
                          index=False, float_format="%.3f")

    # ── Diagnostics table ──
    diag_rows = []
    if fit_temp is not None:
        dt = model_diagnostics(fit_temp)
        diag_rows.append({
            "model": "Temperature", "phi": dt["phi"],
            "durbin_watson": dt["durbin_watson"],
            "ljung_box_min_p": dt["ljung_box_min_p"],
            "acf_lag1": dt["acf_vals"][1],
            "acf_lag7": dt["acf_vals"][7],
        })
    if fit_pm25 is not None:
        dp = model_diagnostics(fit_pm25)
        diag_rows.append({
            "model": "PM2.5", "phi": dp["phi"],
            "durbin_watson": dp["durbin_watson"],
            "ljung_box_min_p": dp["ljung_box_min_p"],
            "acf_lag1": dp["acf_vals"][1],
            "acf_lag7": dp["acf_vals"][7],
        })
    if diag_rows:
        pd.DataFrame(diag_rows).to_csv(
            TBL_DIR / "table_diagnostics.csv", index=False, float_format="%.4f")

    # ── Write report ──
    report_lines.append(f"\n{'=' * 60}")
    report_lines.append("Analysis complete.")
    report_text = "\n".join(report_lines)
    REPORT_PATH.write_text(report_text)

    print(f"\n{'=' * 60}")
    print("  DLNM Analysis Complete")
    print(f"  Report: {REPORT_PATH}")
    print(f"  Figures: {FIG_DIR}")
    print(f"  Tables: {TBL_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
