"""Analysis: before/after shifts and a regression-discontinuity in time.

Two complementary, deliberately simple and defensible methods:

1. Before/after comparison. Mean of a metric during the pre-lockdown period
   versus during the lockdown period, reported as a percentage-point or
   percentage change. Easy to read and hard to argue with.

2. Regression discontinuity in time (interrupted time series). Around the
   lockdown cutoff we fit

       y_t = b0 + b1 * t + b2 * D + b3 * (t * D) + weekday dummies + e_t

   where t is days relative to the cutoff and D = 1 on/after the cutoff. The
   coefficient b2 is the immediate level break at lockdown (the "jump"), and
   b3 is the change in trend. Standard errors use a Newey-West (HAC)
   covariance to account for autocorrelation in daily series. This mirrors the
   discontinuity-regression approach described in the project brief.

All results are computed on synthetic demonstration data.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import statsmodels.api as sm

from . import config as C


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_daily(data_dir=C.DATA_DIR) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "listening_daily.csv", parse_dates=["date"])
    return df


def load_genre(data_dir=C.DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(data_dir / "genre_shares.csv", parse_dates=["date"])


def load_region(data_dir=C.DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(data_dir / "region_daily.csv", parse_dates=["date"])


# ---------------------------------------------------------------------------
# Before/after
# ---------------------------------------------------------------------------
def period_mean(df: pd.DataFrame, col: str, period: str) -> float:
    return float(df.loc[df["period"] == period, col].mean())


def before_after(df: pd.DataFrame, col: str) -> dict:
    """Compare pre-lockdown vs lockdown, plus reopening recovery."""
    pre = period_mean(df, col, "pre_lockdown")
    lock = period_mean(df, col, "lockdown")
    reopen = period_mean(df, col, "reopening")
    return {
        "pre_mean": pre,
        "lockdown_mean": lock,
        "reopening_mean": reopen,
        "abs_change_pp": (lock - pre),            # for share metrics (points)
        "pct_change": _safe_pct(pre, lock),        # relative change
        "recovery_pct_of_drop": _recovery(pre, lock, reopen),
    }


def _safe_pct(a: float, b: float) -> float:
    return float((b - a) / a * 100.0) if a not in (0.0, None) else float("nan")


def _recovery(pre: float, lock: float, reopen: float) -> float:
    """How much of the lockdown gap had closed by the reopening period.

    100% means fully back to the pre-lockdown level, 0% means still at the
    lockdown level, >100% means it overshot.
    """
    gap = lock - pre
    if gap == 0:
        return float("nan")
    return float((reopen - lock) / (-gap) * 100.0)


# ---------------------------------------------------------------------------
# Regression discontinuity in time (interrupted time series)
# ---------------------------------------------------------------------------
def rdd_time(df: pd.DataFrame, col: str,
             cutoff: str = C.LOCKDOWN_DATE,
             pre_days: int = 120, post_days: int = 111,
             hac_lags: int = 14) -> dict:
    """Fit the interrupted-time-series model around `cutoff` for one column.

    Returns the level break (b2), slope change (b3), their standard errors,
    p-values, and the fitted lines needed to plot the discontinuity.
    """
    cut = pd.Timestamp(cutoff)
    lo = cut - pd.Timedelta(days=pre_days)
    hi = cut + pd.Timedelta(days=post_days)
    w = df[(df["date"] >= lo) & (df["date"] < hi)].copy()
    w = w.sort_values("date").reset_index(drop=True)

    t = (w["date"] - cut).dt.days.to_numpy().astype(float)
    D = (t >= 0).astype(float)
    dow = w["date"].dt.dayofweek.to_numpy()

    X = pd.DataFrame({"t": t, "D": D, "tD": t * D})
    # Weekday dummies (Mon..Sat; Sunday is the baseline) to absorb the weekly cycle.
    for d in range(1, 7):
        X[f"dow_{d}"] = (dow == d).astype(float)
    X = sm.add_constant(X)
    y = w[col].to_numpy().astype(float)

    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})

    b_const = model.params["const"]
    b_t = model.params["t"]
    b_D = model.params["D"]
    b_tD = model.params["tD"]

    # Counterfactual level just after the cutoff, had there been no break.
    pre_level_at_cut = b_const  # value at t = 0 on the pre trend (dummies = Sunday baseline)
    post_level_at_cut = b_const + b_D

    return {
        "column": col,
        "cutoff": cutoff,
        "window": [str(lo.date()), str(hi.date())],
        "n_obs": int(len(w)),
        "level_break": float(b_D),
        "level_break_se": float(model.bse["D"]),
        "level_break_pvalue": float(model.pvalues["D"]),
        "level_break_ci": [float(model.conf_int().loc["D", 0]),
                           float(model.conf_int().loc["D", 1])],
        "slope_change_per_day": float(b_tD),
        "slope_change_pvalue": float(model.pvalues["tD"]),
        "pre_slope_per_day": float(b_t),
        "pre_level_at_cutoff": float(pre_level_at_cut),
        "post_level_at_cutoff": float(post_level_at_cut),
        "r_squared": float(model.rsquared),
        # Data needed to draw the fitted pre/post lines and the raw points.
        "_plot": {
            "t": t.tolist(),
            "dates": [str(d.date()) for d in w["date"]],
            "y": y.tolist(),
            "pre_fit": (b_const + b_t * t).tolist(),
            "post_fit": (b_const + b_t * t + b_D * D + b_tD * (t * D)).tolist(),
        },
    }


# ---------------------------------------------------------------------------
# Cross-region robustness
# ---------------------------------------------------------------------------
def region_commute_shifts(region_df: pd.DataFrame) -> list[dict]:
    out = []
    for reg in C.REGIONS:
        sub = region_df[region_df["region"] == reg]
        ba = before_after(sub, "commute_share")
        out.append({
            "region": reg,
            "label": C.REGION_LABELS[reg],
            "pre_mean": ba["pre_mean"],
            "lockdown_mean": ba["lockdown_mean"],
            "abs_change_pp": ba["abs_change_pp"] * 100.0,   # percentage points
            "pct_change": ba["pct_change"],
        })
    return out


# ---------------------------------------------------------------------------
# Genre shifts
# ---------------------------------------------------------------------------
def genre_shifts(genre_df: pd.DataFrame) -> list[dict]:
    out = []
    for g in C.GENRES:
        ba = before_after(genre_df, f"genre_{g}")
        out.append({
            "genre": g,
            "label": C.GENRE_LABELS[g],
            "pre_mean": ba["pre_mean"],
            "lockdown_mean": ba["lockdown_mean"],
            "abs_change_pp": ba["abs_change_pp"] * 100.0,
            "pct_change": ba["pct_change"],
        })
    out.sort(key=lambda r: r["pct_change"])
    return out


# ---------------------------------------------------------------------------
# Assemble the full findings object
# ---------------------------------------------------------------------------
def build_findings(daily=None, genre=None, region=None) -> dict:
    daily = load_daily() if daily is None else daily
    genre = load_genre() if genre is None else genre
    region = load_region() if region is None else region

    # Context shifts (as percentage points and percent).
    context = []
    for c in C.CONTEXTS:
        ba = before_after(daily, f"ctx_{c}")
        context.append({
            "context": c,
            "label": C.CONTEXT_LABELS[c],
            "pre_mean": ba["pre_mean"],
            "lockdown_mean": ba["lockdown_mean"],
            "reopening_mean": ba["reopening_mean"],
            "abs_change_pp": ba["abs_change_pp"] * 100.0,
            "pct_change": ba["pct_change"],
            "recovery_pct_of_drop": ba["recovery_pct_of_drop"],
        })
    context.sort(key=lambda r: r["pct_change"])

    device = []
    for d in C.DEVICES:
        ba = before_after(daily, f"dev_{d}")
        device.append({
            "device": d,
            "label": C.DEVICE_LABELS[d],
            "pre_mean": ba["pre_mean"],
            "lockdown_mean": ba["lockdown_mean"],
            "abs_change_pp": ba["abs_change_pp"] * 100.0,
            "pct_change": ba["pct_change"],
        })
    device.sort(key=lambda r: r["pct_change"])

    total_ba = before_after(daily, "total_streams_millions")
    catalog_ba = before_after(daily, "catalog_share")
    valence_ba = before_after(daily, "mean_valence")
    tempo_ba = before_after(daily, "mean_tempo_bpm")

    # Regression discontinuity for every dimension. Keys use the short name for
    # contexts and devices (e.g. "commute", "car") and "genre_<g>" for genres.
    rdd = {}
    for c in C.CONTEXTS:
        rdd[c] = rdd_time(daily, f"ctx_{c}")
    for d in C.DEVICES:
        rdd[d] = rdd_time(daily, f"dev_{d}")
    for col in ("catalog_share", "mean_valence", "mean_tempo_bpm"):
        rdd[col] = rdd_time(daily, col)
    for g in C.GENRES:
        rdd[f"genre_{g}"] = rdd_time(genre, f"genre_{g}")

    findings = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "seed": C.SEED,
            "disclaimer": C.DISCLAIMER,
            "timeline": {"start": C.START_DATE, "end": C.END_DATE},
            "cutoffs": {"lockdown": C.LOCKDOWN_DATE, "reopening": C.REOPENING_DATE},
            "method": ("Before/after period comparison plus regression "
                       "discontinuity in time (interrupted time series) with "
                       "Newey-West standard errors."),
        },
        "totals": total_ba,
        "context": context,
        "device": device,
        "catalog": catalog_ba,
        "mood": {"valence": valence_ba, "tempo_bpm": tempo_ba},
        "genre": genre_shifts(genre),
        "region_commute": region_commute_shifts(region),
        "rdd": rdd,
    }
    findings["headline"] = _headline(findings)
    return findings


def _headline(f: dict) -> str:
    commute = next(r for r in f["context"] if r["context"] == "commute")
    focus = next(r for r in f["context"] if r["context"] == "focus_work")
    total_pct = f["totals"]["pct_change"]
    return (
        "Listening did not shrink during lockdown, it relocated. Total streaming "
        f"held up (about {total_pct:+.1f}% pre to lockdown, no collapse) while "
        f"commute listening fell {abs(commute['pct_change']):.0f}% and "
        f"focus-and-home listening rose {focus['pct_change']:.0f}%."
    )


def save_findings(findings: dict, path=None) -> str:
    path = (C.OUTPUTS_DIR / "findings.json") if path is None else path
    path.parent.mkdir(parents=True, exist_ok=True)
    # Strip the heavy per-point plotting arrays from the committed JSON copy so
    # it stays readable; keep the summary statistics.
    slim = json.loads(json.dumps(findings))  # deep copy
    for k in slim.get("rdd", {}):
        slim["rdd"][k].pop("_plot", None)
    with open(path, "w") as fh:
        json.dump(slim, fh, indent=2)
    return str(path)


if __name__ == "__main__":
    f = build_findings()
    p = save_findings(f)
    print("headline:", f["headline"])
    print("wrote", p)
