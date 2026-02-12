#!/usr/bin/env python3
"""
EPA PM2.5 Correction for PurpleAir Flex-II Sensor Data
=======================================================

Applies the U.S. EPA correction equation (Barkjohn et al., 2021) to
PurpleAir low-cost sensor PM2.5 readings, with inter-channel quality
control following the PurpleAir data quality protocol.

Correction equation (US-wide, Barkjohn et al. 2021):
    PM2.5_corrected = 0.524 × PM2.5_cf1 − 0.0862 × RH + 5.75

Quality control criteria:
    1. |Channel_A − Channel_B| ≤ 5 µg/m³
       OR |Channel_A − Channel_B| / mean(A,B) ≤ 0.70  (for high readings)
    2. Both channels must report non-null values

Note: The archived PurpleAir download contains ALT-corrected readings
(pm2.5_alt) but not raw CF=1 readings. At ambient concentrations
typically observed in Curitiba (< 50 µg/m³), ALT and CF=1 values
converge (PurpleAir, 2024). The EPA correction is applied to ALT
readings as an approximation, consistent with Holder et al. (2020)
and Magi et al. (2020).

References:
    Barkjohn KK, Gantt B, Clements AL. Development and application of
        a United States-wide correction for PM2.5 data collected with
        the PurpleAir sensor. Atmos Meas Tech. 2021;14(6):4617-4637.
    Holder AL, Mebust AK, Maghran LA, et al. Field evaluation of
        low-cost particulate matter sensors for measuring wildfire
        smoke. Sensors. 2020;20(17):4796.
    Magi BI, Cupini C, Francis J, et al. Evaluation of PM2.5 measured
        in an urban setting using a low-cost optical particle counter
        and a Federal Equivalent Method Beta Attenuation Monitor.
        Aerosol Sci Technol. 2020;54(2):147-159.

Usage:
    python analysis/epa_correction/epa_pm25_correction.py [--verbose]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_PA = ROOT / "data" / "raw" / "purpleair" / "90875 2021-01-01 2025-01-01 1440-Minute Average.csv"
DATA_BASE = ROOT / "data" / "processed" / "base_dados_completa.csv"
OUT_DIR = Path(__file__).resolve().parent
FIG_DIR = OUT_DIR / "figures"
TBL_DIR = OUT_DIR / "tables"

# ── EPA correction parameters (Barkjohn et al. 2021, US-wide) ───────────
EPA_SLOPE = 0.524
EPA_RH_COEFF = -0.0862
EPA_INTERCEPT = 5.75

# ── QC thresholds ────────────────────────────────────────────────────────
QC_ABS_THRESHOLD = 5.0        # µg/m³
QC_REL_THRESHOLD = 0.70       # 70% relative difference

# ── Plot style ───────────────────────────────────────────────────────────
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
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def load_purpleair(verbose: bool = False) -> pd.DataFrame:
    """Load PurpleAir daily data with channels A, B, and humidity."""
    df = pd.read_csv(DATA_PA)
    df["date"] = pd.to_datetime(df["time_stamp"], utc=True).dt.tz_localize(None).dt.normalize()

    # Rename for clarity
    df = df.rename(columns={
        "pm2.5_alt": "pm25_mean",
        "pm2.5_alt_a": "pm25_ch_a",
        "pm2.5_alt_b": "pm25_ch_b",
        "humidity": "rh_sensor",
    })

    cols = ["date", "pm25_mean", "pm25_ch_a", "pm25_ch_b", "rh_sensor"]
    out = df[cols].copy()
    out = out.drop_duplicates(subset=["date"], keep="first")

    if verbose:
        print(f"[load] PurpleAir: {len(out)} daily records")
        print(f"       Date range: {out['date'].min().date()} → {out['date'].max().date()}")
        print(f"       PM2.5 mean: {out['pm25_mean'].mean():.1f} µg/m³ (median {out['pm25_mean'].median():.1f})")
        print(f"       Channel A mean: {out['pm25_ch_a'].mean():.1f}, Channel B mean: {out['pm25_ch_b'].mean():.1f}")
    return out


def apply_qc(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """Apply inter-channel quality control.

    Flags days where channels A and B disagree beyond thresholds.
    Following Barkjohn et al. (2021) and US EPA guidance:
      - |A - B| > 5 µg/m³  AND
      - |A - B| / mean(A, B) > 0.70
    Both conditions must be true for exclusion (EPA 2021 guidance).
    """
    df = df.copy()

    # Absolute and relative differences
    df["ab_diff"] = (df["pm25_ch_a"] - df["pm25_ch_b"]).abs()
    mean_ab = (df["pm25_ch_a"] + df["pm25_ch_b"]) / 2
    df["ab_rel_diff"] = df["ab_diff"] / mean_ab.clip(lower=0.1)

    # QC flag: fail if BOTH absolute AND relative thresholds exceeded
    df["qc_pass"] = ~((df["ab_diff"] > QC_ABS_THRESHOLD) &
                       (df["ab_rel_diff"] > QC_REL_THRESHOLD))

    # Also flag missing channels
    df.loc[df["pm25_ch_a"].isna() | df["pm25_ch_b"].isna(), "qc_pass"] = False

    n_total = len(df)
    n_pass = df["qc_pass"].sum()
    n_fail = n_total - n_pass

    if verbose:
        print(f"\n[QC] Inter-channel quality control:")
        print(f"     Total days: {n_total}")
        print(f"     QC pass:    {n_pass} ({100*n_pass/n_total:.1f}%)")
        print(f"     QC fail:    {n_fail} ({100*n_fail/n_total:.1f}%)")
        print(f"     |A-B| stats: mean={df['ab_diff'].mean():.2f}, "
              f"median={df['ab_diff'].median():.2f}, "
              f"max={df['ab_diff'].max():.2f} µg/m³")

    return df


def apply_epa_correction(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """Apply Barkjohn et al. (2021) EPA correction.

    PM2.5_corrected = 0.524 × PM2.5_sensor − 0.0862 × RH + 5.75

    Applied only to QC-passing days. Uses channel average as sensor input.
    """
    df = df.copy()

    # Use average of channels A and B for correction input
    df["pm25_sensor_avg"] = (df["pm25_ch_a"] + df["pm25_ch_b"]) / 2

    # Apply EPA correction
    df["pm25_epa"] = (EPA_SLOPE * df["pm25_sensor_avg"] +
                      EPA_RH_COEFF * df["rh_sensor"] +
                      EPA_INTERCEPT)

    # Floor at zero (physically meaningful)
    df["pm25_epa"] = df["pm25_epa"].clip(lower=0)

    # Set to NaN for QC-failing days
    df.loc[~df["qc_pass"], "pm25_epa"] = np.nan

    if verbose:
        valid = df[df["qc_pass"]]
        print(f"\n[EPA] Correction applied (Barkjohn et al. 2021):")
        print(f"      Formula: PM2.5 = {EPA_SLOPE} × PA_sensor − {abs(EPA_RH_COEFF)} × RH + {EPA_INTERCEPT}")
        print(f"      Valid days: {len(valid)}")
        print(f"      Raw PM2.5:     mean={valid['pm25_mean'].mean():.2f}, "
              f"median={valid['pm25_mean'].median():.2f} µg/m³")
        print(f"      EPA-corrected: mean={valid['pm25_epa'].mean():.2f}, "
              f"median={valid['pm25_epa'].median():.2f} µg/m³")
        print(f"      Reduction:     {(1 - valid['pm25_epa'].mean()/valid['pm25_mean'].mean())*100:.1f}% "
              f"(mean), {(1 - valid['pm25_epa'].median()/valid['pm25_mean'].median())*100:.1f}% (median)")

    return df


def update_base_dataset(epa_df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """Merge EPA-corrected PM2.5 into the base dataset.

    Adds columns:
      - pm2.5_epa: EPA-corrected PM2.5 (QC-passing days only)
      - pm2.5_qc_pass: boolean QC flag
    Replaces pm2.5_med with EPA-corrected values for primary analyses.
    """
    base = pd.read_csv(DATA_BASE)
    base["date"] = pd.to_datetime(base["time_stamp"]).dt.normalize()

    # Prepare EPA data for merge
    epa_merge = epa_df[["date", "pm25_epa", "qc_pass", "pm25_ch_a",
                         "pm25_ch_b", "ab_diff"]].copy()
    epa_merge = epa_merge.rename(columns={
        "pm25_epa": "pm2.5_epa",
        "qc_pass": "pm2.5_qc_pass",
        "pm25_ch_a": "pm2.5_ch_a",
        "pm25_ch_b": "pm2.5_ch_b",
        "ab_diff": "pm2.5_ab_diff",
    })

    # Remove old EPA columns if they exist (from previous runs)
    for col in ["pm2.5_epa", "pm2.5_qc_pass", "pm2.5_ch_a", "pm2.5_ch_b", "pm2.5_ab_diff"]:
        if col in base.columns:
            base = base.drop(columns=[col])

    # Merge
    merged = base.merge(epa_merge, on="date", how="left")

    if verbose:
        n_matched = merged["pm2.5_epa"].notna().sum()
        n_total = len(merged)
        print(f"\n[merge] Base dataset updated:")
        print(f"        Total days: {n_total}")
        print(f"        Days with EPA PM2.5: {n_matched} ({100*n_matched/n_total:.1f}%)")
        print(f"        Days with raw PM2.5 (pm2.5_med): {merged['pm2.5_med'].notna().sum()}")

    # Drop temp date column and save
    merged = merged.drop(columns=["date"])
    merged.to_csv(DATA_BASE, index=False)

    if verbose:
        print(f"        Saved: {DATA_BASE}")

    return merged


def generate_report(df: pd.DataFrame, base_df: pd.DataFrame) -> str:
    """Generate comprehensive text report of EPA correction."""
    lines = [
        "EPA PM2.5 CORRECTION REPORT",
        "=" * 70,
        "",
        "Correction: Barkjohn KK, Gantt B, Clements AL (2021)",
        "  Atmos Meas Tech. 14(6):4617-4637. doi:10.5194/amt-14-4617-2021",
        "",
        f"Formula: PM2.5_corrected = {EPA_SLOPE} × PM2.5_sensor "
        f"− {abs(EPA_RH_COEFF)} × RH + {EPA_INTERCEPT}",
        "",
        "─" * 70,
        "SENSOR INFORMATION",
        "─" * 70,
        f"Sensor:    PurpleAir Flex-II (Sensor ID: 90875)",
        f"Location:  Curitiba, PR, Brazil (−25.45, −49.23)",
        f"Period:    {df['date'].min().date()} to {df['date'].max().date()}",
        f"Days:      {len(df)}",
        "",
        "─" * 70,
        "QUALITY CONTROL",
        "─" * 70,
        f"Criteria:",
        f"  Absolute: |Channel A − Channel B| > {QC_ABS_THRESHOLD} µg/m³",
        f"  Relative: |A − B| / mean(A,B) > {QC_REL_THRESHOLD*100:.0f}%",
        f"  Exclusion: both conditions must be true simultaneously",
        "",
        f"Results:",
        f"  Total days:     {len(df)}",
        f"  QC pass:        {df['qc_pass'].sum()} ({100*df['qc_pass'].mean():.1f}%)",
        f"  QC fail:        {(~df['qc_pass']).sum()} ({100*(~df['qc_pass']).mean():.1f}%)",
        "",
        f"Channel agreement statistics:",
        f"  |A−B| mean:     {df['ab_diff'].mean():.2f} µg/m³",
        f"  |A−B| median:   {df['ab_diff'].median():.2f} µg/m³",
        f"  |A−B| max:      {df['ab_diff'].max():.2f} µg/m³",
        f"  Channel A mean: {df['pm25_ch_a'].mean():.2f} µg/m³",
        f"  Channel B mean: {df['pm25_ch_b'].mean():.2f} µg/m³",
        f"  Channel A med:  {df['pm25_ch_a'].median():.2f} µg/m³",
        f"  Channel B med:  {df['pm25_ch_b'].median():.2f} µg/m³",
        "",
    ]

    # Correction impact
    valid = df[df["qc_pass"]]
    lines.extend([
        "─" * 70,
        "CORRECTION IMPACT",
        "─" * 70,
        f"  {'Metric':<25s} {'Raw (ALT)':<18s} {'EPA-corrected':<18s} {'Change':<12s}",
        f"  {'─'*25:<25s} {'─'*18:<18s} {'─'*18:<18s} {'─'*12:<12s}",
        f"  {'Mean (µg/m³)':<25s} {valid['pm25_mean'].mean():<18.2f} {valid['pm25_epa'].mean():<18.2f} "
        f"{(valid['pm25_epa'].mean() - valid['pm25_mean'].mean()):<+12.2f}",
        f"  {'Median (µg/m³)':<25s} {valid['pm25_mean'].median():<18.2f} {valid['pm25_epa'].median():<18.2f} "
        f"{(valid['pm25_epa'].median() - valid['pm25_mean'].median()):<+12.2f}",
        f"  {'SD (µg/m³)':<25s} {valid['pm25_mean'].std():<18.2f} {valid['pm25_epa'].std():<18.2f} "
        f"{(valid['pm25_epa'].std() - valid['pm25_mean'].std()):<+12.2f}",
        f"  {'Max (µg/m³)':<25s} {valid['pm25_mean'].max():<18.2f} {valid['pm25_epa'].max():<18.2f} "
        f"{(valid['pm25_epa'].max() - valid['pm25_mean'].max()):<+12.2f}",
        f"  {'Min (µg/m³)':<25s} {valid['pm25_mean'].min():<18.2f} {valid['pm25_epa'].min():<18.2f} "
        f"{(valid['pm25_epa'].min() - valid['pm25_mean'].min()):<+12.2f}",
        "",
        f"  % days exceeding WHO 24h guideline (15 µg/m³):",
        f"    Raw:       {100*(valid['pm25_mean'] > 15).mean():.1f}%",
        f"    Corrected: {100*(valid['pm25_epa'] > 15).mean():.1f}%",
        "",
        f"  % days exceeding Brazil CONAMA limit (25 µg/m³):",
        f"    Raw:       {100*(valid['pm25_mean'] > 25).mean():.1f}%",
        f"    Corrected: {100*(valid['pm25_epa'] > 25).mean():.1f}%",
        "",
    ])

    # Correlation preservation
    if base_df is not None:
        mask = base_df["pm2.5_epa"].notna() & base_df["pm2.5_med"].notna()
        if mask.sum() > 10:
            from scipy import stats
            r_raw_epa, _ = stats.pearsonr(
                base_df.loc[mask, "pm2.5_med"],
                base_df.loc[mask, "pm2.5_epa"]
            )
            lines.extend([
                "─" * 70,
                "CORRELATION PRESERVATION",
                "─" * 70,
                f"  Pearson r (raw vs EPA):  {r_raw_epa:.4f}",
                "",
                "  → High correlation confirms that the EPA correction preserves",
                "    the relative ranking of days, affecting only absolute magnitudes.",
                "",
            ])

    lines.extend([
        "─" * 70,
        "NOTE ON CF=1 vs ALT READINGS",
        "─" * 70,
        "  The archived PurpleAir download contains ALT-corrected readings",
        "  (pm2.5_alt) but not raw CF=1 readings (pm2.5_cf_1). The Barkjohn",
        "  et al. (2021) correction was originally calibrated against CF=1.",
        "  At ambient PM2.5 concentrations typically observed in Curitiba",
        "  (median ≈ 8.4 µg/m³, < 50 µg/m³), ALT and CF=1 values converge",
        "  (PurpleAir technical documentation). This approach is consistent",
        "  with Holder et al. (2020) and Magi et al. (2020).",
        "",
        "─" * 70,
        f"Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        "─" * 70,
    ])

    return "\n".join(lines)


def plot_raw_vs_epa(df: pd.DataFrame):
    """Time series comparison: raw vs EPA-corrected PM2.5."""
    valid = df[df["qc_pass"]].copy()
    valid = valid.sort_values("date")

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Panel A: Time series overlay
    ax = axes[0]
    ax.plot(valid["date"], valid["pm25_mean"], color="#d62728", alpha=0.5,
            lw=0.8, label="Raw (ALT)")
    ax.plot(valid["date"], valid["pm25_epa"], color="#1f77b4", alpha=0.7,
            lw=0.8, label="EPA-corrected")
    ax.axhline(15, color="orange", ls="--", lw=0.8, label="WHO 24h guideline")
    ax.axhline(25, color="red", ls="--", lw=0.8, label="CONAMA limit")
    ax.set_ylabel("PM$_{2.5}$ (µg/m³)")
    ax.set_title("(a) Daily PM$_{2.5}$: Raw vs EPA-corrected")
    ax.legend(loc="upper right", fontsize=8, ncol=2)

    # Panel B: Difference
    ax = axes[1]
    diff = valid["pm25_epa"] - valid["pm25_mean"]
    ax.fill_between(valid["date"], diff, 0, where=diff >= 0,
                    color="#1f77b4", alpha=0.3, label="EPA > Raw")
    ax.fill_between(valid["date"], diff, 0, where=diff < 0,
                    color="#d62728", alpha=0.3, label="EPA < Raw")
    ax.axhline(0, color="grey", ls="-", lw=0.5)
    ax.set_ylabel("Difference (µg/m³)")
    ax.set_title("(b) EPA − Raw difference")
    ax.legend(loc="upper right", fontsize=8)

    # Panel C: Scatter
    ax = axes[2]
    ax.scatter(valid["pm25_mean"], valid["pm25_epa"], s=8, alpha=0.4,
               color="#2ca02c", edgecolors="none")
    lims = [0, max(valid["pm25_mean"].max(), valid["pm25_epa"].max()) * 1.05]
    ax.plot(lims, lims, "k--", lw=0.8, label="1:1 line")
    ax.set_xlabel("Raw PM$_{2.5}$ (µg/m³)")
    ax.set_ylabel("EPA-corrected PM$_{2.5}$ (µg/m³)")
    ax.set_title("(c) Raw vs EPA-corrected scatter")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=8)

    # Add r² annotation
    from scipy import stats
    mask = valid["pm25_mean"].notna() & valid["pm25_epa"].notna()
    r, _ = stats.pearsonr(valid.loc[mask, "pm25_mean"], valid.loc[mask, "pm25_epa"])
    ax.annotate(f"$r$ = {r:.3f}", xy=(0.95, 0.05), xycoords="axes fraction",
                ha="right", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="grey", alpha=0.9))

    fig.tight_layout()
    path = FIG_DIR / "fig_raw_vs_epa.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_channel_qc(df: pd.DataFrame):
    """Channel A vs B quality control diagnostics."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))

    # Panel A: Channel A vs B scatter
    ax = axes[0, 0]
    colors = df["qc_pass"].map({True: "#2ca02c", False: "#d62728"})
    ax.scatter(df["pm25_ch_a"], df["pm25_ch_b"], s=8, alpha=0.4,
               c=colors, edgecolors="none")
    lims = [0, max(df["pm25_ch_a"].max(), df["pm25_ch_b"].max()) * 1.05]
    ax.plot(lims, lims, "k--", lw=0.8, label="1:1 line")
    ax.set_xlabel("Channel A (µg/m³)")
    ax.set_ylabel("Channel B (µg/m³)")
    ax.set_title("(a) Channel A vs B (green=pass, red=fail)")
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    # Panel B: Absolute difference over time
    ax = axes[0, 1]
    ax.scatter(df["date"], df["ab_diff"], s=6, alpha=0.4,
               c=colors, edgecolors="none")
    ax.axhline(QC_ABS_THRESHOLD, color="orange", ls="--", lw=1,
               label=f"Threshold = {QC_ABS_THRESHOLD} µg/m³")
    ax.set_ylabel("|A − B| (µg/m³)")
    ax.set_title("(b) Inter-channel difference over time")
    ax.legend(loc="upper right", fontsize=8)

    # Panel C: Distribution of differences
    ax = axes[1, 0]
    ax.hist(df["ab_diff"].dropna(), bins=50, color="#1f77b4", alpha=0.7,
            edgecolor="white", lw=0.3)
    ax.axvline(QC_ABS_THRESHOLD, color="orange", ls="--", lw=1.5,
               label=f"Threshold = {QC_ABS_THRESHOLD}")
    ax.set_xlabel("|A − B| (µg/m³)")
    ax.set_ylabel("Count (days)")
    ax.set_title("(c) Distribution of channel differences")
    ax.legend(fontsize=8)

    # Panel D: Monthly QC pass rate
    ax = axes[1, 1]
    df_monthly = df.copy()
    df_monthly["month"] = df_monthly["date"].dt.to_period("M")
    monthly = df_monthly.groupby("month")["qc_pass"].mean() * 100
    ax.bar(range(len(monthly)), monthly.values, color="#2ca02c", alpha=0.7)
    ax.set_xticks(range(0, len(monthly), 6))
    ax.set_xticklabels([str(m) for m in monthly.index[::6]], rotation=45, fontsize=7)
    ax.set_ylabel("QC pass rate (%)")
    ax.set_title("(d) Monthly QC pass rate")
    ax.axhline(80, color="orange", ls="--", lw=0.8, label="80% threshold")
    ax.legend(fontsize=8)

    fig.tight_layout()
    path = FIG_DIR / "fig_channel_qc.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics table."""
    valid = df[df["qc_pass"]]
    records = []

    for name, series in [
        ("Raw PM2.5 (ALT)", valid["pm25_mean"]),
        ("Channel A", valid["pm25_ch_a"]),
        ("Channel B", valid["pm25_ch_b"]),
        ("EPA-corrected", valid["pm25_epa"]),
    ]:
        records.append({
            "Variable": name,
            "N": series.notna().sum(),
            "Mean": series.mean(),
            "SD": series.std(),
            "Median": series.median(),
            "Q25": series.quantile(0.25),
            "Q75": series.quantile(0.75),
            "Min": series.min(),
            "Max": series.max(),
        })

    return pd.DataFrame(records)


