"""Synthetic listening-market data generator.

The goal is data with a realistic SHAPE, not real numbers: a daily streaming
market that grows slowly, breathes with the weekly cycle, and reorganizes
itself abruptly when lockdown begins, then partially reverts as things reopen.

Everything is driven by a fixed seed so the committed CSVs are reproducible.
The design deliberately builds in a genuine level break at the lockdown date
so the downstream regression-discontinuity analysis has a real effect to
recover (rather than the analysis inventing one).

All output is synthetic and for demonstration only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _softmax(logits: np.ndarray) -> np.ndarray:
    """Row-wise softmax so each day's shares sum to one."""
    z = logits - logits.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def _period_for(dates: pd.DatetimeIndex) -> np.ndarray:
    lock = pd.Timestamp(C.LOCKDOWN_DATE)
    reopen = pd.Timestamp(C.REOPENING_DATE)
    out = np.where(dates < lock, "pre_lockdown",
                   np.where(dates < reopen, "lockdown", "reopening"))
    return out


def _regime_ramp(dates: pd.DatetimeIndex, rng: np.random.Generator):
    """Return (post_lock, post_reopen) smooth 0..1 regime indicators.

    A short logistic ramp (a few days) around each cutoff is more realistic
    than an instantaneous jump and keeps the discontinuity sharp but not
    perfectly knife-edged. The analysis still treats the cutoff as a step.
    """
    day = (dates - dates[0]).days.to_numpy().astype(float)
    lock_day = (pd.Timestamp(C.LOCKDOWN_DATE) - dates[0]).days
    reopen_day = (pd.Timestamp(C.REOPENING_DATE) - dates[0]).days

    def logistic(center, width):
        return 1.0 / (1.0 + np.exp(-(day - center) / width))

    post_lock = logistic(lock_day, 4.0)
    post_reopen = logistic(reopen_day, 10.0)
    return post_lock, post_reopen


def _weekly(dow: np.ndarray, weekend_lift: float, workday_lift: float) -> np.ndarray:
    """Additive weekly pattern in logit space.

    weekend_lift raises Saturday/Sunday, workday_lift raises Mon..Fri.
    """
    is_weekend = (dow >= 5).astype(float)
    return weekend_lift * is_weekend + workday_lift * (1.0 - is_weekend)


# ---------------------------------------------------------------------------
# Component builders
# ---------------------------------------------------------------------------
def _total_streams(dates, day_norm, dow, post_lock, post_reopen, rng):
    """Daily total streams in millions.

    Total consumption is resilient: it keeps a gentle upward trend and, if
    anything, ticks up slightly during lockdown (more time at home) before
    settling. Weekend days run a little higher.
    """
    base = 100.0
    trend = 14.0 * day_norm                       # gentle secular growth over two years
    weekend = 6.0 * (dow >= 5)                     # weekends higher
    lockdown_bump = 4.0 * post_lock - 2.0 * post_reopen
    noise = rng.normal(0.0, 2.2, size=len(dates))
    total = base + trend + weekend + lockdown_bump + noise
    return np.clip(total, 1.0, None)


def _shares(labels, base, lock_delta, reopen_delta, weekly_spec,
            day_norm, dow, post_lock, post_reopen, rng, noise_sd=0.05,
            trend=None):
    """Generic softmax share builder shared by context/device/genre.

    base, lock_delta, reopen_delta, weekly_spec, trend are dicts keyed by label
    and expressed in logit space. reopen_delta is applied ON TOP of the
    lockdown state as reopening ramps in (a partial revert is a negative
    reopen_delta relative to the lockdown level).
    """
    n = len(day_norm)
    k = len(labels)
    logits = np.zeros((n, k))
    for j, name in enumerate(labels):
        col = np.full(n, base[name], dtype=float)
        col = col + lock_delta[name] * post_lock
        col = col + reopen_delta.get(name, 0.0) * post_reopen
        if trend is not None:
            col = col + trend.get(name, 0.0) * day_norm
        wl = weekly_spec.get(name, (0.0, 0.0))
        col = col + _weekly(dow, wl[0], wl[1])
        col = col + rng.normal(0.0, noise_sd, size=n)
        logits[:, j] = col
    return _softmax(logits)


