#!/usr/bin/env python3
"""
Cross-Basis Matrix Construction for DLNM
==========================================

Pure Python/NumPy/SciPy implementation of the distributed lag non-linear
model cross-basis, following:

  Gasparrini A. Distributed lag linear and non-linear models in R:
  the package dlnm. J Stat Softw. 2011;43(8):1-20.

  Gasparrini A, et al. Mortality risk attributable to high and low
  ambient temperature: a multicountry observational study. Lancet.
  2015;386(9991):369-375.

Uses scipy B-splines (not patsy) so that bases can be evaluated at
arbitrary new points after initial construction.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import BSpline


# ═══════════════════════════════════════════════════════════════════════
# 1. NATURAL CUBIC SPLINE BASIS (via scipy)
# ═══════════════════════════════════════════════════════════════════════

def _quantile_knots(x: np.ndarray, n_inner: int) -> np.ndarray:
    """Place *n_inner* interior knots at equally-spaced quantiles of *x*."""
    probs = np.linspace(0, 1, n_inner + 2)[1:-1]
    return np.quantile(x, probs)


def natural_spline_basis(
    x: np.ndarray,
    df: int | None = None,
    knots: np.ndarray | None = None,
    lower: float | None = None,
    upper: float | None = None,
) -> np.ndarray:
    """Evaluate a natural cubic spline basis.

    Constructs a B-spline basis of degree 3 and applies the natural-spline
    constraint (linear beyond the boundary knots) by projecting out the
    non-linear tail components, following the same approach as R's ``ns()``.

    Parameters
    ----------
    x : array, shape (n,)
    df : int, optional
        Number of basis columns desired.  ``df = n_inner_knots + 1``
        for a natural spline (intercept absorbed).
    knots : array, optional
        Interior knot positions.  If given, ``df`` is ignored and set to
        ``len(knots) + 1``.
    lower, upper : float, optional
        Boundary knot positions.  Default to min/max of *x*.

    Returns
    -------
    B : ndarray, shape (n, df)
    """
    x = np.asarray(x, dtype=float).ravel()

    if lower is None:
        lower = float(x.min())
    if upper is None:
        upper = float(x.max())

    if knots is not None:
        knots = np.sort(np.asarray(knots, dtype=float).ravel())
        n_inner = len(knots)
    elif df is not None:
        n_inner = df - 1
        if n_inner < 0:
            raise ValueError("df must be >= 1")
        if n_inner == 0:
            knots = np.array([])
        else:
            # Only use unique non-boundary values for knot placement
            knots = _quantile_knots(x, n_inner)
    else:
        raise ValueError("Provide either df or knots.")

    # All knots including boundaries
    all_knots = np.concatenate([[lower], knots, [upper]])
    n_all = len(all_knots)  # n_inner + 2

    # B-spline knot vector for degree 3 (clamped boundaries)
    t = np.concatenate([
        np.repeat(lower, 4),
        knots,
        np.repeat(upper, 4),
    ])
    n_bspline = len(t) - 4  # = n_inner + 4

    # Evaluate all B-spline basis functions
    B_full = np.zeros((len(x), n_bspline))
    for j in range(n_bspline):
        c = np.zeros(n_bspline)
        c[j] = 1.0
        spl = BSpline(t, c, 3, extrapolate=True)
        B_full[:, j] = spl(x)

    # Apply natural spline constraint via the approach in Hastie et al. (ESL):
    # We want the function to be linear beyond the boundary knots.
    # Use the QR-based projection: evaluate the basis at boundary knots and
    # their second derivatives, then project to the constrained subspace.
    #
    # Simpler approach: use the "derivative penalty" method.
    # For a natural cubic spline with K interior knots, df = K + 1 (no intercept).
    #
    # Implementation: evaluate second derivatives at boundary knots and
    # constrain them to zero → 2 constraints → df = n_bspline - 2 = n_inner + 2.
    # Then drop one column (intercept) → n_inner + 1 = desired df.

    # Second derivative at boundaries
    D2 = np.zeros((2, n_bspline))
    for j in range(n_bspline):
        c = np.zeros(n_bspline)
        c[j] = 1.0
        spl = BSpline(t, c, 3, extrapolate=True)
        d2 = spl.derivative(2)
        D2[0, j] = d2(lower)
        D2[1, j] = d2(upper)

    # Null space of D2 → columns that satisfy the natural constraint
    # D2 has shape (2, n_bspline). We want null space.
    from scipy.linalg import null_space
    N = null_space(D2)  # shape (n_bspline, n_bspline - 2)

    # Project B-spline basis onto natural subspace
    B_natural = B_full @ N  # shape (n, n_bspline - 2) = (n, n_inner + 2)

    # Drop first column (acts as intercept) to get df = n_inner + 1
    if B_natural.shape[1] > 1:
        B_natural = B_natural[:, 1:]

    # Target df
    target_df = n_inner + 1
    if B_natural.shape[1] != target_df:
        # Trim or pad to match — shouldn't happen in normal cases
        B_natural = B_natural[:, :target_df]

    return B_natural


class SplineMeta:
    """Stores knot information so we can re-evaluate at new points."""

    def __init__(self, knots, lower, upper, df):
        self.knots = knots
        self.lower = lower
        self.upper = upper
        self.df = df


def build_spline_meta(
    x: np.ndarray,
    df: int | None = None,
    knots: np.ndarray | None = None,
) -> SplineMeta:
    """Pre-compute knots from the training data."""
    x = np.asarray(x, dtype=float).ravel()
    lower = float(x.min())
    upper = float(x.max())
    if knots is not None:
        knots = np.sort(np.asarray(knots, dtype=float).ravel())
        actual_df = len(knots) + 1
    elif df is not None:
        n_inner = df - 1
        if n_inner <= 0:
            knots = np.array([])
        else:
            knots = _quantile_knots(x, n_inner)
        actual_df = df
    else:
        raise ValueError("Provide either df or knots.")
    return SplineMeta(knots=knots, lower=lower, upper=upper, df=actual_df)


def eval_spline(x: np.ndarray, meta: SplineMeta) -> np.ndarray:
    """Evaluate natural spline basis at new points using stored knots/bounds."""
    return natural_spline_basis(
        x, knots=meta.knots, lower=meta.lower, upper=meta.upper,
    )


# ═══════════════════════════════════════════════════════════════════════
# 2. LAGGED-EXPOSURE MATRIX
# ═══════════════════════════════════════════════════════════════════════

def _lag_matrix(exposure: np.ndarray, lag_max: int) -> np.ndarray:
    """Build matrix Q where Q[t, l] = exposure[t - l].

    Rows with unavailable lags (t < lag_max) are filled with NaN.
    """
    T = len(exposure)
    L = lag_max + 1
    Q = np.full((T, L), np.nan)
    for lag in range(L):
        if lag == 0:
            Q[:, lag] = exposure
        else:
            Q[lag:, lag] = exposure[:-lag]
    return Q


# ═══════════════════════════════════════════════════════════════════════
# 3. CROSS-BASIS MATRIX
# ═══════════════════════════════════════════════════════════════════════

class CrossBasisMeta:
    """Stores metadata needed to reconstruct predictions."""

    def __init__(
        self,
        exposure_df: int,
        lag_df: int,
        lag_max: int,
        exposure_spline: SplineMeta,
        lag_spline: SplineMeta,
        exposure_range: tuple[float, float],
    ):
        self.exposure_df = exposure_df
        self.lag_df = lag_df
        self.lag_max = lag_max
        self.n_basis = exposure_df * lag_df
        self.exposure_spline = exposure_spline
        self.lag_spline = lag_spline
        self.exposure_range = exposure_range


def _default_lag_knots(lag_max: int, lag_df: int) -> np.ndarray:
    """Log-equispaced interior lag knots (Gasparrini convention)."""
    n_interior = lag_df - 1  # ns: df = n_inner + 1 → n_inner = df - 1
    if n_interior <= 0:
        return np.array([])
    # Strictly interior to (0, lag_max)
    return np.exp(np.linspace(np.log(1), np.log(max(lag_max - 0.5, 1.5)),
                              n_interior))


def build_crossbasis(
    exposure: np.ndarray,
    lag_max: int,
    exposure_df: int = 4,
    lag_df: int = 5,
    exposure_knots: np.ndarray | None = None,
    lag_knots: np.ndarray | None = None,
) -> tuple[np.ndarray, CrossBasisMeta]:
    """Construct the DLNM cross-basis matrix.

    Parameters
    ----------
    exposure : array, shape (T,)
        Daily exposure series (e.g. temperature).
    lag_max : int
        Maximum lag in days.
    exposure_df : int
        Degrees of freedom for the exposure spline.
    lag_df : int
        Degrees of freedom for the lag spline.
    exposure_knots, lag_knots : array, optional
        Interior knot positions.

    Returns
    -------
    CB : ndarray, shape (T, exposure_df * lag_df)
    meta : CrossBasisMeta
    """
    exposure = np.asarray(exposure, dtype=float).ravel()
    T = len(exposure)
    L = lag_max + 1

    # Lag matrix
    Q = _lag_matrix(exposure, lag_max)

    # Build spline metadata from training data
    exp_spline = build_spline_meta(exposure, df=exposure_df, knots=exposure_knots)

    if lag_knots is None:
        lag_knots = _default_lag_knots(lag_max, lag_df)
    lag_positions = np.arange(L, dtype=float)
    lag_spline = build_spline_meta(lag_positions, knots=lag_knots)

    # Exposure basis for all lag-matrix values
    all_vals = Q.ravel()
    valid_mask = ~np.isnan(all_vals)
    unique_vals = np.unique(all_vals[valid_mask])
    B_x_unique = eval_spline(unique_vals, exp_spline)
    actual_exp_df = B_x_unique.shape[1]

    val_to_idx = {v: i for i, v in enumerate(unique_vals)}
    B_x_full = np.zeros((T, L, actual_exp_df))
    for t in range(T):
        for lag in range(L):
            v = Q[t, lag]
            if np.isnan(v):
                B_x_full[t, lag, :] = 0.0
            else:
                B_x_full[t, lag, :] = B_x_unique[val_to_idx[v]]

    # Lag basis
    B_l = eval_spline(lag_positions, lag_spline)
    actual_lag_df = B_l.shape[1]

    # Tensor product
    CB_3d = np.einsum("tlj,lk->tjk", B_x_full, B_l)
    CB = CB_3d.reshape(T, actual_exp_df * actual_lag_df)

    meta = CrossBasisMeta(
        exposure_df=actual_exp_df,
        lag_df=actual_lag_df,
        lag_max=lag_max,
        exposure_spline=exp_spline,
        lag_spline=lag_spline,
        exposure_range=(float(np.nanmin(exposure)), float(np.nanmax(exposure))),
    )

    return CB, meta


# ═══════════════════════════════════════════════════════════════════════
# 4. PREDICTIONS — CUMULATIVE EXPOSURE-RESPONSE
# ═══════════════════════════════════════════════════════════════════════

def _predict_basis_at_value(
    value: float,
    meta: CrossBasisMeta,
) -> np.ndarray:
    """Cross-basis row for a single exposure, summed over lags (cumulative)."""
    L = meta.lag_max + 1

    b_x = eval_spline(np.array([value]), meta.exposure_spline).ravel()
    lag_positions = np.arange(L, dtype=float)
    B_l = eval_spline(lag_positions, meta.lag_spline)
    B_l_sum = B_l.sum(axis=0)

    return np.outer(b_x, B_l_sum).ravel()


def crosspred(
    coefs: np.ndarray,
    vcov: np.ndarray,
    meta: CrossBasisMeta,
    pred_values: np.ndarray,
    centering: float,
    alpha: float = 0.05,
) -> dict:
    """Cumulative exposure-response prediction with confidence intervals."""
    z = __import__("scipy").stats.norm.ppf(1 - alpha / 2)
    pred_values = np.asarray(pred_values, dtype=float).ravel()

    row_center = _predict_basis_at_value(centering, meta)

    log_rr = np.empty(len(pred_values))
    se = np.empty(len(pred_values))

    for i, val in enumerate(pred_values):
        row_val = _predict_basis_at_value(val, meta)
        diff = row_val - row_center
        log_rr[i] = diff @ coefs
        se[i] = np.sqrt(max(diff @ vcov @ diff, 0))

    rr = np.exp(log_rr)
    rr_lower = np.exp(log_rr - z * se)
    rr_upper = np.exp(log_rr + z * se)

    return {
        "values": pred_values,
        "log_rr": log_rr,
        "rr": rr,
        "rr_lower": rr_lower,
        "rr_upper": rr_upper,
        "se": se,
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. PREDICTIONS — LAG-RESPONSE AT FIXED EXPOSURE
# ═══════════════════════════════════════════════════════════════════════

def crosspred_lag(
    coefs: np.ndarray,
    vcov: np.ndarray,
    meta: CrossBasisMeta,
    exposure_value: float,
    centering: float,
    alpha: float = 0.05,
) -> dict:
    """Lag-specific RR at a fixed exposure value."""
    z = __import__("scipy").stats.norm.ppf(1 - alpha / 2)
    L = meta.lag_max + 1

    b_x_val = eval_spline(np.array([exposure_value]),
                           meta.exposure_spline).ravel()
    b_x_cen = eval_spline(np.array([centering]),
                           meta.exposure_spline).ravel()
    b_x_diff = b_x_val - b_x_cen

    lag_positions = np.arange(L, dtype=float)
    B_l = eval_spline(lag_positions, meta.lag_spline)

    lags = np.arange(L)
    log_rr = np.empty(L)
    se = np.empty(L)

    for lag_idx in range(L):
        b_l = B_l[lag_idx, :]
        row = np.outer(b_x_diff, b_l).ravel()
        log_rr[lag_idx] = row @ coefs
        se[lag_idx] = np.sqrt(max(row @ vcov @ row, 0))

    rr = np.exp(log_rr)
    rr_lower = np.exp(log_rr - z * se)
    rr_upper = np.exp(log_rr + z * se)

    return {
        "lags": lags,
        "log_rr": log_rr,
        "rr": rr,
        "rr_lower": rr_lower,
        "rr_upper": rr_upper,
        "se": se,
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. 3D SURFACE: RR(exposure, lag)
# ═══════════════════════════════════════════════════════════════════════

def crosspred_3d(
    coefs: np.ndarray,
    vcov: np.ndarray,
    meta: CrossBasisMeta,
    pred_values: np.ndarray,
    centering: float,
) -> dict:
    """Full RR surface over (exposure, lag) grid."""
    pred_values = np.asarray(pred_values, dtype=float).ravel()
    L = meta.lag_max + 1

    lag_positions = np.arange(L, dtype=float)
    B_l = eval_spline(lag_positions, meta.lag_spline)

    b_x_cen = eval_spline(np.array([centering]),
                           meta.exposure_spline).ravel()

    rr_matrix = np.empty((len(pred_values), L))

    for i, val in enumerate(pred_values):
        b_x_val = eval_spline(np.array([val]),
                               meta.exposure_spline).ravel()
        b_x_diff = b_x_val - b_x_cen
        for lag_idx in range(L):
            b_l = B_l[lag_idx, :]
            row = np.outer(b_x_diff, b_l).ravel()
            rr_matrix[i, lag_idx] = np.exp(row @ coefs)

    return {
        "values": pred_values,
        "lags": np.arange(L),
        "rr_matrix": rr_matrix,
    }