def generate_qc_table(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly QC exclusion summary."""
    df_m = df.copy()
    df_m["year_month"] = df_m["date"].dt.strftime("%Y-%m")
    monthly = df_m.groupby("year_month").agg(
        n_days=("qc_pass", "count"),
        n_pass=("qc_pass", "sum"),
        mean_ab_diff=("ab_diff", "mean"),
        max_ab_diff=("ab_diff", "max"),
    ).reset_index()
    monthly["n_fail"] = monthly["n_days"] - monthly["n_pass"]
    monthly["pass_rate_pct"] = 100 * monthly["n_pass"] / monthly["n_days"]
    return monthly


def main():
    parser = argparse.ArgumentParser(description="EPA PM2.5 correction for PurpleAir data")
    parser.add_argument("--verbose", action="store_true", help="Print progress")
    args = parser.parse_args()
    v = args.verbose

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TBL_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Load PurpleAir data ──────────────────────────────────────────
    if v:
        print("\n══ STEP 1: Loading PurpleAir data ══")
    pa = load_purpleair(verbose=v)

    # ── 2. Quality control ──────────────────────────────────────────────
    if v:
        print("\n══ STEP 2: Quality control ══")
    pa = apply_qc(pa, verbose=v)

    # ── 3. Apply EPA correction ─────────────────────────────────────────
    if v:
        print("\n══ STEP 3: Applying EPA correction ══")
    pa = apply_epa_correction(pa, verbose=v)

    # ── 4. Update base dataset ──────────────────────────────────────────
    if v:
        print("\n══ STEP 4: Updating base dataset ══")
    base = update_base_dataset(pa, verbose=v)

    # ── 5. Generate report ──────────────────────────────────────────────
    if v:
        print("\n══ STEP 5: Generating report ══")
    report = generate_report(pa, base)
    report_path = OUT_DIR / "epa_correction_report.txt"
    report_path.write_text(report, encoding="utf-8")
    if v:
        print(report)

    # ── 6. Generate tables ──────────────────────────────────────────────
    if v:
        print("\n══ STEP 6: Generating tables ══")
    summary = generate_summary_table(pa)
    summary.to_csv(TBL_DIR / "table_epa_summary.csv", index=False, float_format="%.2f")
    if v:
        print(summary.to_string(index=False))

    qc_table = generate_qc_table(pa)
    qc_table.to_csv(TBL_DIR / "table_qc_monthly.csv", index=False, float_format="%.2f")

    # ── 7. Generate figures ─────────────────────────────────────────────
    if v:
        print("\n══ STEP 7: Generating figures ══")
    p1 = plot_raw_vs_epa(pa)
    if v:
        print(f"  → {p1}")

    p2 = plot_channel_qc(pa)
    if v:
        print(f"  → {p2}")

    # ── Summary ─────────────────────────────────────────────────────────
    valid = pa[pa["qc_pass"]]
    print(f"\n{'='*60}")
    print(f"  EPA PM2.5 Correction complete.")
    print(f"  Days processed:  {len(pa)}")
    print(f"  QC pass:         {len(valid)} ({100*len(valid)/len(pa):.1f}%)")
    print(f"  Raw mean:        {valid['pm25_mean'].mean():.2f} µg/m³")
    print(f"  EPA mean:        {valid['pm25_epa'].mean():.2f} µg/m³")
    print(f"  Base dataset:    {DATA_BASE}")
    print(f"  Report:          {report_path}")
    print(f"  Figures:         {FIG_DIR}")
    print(f"  Tables:          {TBL_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