def build_dataset(seed: int = C.SEED) -> dict[str, pd.DataFrame]:
    """Build every synthetic table and return them keyed by name."""
    rng = np.random.default_rng(seed)

    dates = pd.date_range(C.START_DATE, C.END_DATE, freq="D")
    n = len(dates)
    day_norm = np.linspace(0.0, 1.0, n)
    dow = dates.dayofweek.to_numpy()
    period = _period_for(dates)
    post_lock, post_reopen = _regime_ramp(dates, rng)

    # --- total streams -----------------------------------------------------
    total = _total_streams(dates, day_norm, dow, post_lock, post_reopen, rng)

    # --- listening context -------------------------------------------------
    # Commute and workout collapse at lockdown; focus/work, cooking/home and
    # relaxation absorb the freed-up listening. Reopening partially reverts.
    ctx_base = {
        "commute": 0.35, "workout": 0.10, "focus_work": 0.30,
        "relaxation": 0.55, "cooking_home": 0.25,
    }
    ctx_lock = {
        "commute": -1.35, "workout": -0.75, "focus_work": 0.55,
        "relaxation": 0.20, "cooking_home": 0.65,
    }
    # Partial revert during reopening (opposite sign, smaller magnitude).
    ctx_reopen = {
        "commute": 0.85, "workout": 0.45, "focus_work": -0.30,
        "relaxation": -0.10, "cooking_home": -0.35,
    }
    ctx_weekly = {
        "commute": (-0.25, 0.20),      # weekday commuting
        "workout": (0.15, 0.05),
        "focus_work": (-0.30, 0.20),   # weekday focus listening
        "relaxation": (0.25, -0.05),
        "cooking_home": (0.10, 0.0),
    }
    ctx_shares = _shares(C.CONTEXTS, ctx_base, ctx_lock, ctx_reopen, ctx_weekly,
                         day_norm, dow, post_lock, post_reopen, rng, noise_sd=0.05)

    # --- device ------------------------------------------------------------
    dev_base = {"mobile": 0.90, "desktop": 0.35, "smart_speaker": 0.10, "car": 0.55}
    dev_lock = {"mobile": -0.05, "desktop": 0.45, "smart_speaker": 0.70, "car": -1.20}
    dev_reopen = {"mobile": 0.03, "desktop": -0.20, "smart_speaker": -0.10, "car": 0.75}
    dev_weekly = {"car": (-0.15, 0.10), "desktop": (-0.20, 0.10)}
    dev_trend = {"smart_speaker": 0.35}  # smart speakers were rising anyway
    dev_shares = _shares(C.DEVICES, dev_base, dev_lock, dev_reopen, dev_weekly,
                         day_norm, dow, post_lock, post_reopen, rng,
                         noise_sd=0.04, trend=dev_trend)

    # --- genre -------------------------------------------------------------
    gen_base = {
        "pop": 0.60, "hip_hop": 0.55, "rock": 0.35, "electronic_dance": 0.30,
        "latin": 0.25, "classical": 0.05, "ambient_lofi": 0.10, "country": 0.20,
    }
    gen_lock = {
        "pop": -0.05, "hip_hop": -0.10, "rock": 0.05, "electronic_dance": -0.55,
        "latin": -0.15, "classical": 0.45, "ambient_lofi": 0.70, "country": 0.10,
    }
    gen_reopen = {
        "electronic_dance": 0.40, "ambient_lofi": -0.30, "classical": -0.25,
        "latin": 0.15,
    }
    gen_shares = _shares(C.GENRES, gen_base, gen_lock, gen_reopen, {},
                         day_norm, dow, post_lock, post_reopen, rng, noise_sd=0.05)

    # --- catalog vs new release -------------------------------------------
    # Comfort listening: catalog share rises during lockdown, partly reverts.
    cat_logit = (0.50
                 + 0.55 * post_lock
                 - 0.28 * post_reopen
                 + 0.15 * (dow >= 5)
                 + rng.normal(0.0, 0.05, size=n))
    catalog_share = 1.0 / (1.0 + np.exp(-cat_logit))

    # --- mood: valence and tempo ------------------------------------------
    valence = (0.58
               - 0.085 * post_lock
               + 0.050 * post_reopen
               + 0.010 * (dow >= 5)
               + rng.normal(0.0, 0.012, size=n))
    valence = np.clip(valence, 0.0, 1.0)
    tempo = (118.0
             - 8.5 * post_lock
             + 5.0 * post_reopen
             + rng.normal(0.0, 1.1, size=n))

    # --- assemble master daily table --------------------------------------
    daily = pd.DataFrame({"date": dates, "period": period})
    daily["total_streams_millions"] = np.round(total, 2)
    for j, name in enumerate(C.CONTEXTS):
        daily[f"ctx_{name}"] = np.round(ctx_shares[:, j], 5)
    for j, name in enumerate(C.DEVICES):
        daily[f"dev_{name}"] = np.round(dev_shares[:, j], 5)
    daily["catalog_share"] = np.round(catalog_share, 5)
    daily["new_release_share"] = np.round(1.0 - catalog_share, 5)
    daily["mean_valence"] = np.round(valence, 4)
    daily["mean_tempo_bpm"] = np.round(tempo, 2)

    # --- genre table -------------------------------------------------------
    genre = pd.DataFrame({"date": dates, "period": period})
    for j, name in enumerate(C.GENRES):
        genre[f"genre_{name}"] = np.round(gen_shares[:, j], 5)

    # --- region table (for cross-region robustness) -----------------------
    region = _build_region_table(dates, period, day_norm, dow,
                                 post_lock, post_reopen, rng)

    return {"daily": daily, "genre": genre, "region": region}


