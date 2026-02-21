#!/usr/bin/env python3
"""
Clustering Analysis for CWB Temperature–Pollution–Health Study
==============================================================

Reproduces and validates the K-means clustering described in the manuscript
("Structural Adaptation Gaps Amplify the Synergistic Mortality Risk of
Cold Spells and Particulate Matter in a Subtropical Metropolis").

Resolves two manuscript divergences:
  D6 — No clustering code existed in the repository.
  D7 — Manuscript table shows temperatures in Fahrenheit mislabelled as Celsius.

Usage:
  python analysis/clustering/cluster_analysis.py [options]

Options:
  --k INT           Force cluster count (default: auto-select via metrics)
  --features {6,4}  6 = all features; 4 = drop pressure & humidity (default: 6)
  --imputation {dropna,mean,median,knn}  Missing-data strategy (default: dropna)
  --gap-statistic   Compute gap statistic (slow, ~30 s)
  --verbose         Print progress to stdout
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]  # cwb-temp-pollution-health/
DATA_PROC = ROOT / "data" / "processed" / "base_dados_completa.csv"
DATA_PA = ROOT / "data" / "raw" / "purpleair" / "90875 2021-01-01 2025-01-01 1440-Minute Average.csv"
DATA_HEALTH = ROOT / "data" / "raw" / "health" / "morb_mort_freq_2021-2024_cwb.csv"
OUT_DIR = Path(__file__).resolve().parent
FIG_DIR = OUT_DIR / "figures"
TBL_DIR = OUT_DIR / "tables"

# ── Manuscript reference values (Table X, reported as "°C") ──────────────────
# These are the values printed in the manuscript. We compare computed clusters
# against them and flag the Fahrenheit-vs-Celsius discrepancy.
MANUSCRIPT_CLUSTERS = {
    "Polluted Heat": {"Tmax": 78.2, "Tmed": 71.6, "Tmin": 65.1, "PM2.5": 14.3},
    "Clean Heat":    {"Tmax": 76.5, "Tmed": 69.8, "Tmin": 63.4, "PM2.5": 4.8},
    "Moderate Transition": {"Tmax": 68.9, "Tmed": 61.2, "Tmin": 54.7, "PM2.5": 8.7},
    "Clean Cold":    {"Tmax": 62.3, "Tmed": 55.1, "Tmin": 49.2, "PM2.5": 3.2},
}

# ── Plot style ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "pdf.fonttype": 42,  # TrueType for journal compliance
    "ps.fonttype": 42,
})
PALETTE = sns.color_palette("Set2", 8)

# ══════════════════════════════════════════════════════════════════════════════
# 1. DATA LOADING & MERGING
# ══════════════════════════════════════════════════════════════════════════════

def load_base(verbose: bool = False) -> pd.DataFrame:
    """Load the main processed dataset."""
    df = pd.read_csv(DATA_PROC)
    df["date"] = pd.to_datetime(df["time_stamp"]).dt.normalize()
    if verbose:
        print(f"[load] base_dados_completa: {len(df)} rows, cols={list(df.columns)}")
    return df


def load_pressure(verbose: bool = False) -> pd.DataFrame:
    """Load PurpleAir pressure (and flag temperature unit)."""
    df = pd.read_csv(DATA_PA)
    df["date"] = pd.to_datetime(df["time_stamp"], utc=True).dt.tz_localize(None).dt.normalize()
    # Keep only pressure; temperature here is in °F
    out = df[["date", "pressure"]].copy()
    out = out.dropna(subset=["pressure"])
    out = out.drop_duplicates(subset=["date"], keep="first")
    if verbose:
        print(f"[load] PurpleAir pressure: {len(out)} days")
        # Show that temperature column is Fahrenheit
        if "temperature" in df.columns:
            tmean = df["temperature"].mean()
            print(f"       PurpleAir temp mean = {tmean:.1f} (Fahrenheit)")
    return out


def load_health(verbose: bool = False) -> pd.DataFrame:
    """Load health data (hospitalizations, deaths)."""
    df = pd.read_csv(DATA_HEALTH)
    df["date"] = pd.to_datetime(df["DATE"]).dt.normalize()
    out = df[["date", "Hospitalizations", "Obits"]].copy()
    if verbose:
        print(f"[load] Health data: {len(out)} rows, date range "
              f"{out['date'].min().date()} → {out['date'].max().date()}")
    return out


def merge_datasets(verbose: bool = False) -> pd.DataFrame:
    """Merge base + pressure + health by date."""
    base = load_base(verbose)
    pressure = load_pressure(verbose)
    health = load_health(verbose)

    df = base.merge(pressure, on="date", how="left")
    df = df.merge(health, on="date", how="left")

    if verbose:
        print(f"[merge] Combined: {len(df)} rows")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 2. DATA AUDIT & MISSING-DATA HANDLING
# ══════════════════════════════════════════════════════════════════════════════

FEATURES_6 = ["t_max", "t_med", "t_min", "pm2.5_epa", "umidade_relativa", "pressure"]
FEATURES_4 = ["t_max", "t_med", "t_min", "pm2.5_epa"]


def audit_data(df: pd.DataFrame, features: list[str]) -> str:
    """Generate a plain-text data-quality audit."""
    lines = ["DATA AUDIT REPORT", "=" * 60, ""]
    lines.append(f"Total rows: {len(df)}")
    lines.append(f"Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    lines.append(f"Features for clustering: {features}")
    lines.append("")
    lines.append("Missing values per feature:")
    for col in features:
        if col in df.columns:
            n_miss = df[col].isna().sum()
            pct = 100 * n_miss / len(df)
            lines.append(f"  {col:25s}: {n_miss:5d} / {len(df)} ({pct:.1f}%)")
        else:
            lines.append(f"  {col:25s}: COLUMN NOT FOUND")
    n_complete = df[features].dropna().shape[0]
    lines.append(f"\nComplete cases (all {len(features)} features): {n_complete} / {len(df)} "
                 f"({100*n_complete/len(df):.1f}%)")

    # Per-feature basic stats
    lines.append("\nDescriptive statistics (raw, before scaling):")
    desc = df[features].describe().T
    for col in features:
        if col in desc.index:
            r = desc.loc[col]
            lines.append(f"  {col:25s}: mean={r['mean']:.2f}  sd={r['std']:.2f}  "
                         f"min={r['min']:.2f}  max={r['max']:.2f}")
    lines.append("")
    return "\n".join(lines)


def handle_missing(df: pd.DataFrame, features: list[str],
                   method: str = "dropna", verbose: bool = False) -> pd.DataFrame:
    """Handle missing values in the feature columns."""
    n_before = len(df)
    if method == "dropna":
        df = df.dropna(subset=features).copy()
    elif method in ("mean", "median"):
        for col in features:
            if col in df.columns:
                fill = df[col].mean() if method == "mean" else df[col].median()
                df[col] = df[col].fillna(fill)
    elif method == "knn":
        from sklearn.impute import KNNImputer
        imp = KNNImputer(n_neighbors=5)
        df[features] = imp.fit_transform(df[features])
    else:
        raise ValueError(f"Unknown imputation method: {method}")

    n_after = len(df)
    if verbose:
        print(f"[missing] {method}: {n_before} → {n_after} rows "
              f"(dropped {n_before - n_after})")
    return df.reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
# 3. STANDARDISATION
# ══════════════════════════════════════════════════════════════════════════════

def scale_features(df: pd.DataFrame, features: list[str]):
    """StandardScaler on selected features. Returns (X_scaled, scaler)."""
    scaler = StandardScaler()
    X = scaler.fit_transform(df[features].values)
    return X, scaler


# ══════════════════════════════════════════════════════════════════════════════
# 4. K SELECTION
# ══════════════════════════════════════════════════════════════════════════════

def k_selection_metrics(X: np.ndarray, k_range: range,
                        verbose: bool = False) -> pd.DataFrame:
    """Compute inertia, silhouette, CH, DB for each K."""
    records = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        labels = km.fit_predict(X)
        row = {"K": k, "inertia": km.inertia_}
        if k >= 2:
            row["silhouette"] = silhouette_score(X, labels)
            row["calinski_harabasz"] = calinski_harabasz_score(X, labels)
            row["davies_bouldin"] = davies_bouldin_score(X, labels)
        else:
            row["silhouette"] = np.nan
            row["calinski_harabasz"] = np.nan
            row["davies_bouldin"] = np.nan
        records.append(row)
        if verbose:
            sil = f"{row['silhouette']:.3f}" if k >= 2 else "n/a"
            print(f"  K={k:2d}  inertia={row['inertia']:.0f}  silhouette={sil}")
    return pd.DataFrame(records)


def gap_statistic(X: np.ndarray, k_range: range, n_refs: int = 20,
                  verbose: bool = False) -> pd.DataFrame:
    """Gap statistic (Tibshirani et al. 2001)."""
    if verbose:
        print("[gap] Computing gap statistic …")
    rng = np.random.default_rng(42)
    mins = X.min(axis=0)
    maxs = X.max(axis=0)

    records = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(X)
        log_wk = np.log(km.inertia_)

        ref_log_wks = []
        for _ in range(n_refs):
            X_ref = rng.uniform(mins, maxs, size=X.shape)
            km_ref = KMeans(n_clusters=k, n_init=10, random_state=42)
            km_ref.fit(X_ref)
            ref_log_wks.append(np.log(km_ref.inertia_))

        gap = np.mean(ref_log_wks) - log_wk
        sk = np.std(ref_log_wks) * np.sqrt(1 + 1 / n_refs)
        records.append({"K": k, "gap": gap, "sk": sk})

    df = pd.DataFrame(records)
    # Optimal: smallest K where gap(k) >= gap(k+1) - s(k+1)
    for i in range(len(df) - 1):
        if df.loc[i, "gap"] >= df.loc[i + 1, "gap"] - df.loc[i + 1, "sk"]:
            if verbose:
                print(f"[gap] Optimal K = {df.loc[i, 'K']} (gap criterion)")
            break
    return df


def find_optimal_k(metrics: pd.DataFrame) -> int:
    """Heuristic: pick K that maximises silhouette among K=2..10."""
    valid = metrics.dropna(subset=["silhouette"])
    best = valid.loc[valid["silhouette"].idxmax()]
    return int(best["K"])


# ══════════════════════════════════════════════════════════════════════════════
# 5. METHOD COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

def compare_methods(X: np.ndarray, k: int,
                    verbose: bool = False) -> pd.DataFrame:
    """Compare K-means, Ward, DBSCAN on the same data."""
    results = []

    # K-means
    km = KMeans(n_clusters=k, n_init=20, random_state=42)
    lbl_km = km.fit_predict(X)
    results.append({
        "method": "K-means",
        "n_clusters": k,
        "silhouette": silhouette_score(X, lbl_km),
        "calinski_harabasz": calinski_harabasz_score(X, lbl_km),
        "davies_bouldin": davies_bouldin_score(X, lbl_km),
    })

    # Ward hierarchical
    ward = AgglomerativeClustering(n_clusters=k, linkage="ward")
    lbl_ward = ward.fit_predict(X)
    results.append({
        "method": "Ward",
        "n_clusters": k,
        "silhouette": silhouette_score(X, lbl_ward),
        "calinski_harabasz": calinski_harabasz_score(X, lbl_ward),
        "davies_bouldin": davies_bouldin_score(X, lbl_ward),
    })

    # DBSCAN — auto eps via k-distance
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=2 * X.shape[1])
    nn.fit(X)
    distances, _ = nn.kneighbors(X)
    eps = np.percentile(distances[:, -1], 90)
    db = DBSCAN(eps=eps, min_samples=2 * X.shape[1])
    lbl_db = db.fit_predict(X)
    n_db = len(set(lbl_db) - {-1})
    if n_db >= 2:
        mask = lbl_db >= 0
        results.append({
            "method": "DBSCAN",
            "n_clusters": n_db,
            "silhouette": silhouette_score(X[mask], lbl_db[mask]),
            "calinski_harabasz": calinski_harabasz_score(X[mask], lbl_db[mask]),
            "davies_bouldin": davies_bouldin_score(X[mask], lbl_db[mask]),
        })
    else:
        results.append({
            "method": "DBSCAN",
            "n_clusters": n_db,
            "silhouette": np.nan,
            "calinski_harabasz": np.nan,
            "davies_bouldin": np.nan,
        })

    df = pd.DataFrame(results)
    if verbose:
        print("[methods]")
        print(df.to_string(index=False))
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 6. CLUSTERING + PROFILE LABELLING
# ══════════════════════════════════════════════════════════════════════════════

def run_kmeans(X: np.ndarray, k: int) -> tuple[np.ndarray, KMeans]:
    """Fit K-means and return (labels, model)."""
    km = KMeans(n_clusters=k, n_init=20, random_state=42)
    labels = km.fit_predict(X)
    return labels, km


def cluster_profiles(df: pd.DataFrame, labels: np.ndarray,
                     features: list[str]) -> pd.DataFrame:
    """Descriptive statistics per cluster (on original scale)."""
    df = df.copy()
    df["cluster"] = labels
    records = []
    for cl in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cl]
        row = {"cluster": cl, "n": len(sub)}
        for feat in features:
            vals = sub[feat]
            row[f"{feat}_mean"] = vals.mean()
            row[f"{feat}_sd"] = vals.std()
            row[f"{feat}_median"] = vals.median()
            row[f"{feat}_q25"] = vals.quantile(0.25)
            row[f"{feat}_q75"] = vals.quantile(0.75)
        records.append(row)
    return pd.DataFrame(records)


def assign_labels(profiles: pd.DataFrame) -> dict[int, str]:
    """Assign interpretive labels based on temperature and PM2.5 percentiles."""
    label_map = {}
    # Sort by t_med_mean descending
    ranked = profiles.sort_values("t_med_mean", ascending=False).reset_index(drop=True)
    n = len(ranked)

    for i, (_, row) in enumerate(ranked.iterrows()):
        cl = int(row["cluster"])
        high_temp = i < n / 2
        high_pm = row.get("pm2.5_epa_mean", 0) > profiles["pm2.5_epa_mean"].median()

        if high_temp and high_pm:
            label_map[cl] = "Polluted Heat"
        elif high_temp and not high_pm:
            label_map[cl] = "Clean Heat"
        elif not high_temp and high_pm:
            label_map[cl] = "Moderate Transition"
        else:
            label_map[cl] = "Clean Cold"

    # De-duplicate labels by appending index if needed
    seen = {}
    for cl in sorted(label_map):
        lbl = label_map[cl]
        if lbl in seen:
            seen[lbl] += 1
            label_map[cl] = f"{lbl} {seen[lbl]}"
        else:
            seen[lbl] = 1
    return label_map


# ══════════════════════════════════════════════════════════════════════════════
# 7. MANUSCRIPT VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def validate_manuscript(profiles: pd.DataFrame, label_map: dict[int, str],
                        verbose: bool = False) -> str:
    """Compare computed clusters against manuscript values and flag F→C error."""
    lines = [
        "VALIDATION REPORT: Manuscript vs Computed Clusters",
        "=" * 60,
        "",
        "Manuscript values are reproduced from the published table.",
        "Computed values come from K-means on the actual data.",
        "",
    ]

    # Fahrenheit check
    lines.append("── Fahrenheit → Celsius Check ──")
    lines.append("")
    for name, mvals in MANUSCRIPT_CLUSTERS.items():
        tmax_c = (mvals["Tmax"] - 32) * 5 / 9
        tmed_c = (mvals["Tmed"] - 32) * 5 / 9
        tmin_c = (mvals["Tmin"] - 32) * 5 / 9
        lines.append(f"  {name}:")
        lines.append(f"    Manuscript 'Tmax (°C)' = {mvals['Tmax']:.1f}")
        lines.append(f"    If Fahrenheit → Celsius:  {tmax_c:.1f} °C")
        lines.append(f"    Plausible for Curitiba (subtropical, ~16-30 °C)? "
                     f"{'YES' if 10 < tmax_c < 40 else 'NO'}")
        lines.append(f"    Original value plausible as °C (>60°C)? NO — "
                     f"{'CONFIRMED FAHRENHEIT' if mvals['Tmax'] > 50 else 'uncertain'}")
        lines.append("")

    lines.append("CONCLUSION: All manuscript temperature values are in FAHRENHEIT")
    lines.append("            mislabelled as Celsius. This is divergence D7.")
    lines.append("")

    # Side-by-side comparison
    lines.append("── Cluster-by-Cluster Comparison ──")
    lines.append("")

    # Convert manuscript values to Celsius for comparison
    ms_celsius = {}
    for name, mvals in MANUSCRIPT_CLUSTERS.items():
        ms_celsius[name] = {
            "Tmax": (mvals["Tmax"] - 32) * 5 / 9,
            "Tmed": (mvals["Tmed"] - 32) * 5 / 9,
            "Tmin": (mvals["Tmin"] - 32) * 5 / 9,
            "PM2.5": mvals["PM2.5"],
        }

    for cl_id in sorted(label_map):
        computed_name = label_map[cl_id]
        row = profiles[profiles["cluster"] == cl_id].iloc[0]

        lines.append(f"  Computed cluster {cl_id} → '{computed_name}' (n={int(row['n'])})")
        lines.append(f"    Tmax  = {row['t_max_mean']:.1f} °C (sd={row['t_max_sd']:.1f})")
        lines.append(f"    Tmed  = {row['t_med_mean']:.1f} °C (sd={row['t_med_sd']:.1f})")
        lines.append(f"    Tmin  = {row['t_min_mean']:.1f} °C (sd={row['t_min_sd']:.1f})")
        lines.append(f"    PM2.5 = {row['pm2.5_epa_mean']:.1f} µg/m³ (sd={row['pm2.5_epa_sd']:.1f})")

        # Find closest manuscript cluster
        best_match, best_dist = None, float("inf")
        for ms_name, ms_vals in ms_celsius.items():
            dist = abs(row["t_med_mean"] - ms_vals["Tmed"])
            if dist < best_dist:
                best_dist = dist
                best_match = ms_name

        if best_match:
            ms_v = ms_celsius[best_match]
            tmed_diff = abs(row["t_med_mean"] - ms_v["Tmed"])
            if tmed_diff < 2:
                verdict = "MATCH"
            elif tmed_diff < 5:
                verdict = "PARTIAL"
            else:
                verdict = "DIVERGENT"
            lines.append(f"    Closest manuscript cluster: '{best_match}' "
                         f"(Tmed={ms_v['Tmed']:.1f} °C after F→C)")
            lines.append(f"    Agreement: {verdict} (ΔTmed = {tmed_diff:.1f} °C)")
        lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 8. HEALTH CORRELATION (EXPLORATORY)
# ══════════════════════════════════════════════════════════════════════════════

def lag_correlations(df: pd.DataFrame, labels: np.ndarray,
                     max_lag: int = 14,
                     verbose: bool = False) -> pd.DataFrame:
    """Cross-correlation between cluster membership and hospitalisations."""
    df = df.copy()
    df["cluster"] = labels

    records = []
    clusters = sorted(df["cluster"].unique())

    for cl in clusters:
        df[f"in_cl_{cl}"] = (df["cluster"] == cl).astype(int)

    hosp_col = "Hospitalizations" if "Hospitalizations" in df.columns else "freq_internacao_abs"
    if hosp_col not in df.columns:
        if verbose:
            print("[health] No hospitalization column found, skipping lag analysis.")
        return pd.DataFrame()

    for cl in clusters:
        membership = df[f"in_cl_{cl}"]
        for lag in range(max_lag + 1):
            hosp = df[hosp_col].shift(-lag)
            valid = pd.notna(hosp) & pd.notna(membership)
            if valid.sum() < 30:
                continue
            r_pearson, p_pearson = stats.pearsonr(
                membership[valid], hosp[valid]
            )
            r_spearman, p_spearman = stats.spearmanr(
                membership[valid], hosp[valid]
            )
            records.append({
                "cluster": cl,
                "lag_days": lag,
                "pearson_r": r_pearson,
                "pearson_p": p_pearson,
                "spearman_rho": r_spearman,
                "spearman_p": p_spearman,
            })

    return pd.DataFrame(records)


def kruskal_wallis_test(df: pd.DataFrame, labels: np.ndarray,
                        verbose: bool = False) -> dict:
    """Kruskal-Wallis test for differences in hospitalisations across clusters."""
    df = df.copy()
    df["cluster"] = labels
    hosp_col = "Hospitalizations" if "Hospitalizations" in df.columns else "freq_internacao_abs"
    if hosp_col not in df.columns:
        return {}

    groups = [g[hosp_col].dropna().values for _, g in df.groupby("cluster")]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 2:
        return {}

    stat, pval = stats.kruskal(*groups)
    result = {"H_statistic": stat, "p_value": pval, "n_groups": len(groups)}

    # Per-cluster descriptives
    cluster_stats = []
    for cl in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cl][hosp_col].dropna()
        cluster_stats.append({
            "cluster": cl,
            "n": len(sub),
            "mean_hosp": sub.mean(),
            "median_hosp": sub.median(),
            "sd_hosp": sub.std(),
        })
    result["cluster_stats"] = pd.DataFrame(cluster_stats)

    if verbose:
        print(f"[kruskal] H={stat:.2f}, p={pval:.4f}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 9. FIGURES
# ══════════════════════════════════════════════════════════════════════════════

def plot_k_selection(metrics: pd.DataFrame, gap_df: pd.DataFrame | None = None):
    """2x2 panel: elbow, silhouette, CH, DB (+ gap if available)."""
    n_panels = 5 if gap_df is not None else 4
    ncols = 3 if gap_df is not None else 2
    nrows = 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5 * ncols, 4 * nrows))
    axes = axes.flatten()

    valid = metrics.dropna(subset=["silhouette"])

    # Elbow
    ax = axes[0]
    ax.plot(metrics["K"], metrics["inertia"], "o-", color=PALETTE[0], lw=1.5)
    ax.set_xlabel("K")
    ax.set_ylabel("Inertia (within-cluster SS)")
    ax.set_title("(a) Elbow Method")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Silhouette
    ax = axes[1]
    ax.plot(valid["K"], valid["silhouette"], "s-", color=PALETTE[1], lw=1.5)
    ax.set_xlabel("K")
    ax.set_ylabel("Silhouette Score")
    ax.set_title("(b) Silhouette Score")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Calinski-Harabasz
    ax = axes[2]
    ax.plot(valid["K"], valid["calinski_harabasz"], "^-", color=PALETTE[2], lw=1.5)
    ax.set_xlabel("K")
    ax.set_ylabel("Calinski-Harabasz Index")
    ax.set_title("(c) Calinski-Harabasz")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Davies-Bouldin
    ax = axes[3]
    ax.plot(valid["K"], valid["davies_bouldin"], "D-", color=PALETTE[3], lw=1.5)
    ax.set_xlabel("K")
    ax.set_ylabel("Davies-Bouldin Index")
    ax.set_title("(d) Davies-Bouldin")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Gap statistic (optional)
    if gap_df is not None:
        ax = axes[4]
        ax.errorbar(gap_df["K"], gap_df["gap"], yerr=gap_df["sk"],
                     fmt="v-", color=PALETTE[4], lw=1.5, capsize=3)
        ax.set_xlabel("K")
        ax.set_ylabel("Gap Statistic")
        ax.set_title("(e) Gap Statistic")
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Hide unused axes
    for i in range(n_panels, len(axes)):
        axes[i].set_visible(False)

    fig.tight_layout()
    path = FIG_DIR / "fig_elbow_silhouette.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_pca_biplot(X: np.ndarray, labels: np.ndarray, features: list[str],
                    label_map: dict[int, str]):
    """PCA biplot coloured by cluster."""
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)

    fig, ax = plt.subplots(figsize=(7, 6))
    clusters = sorted(set(labels))
    for cl in clusters:
        mask = labels == cl
        lbl = label_map.get(cl, f"Cluster {cl}")
        ax.scatter(X2[mask, 0], X2[mask, 1], s=12, alpha=0.6,
                   color=PALETTE[cl % len(PALETTE)], label=lbl)

    # Loading vectors
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    scale = 3.0
    _DISPLAY = {
        "t_max": r"$T_{\mathrm{max}}$",
        "t_med": r"$T_{\mathrm{med}}$",
        "t_min": r"$T_{\mathrm{min}}$",
        "pm2.5_epa": r"$\mathrm{PM}_{2.5}$",
        "umidade_relativa": "Relative humidity",
        "pressure": "Pressure",
    }
    for i, feat in enumerate(features):
        ax.annotate(
            _DISPLAY.get(feat, feat), xy=(0, 0),
            xytext=(loadings[i, 0] * scale, loadings[i, 1] * scale),
            arrowprops=dict(arrowstyle="->", color="grey", lw=1),
            fontsize=8, color="grey", ha="center", va="center",
        )

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_title("PCA Biplot of Cluster Assignments")
    ax.legend(loc="best", frameon=True, framealpha=0.9)
    fig.tight_layout()
    path = FIG_DIR / "fig_cluster_pca.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_cluster_profiles(profiles: pd.DataFrame, features: list[str],
                          label_map: dict[int, str]):
    """Heatmap of cluster centroids (z-scored for visualisation)."""
    # Build matrix: clusters × features
    mat = np.zeros((len(profiles), len(features)))
    for i, (_, row) in enumerate(profiles.iterrows()):
        for j, feat in enumerate(features):
            mat[i, j] = row[f"{feat}_mean"]

    # Z-score columns for heatmap visibility
    z = (mat - mat.mean(axis=0)) / (mat.std(axis=0) + 1e-9)

    ylabels = [label_map.get(int(row["cluster"]), f"C{int(row['cluster'])}")
               for _, row in profiles.iterrows()]

    fig, ax = plt.subplots(figsize=(max(6, len(features) * 1.2), max(3, len(profiles) * 0.8)))
    im = ax.imshow(z, aspect="auto", cmap="RdYlBu_r")

    ax.set_xticks(range(len(features)))
    _DISPLAY = {
        "t_max": r"$T_{\mathrm{max}}$",
        "t_med": r"$T_{\mathrm{med}}$",
        "t_min": r"$T_{\mathrm{min}}$",
        "pm2.5_epa": r"$\mathrm{PM}_{2.5}$",
        "umidade_relativa": "Rel. humidity",
        "pressure": "Pressure",
    }
    ax.set_xticklabels([_DISPLAY.get(f, f) for f in features], fontsize=9)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=9)

    # Annotate with raw values
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            ax.text(j, i, f"{mat[i, j]:.1f}", ha="center", va="center", fontsize=8)

    plt.colorbar(im, ax=ax, label="Z-score", shrink=0.8)
    ax.set_title("Cluster Centroids (values = raw means, colours = z-scored)")
    fig.tight_layout()
    path = FIG_DIR / "fig_cluster_profiles.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_lag_correlations(lag_df: pd.DataFrame, label_map: dict[int, str]):
    """Lag-correlation plot: Pearson r per cluster across lags 0-14."""
    if lag_df.empty:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    clusters = sorted(lag_df["cluster"].unique())

    for cl in clusters:
        sub = lag_df[lag_df["cluster"] == cl]
        lbl = label_map.get(cl, f"C{cl}")
        axes[0].plot(sub["lag_days"], sub["pearson_r"], "o-",
                     color=PALETTE[cl % len(PALETTE)], label=lbl, lw=1.2, ms=4)
        axes[1].plot(sub["lag_days"], sub["spearman_rho"], "s-",
                     color=PALETTE[cl % len(PALETTE)], label=lbl, lw=1.2, ms=4)

    for ax, title, ylabel in [
        (axes[0], "(a) Pearson r", "Pearson r"),
        (axes[1], "(b) Spearman ρ", "Spearman ρ"),
    ]:
        ax.axhline(0, color="grey", ls="--", lw=0.5)
        ax.set_xlabel("Lag (days)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(loc="best", fontsize=8)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.suptitle("Cluster Membership × Hospitalisation Lag Correlations", y=1.02)
    fig.tight_layout()
    path = FIG_DIR / "fig_lag_correlation.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_method_comparison(X: np.ndarray, k: int, label_map: dict[int, str]):
    """Side-by-side PCA scatter: K-means vs Ward vs DBSCAN."""
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)

    # Fit each method
    km = KMeans(n_clusters=k, n_init=20, random_state=42)
    lbl_km = km.fit_predict(X)

    ward = AgglomerativeClustering(n_clusters=k, linkage="ward")
    lbl_ward = ward.fit_predict(X)

    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=2 * X.shape[1])
    nn.fit(X)
    distances, _ = nn.kneighbors(X)
    eps = np.percentile(distances[:, -1], 90)
    dbs = DBSCAN(eps=eps, min_samples=2 * X.shape[1])
    lbl_db = dbs.fit_predict(X)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, lbl, title in [
        (axes[0], lbl_km, "K-means"),
        (axes[1], lbl_ward, "Ward Hierarchical"),
        (axes[2], lbl_db, "DBSCAN"),
    ]:
        unique = sorted(set(lbl))
        for cl in unique:
            mask = lbl == cl
            name = f"Noise" if cl == -1 else f"C{cl}"
            color = "lightgrey" if cl == -1 else PALETTE[cl % len(PALETTE)]
            ax.scatter(X2[mask, 0], X2[mask, 1], s=10, alpha=0.5,
                       color=color, label=name)
        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
        ax.set_title(title)
        ax.legend(loc="best", fontsize=7, ncol=2)

    fig.suptitle(f"Method Comparison (K={k})", y=1.02)
    fig.tight_layout()
    path = FIG_DIR / "fig_method_comparison.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Clustering analysis for CWB temperature–pollution–health study",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--k", type=int, default=None,
                        help="Force cluster count (default: auto-select)")
    parser.add_argument("--features", type=int, choices=[4, 6], default=6,
                        help="Number of features: 6 (all) or 4 (no pressure/humidity)")
    parser.add_argument("--imputation", choices=["dropna", "mean", "median", "knn"],
                        default="dropna", help="Missing-data strategy")
    parser.add_argument("--gap-statistic", action="store_true",
                        help="Compute gap statistic (slow)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print progress")
    args = parser.parse_args()

    features = FEATURES_6 if args.features == 6 else FEATURES_4
    v = args.verbose

    # Ensure output dirs exist
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TBL_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Load & merge ──────────────────────────────────────────────────
    if v:
        print("\n══ STEP 1: Loading data ══")
    df = merge_datasets(verbose=v)

    # ── 2. Audit & missing data ──────────────────────────────────────────
    if v:
        print("\n══ STEP 2: Data audit & missing handling ══")
    audit_text = audit_data(df, features)
    audit_path = OUT_DIR / "data_audit.txt"
    audit_path.write_text(audit_text, encoding="utf-8")
    if v:
        print(audit_text)

    df = handle_missing(df, features, method=args.imputation, verbose=v)
    n_obs = len(df)

    # ── 3. Scale ─────────────────────────────────────────────────────────
    if v:
        print(f"\n══ STEP 3: Standardising {len(features)} features on {n_obs} obs ══")
    X, scaler = scale_features(df, features)

    # ── 4. K selection ───────────────────────────────────────────────────
    if v:
        print("\n══ STEP 4: K selection metrics ══")
    k_range = range(2, 11)
    metrics = k_selection_metrics(X, k_range, verbose=v)
    metrics.to_csv(TBL_DIR / "table_k_selection.csv", index=False, float_format="%.4f")

    gap_df = None
    if args.gap_statistic:
        gap_df = gap_statistic(X, k_range, verbose=v)

    optimal_k = find_optimal_k(metrics)
    k_final = args.k if args.k is not None else optimal_k
    if v:
        print(f"  Optimal K (silhouette) = {optimal_k}")
        print(f"  Using K = {k_final}" +
              (" (user-specified)" if args.k else " (auto-selected)"))

    # ── 5. Method comparison ─────────────────────────────────────────────
    if v:
        print(f"\n══ STEP 5: Method comparison (K={k_final}) ══")
    method_df = compare_methods(X, k_final, verbose=v)
    method_df.to_csv(TBL_DIR / "table_method_comparison.csv",
                     index=False, float_format="%.4f")

    # ── 6. Final clustering + profiles ───────────────────────────────────
    if v:
        print(f"\n══ STEP 6: K-means clustering (K={k_final}) ══")
    labels, km_model = run_kmeans(X, k_final)
    profiles = cluster_profiles(df, labels, features)
    label_map = assign_labels(profiles)

    if v:
        print("  Cluster profiles (means on original scale):")
        for _, row in profiles.iterrows():
            cl = int(row["cluster"])
            name = label_map.get(cl, f"C{cl}")
            parts = [f"{f}={row[f'{f}_mean']:.1f}" for f in features]
            print(f"    {name} (n={int(row['n'])}): {', '.join(parts)}")

    profiles_out = profiles.copy()
    profiles_out["label"] = profiles_out["cluster"].map(label_map)
    profiles_out.to_csv(TBL_DIR / "table_cluster_profiles.csv",
                        index=False, float_format="%.2f")

    # Also run K=4 for manuscript validation if user chose a different K
    if k_final != 4:
        if v:
            print("\n  Running K=4 for manuscript validation …")
        labels_4, _ = run_kmeans(X, 4)
        profiles_4 = cluster_profiles(df, labels_4, features)
        label_map_4 = assign_labels(profiles_4)
    else:
        labels_4, profiles_4, label_map_4 = labels, profiles, label_map

    # ── 7. Manuscript validation ─────────────────────────────────────────
    if v:
        print("\n══ STEP 7: Manuscript validation ══")
    val_text = validate_manuscript(profiles_4, label_map_4, verbose=v)
    val_path = OUT_DIR / "validation_report.txt"
    val_path.write_text(val_text, encoding="utf-8")
    if v:
        print(val_text)

    # Manuscript comparison table
    ms_records = []
    for cl_id in sorted(label_map_4):
        row = profiles_4[profiles_4["cluster"] == cl_id].iloc[0]
        computed_name = label_map_4[cl_id]

        # Find closest manuscript cluster by Tmed (after F→C conversion)
        best_match = None
        best_dist = float("inf")
        for ms_name, ms_vals in MANUSCRIPT_CLUSTERS.items():
            ms_tmed_c = (ms_vals["Tmed"] - 32) * 5 / 9
            dist = abs(row["t_med_mean"] - ms_tmed_c)
            if dist < best_dist:
                best_dist = dist
                best_match = ms_name

        ms_vals_c = MANUSCRIPT_CLUSTERS.get(best_match, {})
        ms_records.append({
            "computed_cluster": computed_name,
            "computed_tmax": row["t_max_mean"],
            "computed_tmed": row["t_med_mean"],
            "computed_tmin": row["t_min_mean"],
            "computed_pm25": row["pm2.5_epa_mean"],
            "computed_n": int(row["n"]),
            "manuscript_cluster": best_match,
            "manuscript_tmax_F": ms_vals_c.get("Tmax"),
            "manuscript_tmax_as_C": (ms_vals_c.get("Tmax", 32) - 32) * 5 / 9,
            "manuscript_tmed_F": ms_vals_c.get("Tmed"),
            "manuscript_tmed_as_C": (ms_vals_c.get("Tmed", 32) - 32) * 5 / 9,
            "delta_tmed": best_dist,
            "agreement": "MATCH" if best_dist < 2 else ("PARTIAL" if best_dist < 5 else "DIVERGENT"),
        })
    pd.DataFrame(ms_records).to_csv(
        TBL_DIR / "table_manuscript_comparison.csv", index=False, float_format="%.2f"
    )

    # ── 8. Health correlation ────────────────────────────────────────────
    if v:
        print("\n══ STEP 8: Health lag correlations ══")
    lag_df = lag_correlations(df, labels, max_lag=14, verbose=v)
    if not lag_df.empty:
        lag_df.to_csv(TBL_DIR / "table_lag_correlations.csv",
                      index=False, float_format="%.4f")

    kw = kruskal_wallis_test(df, labels, verbose=v)
    if kw and "cluster_stats" in kw:
        kw_df = kw["cluster_stats"]
        kw_df["label"] = kw_df["cluster"].map(label_map)
        kw_df["kruskal_H"] = kw["H_statistic"]
        kw_df["kruskal_p"] = kw["p_value"]
        kw_df.to_csv(TBL_DIR / "table_cluster_health_stats.csv",
                     index=False, float_format="%.4f")

    # ── 9. Figures ───────────────────────────────────────────────────────
    if v:
        print("\n══ STEP 9: Generating figures ══")

    p1 = plot_k_selection(metrics, gap_df)
    if v:
        print(f"  → {p1}")

    p2 = plot_pca_biplot(X, labels, features, label_map)
    if v:
        print(f"  → {p2}")

    p3 = plot_cluster_profiles(profiles, features, label_map)
    if v:
        print(f"  → {p3}")

    p4 = plot_lag_correlations(lag_df, label_map)
    if v and p4:
        print(f"  → {p4}")

    p5 = plot_method_comparison(X, k_final, label_map)
    if v:
        print(f"  → {p5}")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Clustering complete.")
    print(f"  Observations: {n_obs}")
    print(f"  Features:     {len(features)} ({', '.join(features)})")
    print(f"  K (final):    {k_final} (optimal by silhouette: {optimal_k})")
    print(f"  Imputation:   {args.imputation}")
    print(f"  Output:       {OUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
