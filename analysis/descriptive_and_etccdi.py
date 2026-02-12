#!/usr/bin/env python3
"""
Descriptive Statistics (Table 1) + ETCCDI Extreme Event Definitions
===================================================================

Generates:
  1. Table 1 (Lancet format): descriptive statistics for all study variables
  2. ETCCDI extreme temperature events: TX90p heatwaves, TN10p coldwaves
  3. Extended lag-correlation sensitivity (lags 0-28 days)
  4. Stationarity assessment (ADF test with documentation)

Uses:
  - INMET temperature data (1961-2024) for percentile baselines
  - base_dados_completa.csv (2022-2024) for study-period analyses
  - Health data for hospitalization counts
  - PurpleAir data for pressure

References:
  Zhang X, et al. Indices for monitoring changes in extremes based on
      daily temperature and precipitation data. WIREs Clim Change.
      2011;2(6):851-870. doi:10.1002/wcc.147
  WMO. Guidelines on the definition and monitoring of extreme weather
      and climate events. WMO-No. 1310. Geneva: WMO; 2023.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
DATA_INMET = ROOT / "data" / "raw" / "inmet" / "temp_cwb_1961-2024.csv"
DATA_BASE = ROOT / "data" / "processed" / "base_dados_completa.csv"
DATA_PA = ROOT / "data" / "raw" / "purpleair" / "90875 2021-01-01 2025-01-01 1440-Minute Average.csv"
DATA_HEALTH = ROOT / "data" / "raw" / "health" / "morb_mort_freq_2021-2024_cwb.csv"
OUT_DIR = ROOT / "analysis"
FIG_DIR = OUT_DIR / "figures"
TBL_DIR = OUT_DIR / "tables"

plt.rcParams.update({
    "font.family": "serif", "font.size": 10,
    "axes.labelsize": 11, "axes.titlesize": 12,
    "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "pdf.fonttype": 42,
})


# ══════════════════════════════════════════════════════════════════════════
# 1. TABLE 1 — DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════

def generate_table1(verbose: bool = False) -> pd.DataFrame:
    """Lancet-style Table 1: descriptive statistics for all variables."""
    base = pd.read_csv(DATA_BASE)
    base["date"] = pd.to_datetime(base["time_stamp"]).dt.normalize()

    # Merge health
    health = pd.read_csv(DATA_HEALTH)
    health["date"] = pd.to_datetime(health["DATE"]).dt.normalize()
    df = base.merge(health[["date", "Hospitalizations", "Obits"]], on="date", how="left")

    # Merge pressure
    pa = pd.read_csv(DATA_PA)
    pa["date"] = pd.to_datetime(pa["time_stamp"], utc=True).dt.tz_localize(None).dt.normalize()
    pa_p = pa[["date", "pressure"]].drop_duplicates("date", keep="first")
    df = df.merge(pa_p, on="date", how="left")

    variables = [
        ("t_max", "Maximum temperature (°C)"),
        ("t_med", "Mean temperature (°C)"),
        ("t_min", "Minimum temperature (°C)"),
        ("pm2.5_epa", "PM₂.₅ EPA-corrected (µg/m³)"),
        ("pm2.5_med", "PM₂.₅ raw sensor (µg/m³)"),
        ("umidade_relativa", "Relative humidity (%)"),
        ("pressure", "Atmospheric pressure (hPa)"),
        ("Hospitalizations", "Daily hospitalisations (n)"),
        ("Obits", "Daily deaths (n)"),
    ]

    records = []
    for col, label in variables:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        records.append({
            "Variable": label,
            "N": int(s.count()),
            "Mean": s.mean(),
            "SD": s.std(),
            "Median": s.median(),
            "Q25": s.quantile(0.25),
            "Q75": s.quantile(0.75),
            "Min": s.min(),
            "Max": s.max(),
            "Missing (%)": f"{100 * df[col].isna().mean():.1f}",
        })

    tab = pd.DataFrame(records)

    # Add study period metadata
    n_days = len(df)
    date_range = f"{df['date'].min().date()} to {df['date'].max().date()}"
    total_hosp = df["Hospitalizations"].sum()
    total_deaths = df["Obits"].sum()

    if verbose:
        print(f"\n── TABLE 1: Descriptive Statistics ──")
        print(f"Study period: {date_range}")
        print(f"Total days: {n_days}")
        print(f"Total hospitalisations: {total_hosp:,.0f}")
        print(f"Total deaths: {total_deaths:,.0f}")
        print(tab.to_string(index=False, float_format="%.2f"))

    return tab, {
        "n_days": n_days, "date_range": date_range,
        "total_hosp": total_hosp, "total_deaths": total_deaths,
    }


# ══════════════════════════════════════════════════════════════════════════
# 2. ETCCDI EXTREME EVENT DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════

def compute_etccdi(verbose: bool = False) -> dict:
    """Compute ETCCDI-based extreme temperature events.

    TX90p: days where Tmax > 90th percentile of that calendar month
    TN10p: days where Tmin < 10th percentile of that calendar month
    Baseline: 1961-2020 (WMO standard 30-year + extension)
    Heatwave: ≥3 consecutive TX90p days
    Coldwave: ≥3 consecutive TN10p days
    """
    # Load full INMET series
    inmet = pd.read_csv(DATA_INMET)
    inmet["date"] = pd.to_datetime(inmet["date"])
    inmet["month"] = inmet["date"].dt.month

    # Baseline period for percentile calculation (1961-2020)
    baseline = inmet[(inmet["date"].dt.year >= 1961) &
                     (inmet["date"].dt.year <= 2020)].copy()

    # Monthly percentiles
    percentiles = {}
    for month in range(1, 13):
        m_data = baseline[baseline["month"] == month]
        percentiles[month] = {
            "tx90": m_data["t_max"].quantile(0.90),
            "tn10": m_data["t_min"].quantile(0.10),
            "tx_median": m_data["t_max"].median(),
            "tn_median": m_data["t_min"].median(),
        }

    if verbose:
        print("\n── ETCCDI Monthly Percentiles (baseline 1961-2020) ──")
        print(f"  {'Month':>5s}  {'TX90 (°C)':>10s}  {'TN10 (°C)':>10s}")
        for m in range(1, 13):
            print(f"  {m:>5d}  {percentiles[m]['tx90']:>10.1f}  {percentiles[m]['tn10']:>10.1f}")

    # Apply to study period (2022-2024)
    study = inmet[(inmet["date"].dt.year >= 2022) &
                  (inmet["date"].dt.year <= 2024)].copy()
    study = study.dropna(subset=["t_max", "t_min"])

    study["tx90_threshold"] = study["month"].map(lambda m: percentiles[m]["tx90"])
    study["tn10_threshold"] = study["month"].map(lambda m: percentiles[m]["tn10"])
    study["is_extreme_hot"] = study["t_max"] > study["tx90_threshold"]
    study["is_extreme_cold"] = study["t_min"] < study["tn10_threshold"]

    # Identify waves (≥3 consecutive days)
    def find_waves(series: pd.Series, min_duration: int = 3) -> list[dict]:
        waves = []
        in_wave = False
        start = None
        count = 0
        for idx, val in series.items():
            if val:
                if not in_wave:
                    in_wave = True
                    start = idx
                    count = 1
                else:
                    count += 1
            else:
                if in_wave and count >= min_duration:
                    waves.append({"start": start, "end": idx - 1,
                                  "duration": count})
                in_wave = False
                count = 0
        if in_wave and count >= min_duration:
            waves.append({"start": start, "end": series.index[-1],
                          "duration": count})
        return waves

    # Reset index for consecutive detection
    study = study.sort_values("date").reset_index(drop=True)
    heatwaves = find_waves(study["is_extreme_hot"])
    coldwaves = find_waves(study["is_extreme_cold"])

    # Get dates for waves
    hw_details = []
    for w in heatwaves:
        dates = study.loc[w["start"]:w["end"]]
        hw_details.append({
            "start_date": dates["date"].iloc[0],
            "end_date": dates["date"].iloc[-1],
            "duration": w["duration"],
            "mean_tmax": dates["t_max"].mean(),
            "max_tmax": dates["t_max"].max(),
        })

    cw_details = []
    for w in coldwaves:
        dates = study.loc[w["start"]:w["end"]]
        cw_details.append({
            "start_date": dates["date"].iloc[0],
            "end_date": dates["date"].iloc[-1],
            "duration": w["duration"],
            "mean_tmin": dates["t_min"].mean(),
            "min_tmin": dates["t_min"].min(),
        })

    n_hot_days = study["is_extreme_hot"].sum()
    n_cold_days = study["is_extreme_cold"].sum()

    results = {
        "percentiles": percentiles,
        "n_study_days": len(study),
        "n_extreme_hot": int(n_hot_days),
        "pct_extreme_hot": 100 * n_hot_days / len(study),
        "n_extreme_cold": int(n_cold_days),
        "pct_extreme_cold": 100 * n_cold_days / len(study),
        "n_heatwaves": len(hw_details),
        "n_coldwaves": len(cw_details),
        "heatwaves": hw_details,
        "coldwaves": cw_details,
        "study_data": study,
    }

    if verbose:
        print(f"\n── ETCCDI Results (2022-2024) ──")
        print(f"  Study days: {len(study)}")
        print(f"  Extreme hot days (TX90p): {n_hot_days} ({results['pct_extreme_hot']:.1f}%)")
        print(f"  Extreme cold days (TN10p): {n_cold_days} ({results['pct_extreme_cold']:.1f}%)")
        print(f"  Heatwaves (≥3 days): {len(hw_details)}")
        for i, hw in enumerate(hw_details):
            print(f"    HW{i+1}: {hw['start_date'].date()} → {hw['end_date'].date()} "
                  f"({hw['duration']} days, max Tmax={hw['max_tmax']:.1f}°C)")
        print(f"  Coldwaves (≥3 days): {len(cw_details)}")
        for i, cw in enumerate(cw_details):
            print(f"    CW{i+1}: {cw['start_date'].date()} → {cw['end_date'].date()} "
                  f"({cw['duration']} days, min Tmin={cw['min_tmin']:.1f}°C)")

    return results


def plot_etccdi(etccdi: dict):
    """Plot extreme events timeline."""
    study = etccdi["study_data"]

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    # Tmax with TX90p
    ax = axes[0]
    ax.plot(study["date"], study["t_max"], color="#d62728", lw=0.6, alpha=0.7)
    ax.plot(study["date"], study["tx90_threshold"], color="orange",
            ls="--", lw=0.8, label="TX90p threshold")
    hot_mask = study["is_extreme_hot"]
    ax.scatter(study.loc[hot_mask, "date"], study.loc[hot_mask, "t_max"],
               s=8, color="#d62728", zorder=5, label=f"Extreme hot (n={hot_mask.sum()})")
    ax.set_ylabel("$T_{max}$ (°C)")
    ax.set_title("(a) Maximum temperature and TX90p extreme days")
    ax.legend(loc="upper right", fontsize=8)

    # Tmin with TN10p
    ax = axes[1]
    ax.plot(study["date"], study["t_min"], color="#1f77b4", lw=0.6, alpha=0.7)
    ax.plot(study["date"], study["tn10_threshold"], color="cyan",
            ls="--", lw=0.8, label="TN10p threshold")
    cold_mask = study["is_extreme_cold"]
    ax.scatter(study.loc[cold_mask, "date"], study.loc[cold_mask, "t_min"],
               s=8, color="#1f77b4", zorder=5, label=f"Extreme cold (n={cold_mask.sum()})")
    ax.set_ylabel("$T_{min}$ (°C)")
    ax.set_xlabel("Date")
    ax.set_title("(b) Minimum temperature and TN10p extreme days")
    ax.legend(loc="upper right", fontsize=8)

    # Mark waves
    for hw in etccdi["heatwaves"]:
        axes[0].axvspan(hw["start_date"], hw["end_date"],
                        alpha=0.15, color="red", zorder=0)
    for cw in etccdi["coldwaves"]:
        axes[1].axvspan(cw["start_date"], cw["end_date"],
                        alpha=0.15, color="blue", zorder=0)

    fig.tight_layout()
    path = FIG_DIR / "fig_etccdi_extremes.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════════
# 3. EXTENDED LAG CORRELATIONS (SENSITIVITY D7)
# ══════════════════════════════════════════════════════════════════════════

def extended_lag_analysis(max_lag: int = 28, verbose: bool = False) -> pd.DataFrame:
    """Compute lag correlations for PM2.5 and Tmin vs hospitalisations up to 28 days."""
    base = pd.read_csv(DATA_BASE)
    base["date"] = pd.to_datetime(base["time_stamp"]).dt.normalize()

    health = pd.read_csv(DATA_HEALTH)
    health["date"] = pd.to_datetime(health["DATE"]).dt.normalize()
    df = base.merge(health[["date", "Hospitalizations"]], on="date", how="left")

    records = []
    for var, label in [("pm2.5_epa", "PM2.5_EPA"), ("t_min", "Tmin")]:
        sub = df[[var, "Hospitalizations"]].dropna()
        for lag in range(max_lag + 1):
            hosp_shifted = sub["Hospitalizations"].shift(-lag)
            valid = sub[var].notna() & hosp_shifted.notna()
            if valid.sum() < 30:
                continue
            r, p = stats.pearsonr(sub.loc[valid, var], hosp_shifted[valid])
            rho, sp = stats.spearmanr(sub.loc[valid, var], hosp_shifted[valid])
            records.append({
                "variable": label, "lag_days": lag,
                "pearson_r": r, "pearson_p": p,
                "spearman_rho": rho, "spearman_p": sp,
                "n": int(valid.sum()),
            })

    lag_df = pd.DataFrame(records)

    if verbose:
        print(f"\n── Extended Lag Correlations (0-{max_lag} days) ──")
        for var in ["PM2.5_EPA", "Tmin"]:
            sub = lag_df[lag_df["variable"] == var]
            peak = sub.loc[sub["pearson_r"].abs().idxmax()]
            print(f"  {var}: peak |r| at lag {int(peak['lag_days'])} "
                  f"(r={peak['pearson_r']:.3f}, p={peak['pearson_p']:.4f})")

    return lag_df


def plot_extended_lags(lag_df: pd.DataFrame):
    """Plot extended lag correlations."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for var, color, marker in [("PM2.5_EPA", "#d62728", "o"),
                                ("Tmin", "#1f77b4", "s")]:
        sub = lag_df[lag_df["variable"] == var]
        axes[0].plot(sub["lag_days"], sub["pearson_r"], f"{marker}-",
                     color=color, lw=1, ms=3, alpha=0.8, label=var)
        axes[1].plot(sub["lag_days"], sub["spearman_rho"], f"{marker}-",
                     color=color, lw=1, ms=3, alpha=0.8, label=var)

    for ax, title, ylabel in [
        (axes[0], "(a) Pearson r", "Pearson r"),
        (axes[1], "(b) Spearman ρ", "Spearman ρ"),
    ]:
        ax.axhline(0, color="grey", ls="--", lw=0.5)
        # Mark original 14-day boundary
        ax.axvline(14, color="orange", ls=":", lw=0.8,
                   label="Original max lag (14d)")
        ax.set_xlabel("Lag (days)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(loc="best", fontsize=8)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.suptitle("Extended Lag Sensitivity: PM$_{2.5}$ and $T_{min}$ vs Hospitalisations",
                 y=1.02)
    fig.tight_layout()
    path = FIG_DIR / "fig_extended_lag_sensitivity.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════════