def _build_region_table(dates, period, day_norm, dow, post_lock, post_reopen, rng):
    """Long-format region table: each region shows the commute drop, with
    region-specific magnitude and a slightly different reopening pace."""
    n = len(dates)
    # Region-specific multipliers on the commute lockdown drop and reopening.
    reg_spec = {
        "north_america": dict(share=0.30, drop=-1.30, reopen=0.80, size=1.00),
        "europe":        dict(share=0.25, drop=-1.45, reopen=0.70, size=0.85),
        "latin_america": dict(share=0.28, drop=-1.10, reopen=0.95, size=0.60),
        "asia_pacific":  dict(share=0.22, drop=-1.20, reopen=0.90, size=0.75),
    }
    frames = []
    for reg, s in reg_spec.items():
        commute_logit = (s["share"]
                         + s["drop"] * post_lock
                         + s["reopen"] * post_reopen
                         - 0.25 * (dow >= 5)
                         + rng.normal(0.0, 0.06, size=n))
        # A compact 2-way share: commute vs everything-else-at-home.
        commute_share = 1.0 / (1.0 + np.exp(-commute_logit))
        home_share = 1.0 - commute_share
        total = (100.0 * s["size"]) + 40.0 * s["size"] * day_norm \
            + 6.0 * s["size"] * post_lock + rng.normal(0.0, 2.0, size=n)
        frames.append(pd.DataFrame({
            "date": dates,
            "region": reg,
            "period": period,
            "total_streams_millions": np.round(np.clip(total, 1.0, None), 2),
            "commute_share": np.round(commute_share, 5),
            "home_share": np.round(home_share, 5),
        }))
    return pd.concat(frames, ignore_index=True)


def save_dataset(seed: int = C.SEED, data_dir=C.DATA_DIR) -> dict[str, str]:
    """Generate and write all CSVs. Returns paths written."""
    data_dir.mkdir(parents=True, exist_ok=True)
    tables = build_dataset(seed)
    paths = {}
    filenames = {
        "daily": "listening_daily.csv",
        "genre": "genre_shares.csv",
        "region": "region_daily.csv",
    }
    for key, df in tables.items():
        path = data_dir / filenames[key]
        df.to_csv(path, index=False)
        paths[key] = str(path)
    return paths


if __name__ == "__main__":
    written = save_dataset()
    for k, v in written.items():
        print(f"wrote {k}: {v}")