# 4. STATIONARITY ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════

def stationarity_tests(verbose: bool = False) -> pd.DataFrame:
    """ADF tests for all key variables."""
    from statsmodels.tsa.stattools import adfuller

    base = pd.read_csv(DATA_BASE)
    base["date"] = pd.to_datetime(base["time_stamp"]).dt.normalize()
    health = pd.read_csv(DATA_HEALTH)
    health["date"] = pd.to_datetime(health["DATE"]).dt.normalize()
    df = base.merge(health[["date", "Hospitalizations"]], on="date", how="left")

    records = []
    for col, label in [
        ("t_max", "Tmax"), ("t_min", "Tmin"),
        ("pm2.5_epa", "PM2.5 (EPA)"),
        ("Hospitalizations", "Hospitalisations"),
    ]:
        s = df[col].dropna()
        if len(s) < 30:
            continue
        result = adfuller(s, maxlag=14, autolag="AIC")
        records.append({
            "Variable": label,
            "ADF_statistic": result[0],
            "p_value": result[1],
            "n_lags": result[2],
            "n_obs": result[3],
            "stationary": "Yes" if result[1] < 0.05 else "No",
        })

    tab = pd.DataFrame(records)
    if verbose:
        print("\n── Stationarity Tests (ADF) ──")
        print(tab.to_string(index=False, float_format="%.4f"))

    return tab


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Descriptive statistics, ETCCDI, and lag sensitivity")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    v = args.verbose

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TBL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Table 1
    if v:
        print("\n══ TABLE 1: Descriptive Statistics ══")
    tab1, meta = generate_table1(verbose=v)
    tab1.to_csv(TBL_DIR / "table1_descriptive.csv", index=False, float_format="%.2f")

    # 2. ETCCDI
    if v:
        print("\n══ ETCCDI Extreme Events ══")
    etccdi = compute_etccdi(verbose=v)

    # Save percentiles table
    perc_records = []
    for m in range(1, 13):
        p = etccdi["percentiles"][m]
        perc_records.append({
            "Month": m, "TX90 (°C)": p["tx90"], "TN10 (°C)": p["tn10"],
            "Tmax_median": p["tx_median"], "Tmin_median": p["tn_median"],
        })
    pd.DataFrame(perc_records).to_csv(
        TBL_DIR / "table_etccdi_percentiles.csv", index=False, float_format="%.1f")

    # Save events
    if etccdi["heatwaves"]:
        hw_df = pd.DataFrame(etccdi["heatwaves"])
        hw_df.to_csv(TBL_DIR / "table_heatwaves.csv", index=False, float_format="%.1f")
    if etccdi["coldwaves"]:
        cw_df = pd.DataFrame(etccdi["coldwaves"])
        cw_df.to_csv(TBL_DIR / "table_coldwaves.csv", index=False, float_format="%.1f")

    p1 = plot_etccdi(etccdi)
    if v:
        print(f"  → {p1}")

    # 3. Extended lag correlations
    if v:
        print("\n══ Extended Lag Sensitivity (0-28 days) ══")
    lag_df = extended_lag_analysis(max_lag=28, verbose=v)
    lag_df.to_csv(TBL_DIR / "table_extended_lag_correlations.csv",
                  index=False, float_format="%.4f")
    p2 = plot_extended_lags(lag_df)
    if v:
        print(f"  → {p2}")

    # 4. Stationarity
    if v:
        print("\n══ Stationarity Tests ══")
    try:
        adf = stationarity_tests(verbose=v)
        adf.to_csv(TBL_DIR / "table_stationarity_adf.csv",
                    index=False, float_format="%.4f")
    except ImportError:
        if v:
            print("  statsmodels not available, skipping ADF tests")

    # Summary
    print(f"\n{'='*60}")
    print(f"  Analysis complete.")
    print(f"  Table 1: {TBL_DIR / 'table1_descriptive.csv'}")
    print(f"  ETCCDI:  {etccdi['n_extreme_hot']} hot days, "
          f"{etccdi['n_extreme_cold']} cold days")
    print(f"           {etccdi['n_heatwaves']} heatwaves, "
          f"{etccdi['n_coldwaves']} coldwaves")
    print(f"  Lags:    0-28 days ({TBL_DIR / 'table_extended_lag_correlations.csv'})")
    print(f"  Figures: {FIG_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
