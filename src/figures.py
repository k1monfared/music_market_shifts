"""Chart generation for the press report.

Six figures, one per key finding, plus a light house style. All charts read
from the committed data and the findings object, so re-running reproduces them
exactly. No emojis, plain text labels only.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import analysis as A
from . import config as C

# ---------------------------------------------------------------------------
# House style
# ---------------------------------------------------------------------------
INK = "#1c2230"
MUTED = "#5b6472"
GRID = "#e6e8ee"
UP = "#1f7a5a"      # green for increases
DOWN = "#b5423a"    # red for decreases
ACCENT = "#2f5fb0"  # blue accent
BAND_LOCK = "#f2d9d6"
BAND_REOPEN = "#dbe7f2"

# Colorblind-safe categorical palette (Okabe-Ito subset).
CATEGORICAL = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9",
               "#D55E00", "#F0E442", "#999999"]

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 130,
    "font.size": 11,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "figure.autolayout": False,
})

LOCK = pd.Timestamp(C.LOCKDOWN_DATE)
REOPEN = pd.Timestamp(C.REOPENING_DATE)
END = pd.Timestamp(C.END_DATE)


def _period_bands(ax):
    ax.axvspan(LOCK, REOPEN, color=BAND_LOCK, alpha=0.7, zorder=0, lw=0)
    ax.axvspan(REOPEN, END, color=BAND_REOPEN, alpha=0.55, zorder=0, lw=0)
    ax.axvline(LOCK, color=DOWN, lw=1.3, ls="--", zorder=2)


def _band_legend_note(ax):
    ax.text(LOCK, ax.get_ylim()[1], "  Lockdown", color=DOWN, va="top",
            ha="left", fontsize=9, fontweight="bold")
    ax.text(REOPEN, ax.get_ylim()[1], "  Reopening", color=ACCENT, va="top",
            ha="left", fontsize=9, fontweight="bold")


def _rolling(s: pd.Series, w: int = 7) -> pd.Series:
    return s.rolling(w, center=True, min_periods=1).mean()


def _save(fig, name: str):
    C.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = C.IMAGES_DIR / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def _source_note(fig):
    fig.text(0.005, 0.005, "Synthetic data for demonstration only.",
             fontsize=8, color=MUTED, ha="left")


# ---------------------------------------------------------------------------
# 1. Total streams resilience
# ---------------------------------------------------------------------------
def fig_total_streams(daily: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(daily["date"], daily["total_streams_millions"], color="#c9ced9",
            lw=0.8, zorder=1, label="Daily")
    ax.plot(daily["date"], _rolling(daily["total_streams_millions"]),
            color=ACCENT, lw=2.2, zorder=3, label="7-day average")
    _period_bands(ax)
    ax.set_title("Total streaming stayed resilient through lockdown",
                 fontsize=14, fontweight="bold", loc="left")
    ax.set_ylabel("Streams per day (millions)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(loc="lower right", frameon=False)
    _band_legend_note(ax)
    _source_note(fig)
    return _save(fig, "fig_total_streams.png")


# ---------------------------------------------------------------------------
# 2. Listening context shift
# ---------------------------------------------------------------------------
def fig_context_shift(findings: dict) -> str:
    rows = sorted(findings["context"], key=lambda r: r["pct_change"])
    labels = [r["label"] for r in rows]
    pct = [r["pct_change"] for r in rows]
    colors = [UP if v >= 0 else DOWN for v in pct]

    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    y = np.arange(len(rows))
    ax.barh(y, pct, color=colors, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_xlabel("Change in share of listening, pre-lockdown to lockdown (%)")
    ax.set_title("Listening relocated: commute and workout down, home up",
                 fontsize=14, fontweight="bold", loc="left")
    ax.grid(axis="y", visible=False)
    for yi, v in zip(y, pct):
        ax.text(v + (1.5 if v >= 0 else -1.5), yi, f"{v:+.0f}%",
                va="center", ha="left" if v >= 0 else "right",
                fontsize=10, fontweight="bold",
                color=UP if v >= 0 else DOWN)
    xmax = max(abs(min(pct)), abs(max(pct))) * 1.25
    ax.set_xlim(-xmax, xmax)
    _source_note(fig)
    return _save(fig, "fig_context_shift.png")


# ---------------------------------------------------------------------------
# 2b. Listening context shares, before versus during lockdown
# ---------------------------------------------------------------------------
def fig_context_shares(findings: dict) -> str:
    order = ["commute", "workout", "relaxation", "focus_work", "cooking_home"]
    by_key = {r["context"]: r for r in findings["context"]}
    rows = [by_key[k] for k in order]
    labels = [r["label"] for r in rows]
    pre = [r["pre_mean"] * 100 for r in rows]
    lock = [r["lockdown_mean"] * 100 for r in rows]

    x = np.arange(len(rows))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.bar(x - w/2, pre, w, label="Before lockdown", color="#9fb0cc", zorder=3)
    ax.bar(x + w/2, lock, w, label="During lockdown", color=ACCENT, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Share of listening (%)")
    ax.grid(axis="x", visible=False)
    ax.set_title("Where listening happened, before versus during lockdown",
                 fontsize=13.5, fontweight="bold", loc="left")
    for xi, (a, b) in zip(x, zip(pre, lock)):
        delta = b - a
        sign = "−" if delta < 0 else "+"
        ax.text(xi + w/2, b + 0.6, f"{sign}{abs(delta):.1f} pts", ha="center",
                fontsize=9, fontweight="bold",
                color=UP if delta >= 0 else DOWN)
    ax.set_ylim(0, max(max(pre), max(lock)) * 1.22)
    ax.legend(loc="upper right", frameon=False, ncol=2)
    _source_note(fig)
    return _save(fig, "fig_context_shares.png")


# ---------------------------------------------------------------------------
# 3. Regression discontinuity, general reusable plot
# ---------------------------------------------------------------------------
def fig_rdd_series(findings: dict, key: str, ylabel: str, title: str,
                   filename: str, is_share: bool = True,
                   unit: str = "pts", decimals: int = 1) -> str:
    """Draw one interrupted-time-series discontinuity for `findings["rdd"][key]`.

    If `is_share` is true the series is a fraction and is scaled to percent for
    display, and the level break is reported in percentage points. Otherwise the
    raw values are plotted and the break is reported in native units.
    """
    r = findings["rdd"][key]
    p = r["_plot"]
    scale = 100.0 if is_share else 1.0
    dates = pd.to_datetime(p["dates"])
    y = np.array(p["y"]) * scale
    pre_fit = np.array(p["pre_fit"]) * scale
    post_fit = np.array(p["post_fit"]) * scale
    t = np.array(p["t"])
    pre_mask = t < 0
    post_mask = t >= 0

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter(dates[pre_mask], y[pre_mask], s=10, color="#9fb0cc",
               alpha=0.7, zorder=2, label="Daily (pre)")
    ax.scatter(dates[post_mask], y[post_mask], s=10, color="#d7a19c",
               alpha=0.7, zorder=2, label="Daily (lockdown)")
    ax.plot(dates[pre_mask], pre_fit[pre_mask], color=ACCENT, lw=2.4,
            zorder=4, label="Fitted trend, pre")
    ax.plot(dates[post_mask], post_fit[post_mask], color=DOWN, lw=2.4,
            zorder=4, label="Fitted trend, lockdown")
    # Counterfactual continuation of the pre trend.
    ax.plot(dates[post_mask], pre_fit[post_mask], color=ACCENT, lw=1.6,
            ls=":", zorder=3, label="Pre trend extrapolated")
    ax.axvline(LOCK, color=DOWN, lw=1.3, ls="--", zorder=1)

    break_val = r["level_break"] * scale
    lo, hi = [b * scale for b in r["level_break_ci"]]
    unit_txt = f" {unit}" if unit else ""
    ax.annotate(
        f"Level break at lockdown: {break_val:+.{decimals}f}{unit_txt}\n"
        f"95% CI [{lo:+.{decimals}f}, {hi:+.{decimals}f}], "
        f"p {_fmt_p(r['level_break_pvalue'])}",
        xy=(LOCK, r["post_level_at_cutoff"] * scale),
        xytext=(0.03, 0.12), textcoords="axes fraction",
        fontsize=10, color=INK,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2),
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=MUTED, lw=0.8))

    ax.set_title(title, fontsize=14, fontweight="bold", loc="left")
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(loc="upper right", frameon=False, fontsize=8.5, ncol=2)
    _source_note(fig)
    return _save(fig, filename)


def fig_rdd_commute(findings: dict) -> str:
    return fig_rdd_series(
        findings, "commute",
        ylabel="Commute share of listening (%)",
        title="Regression discontinuity: an abrupt break in commute listening",
        filename="fig_rdd_commute.png", is_share=True, unit="pts")


# ---------------------------------------------------------------------------
# 4. Device mix shift
# ---------------------------------------------------------------------------
def fig_device_shift(findings: dict) -> str:
    rows = sorted(findings["device"], key=lambda r: r["device"])
    order = ["mobile", "car", "desktop", "smart_speaker"]
    rows = sorted(rows, key=lambda r: order.index(r["device"]))
    labels = [r["label"] for r in rows]
    pre = [r["pre_mean"] * 100 for r in rows]
    lock = [r["lockdown_mean"] * 100 for r in rows]

    x = np.arange(len(rows))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.bar(x - w/2, pre, w, label="Pre-lockdown", color="#9fb0cc", zorder=3)
    ax.bar(x + w/2, lock, w, label="Lockdown", color=ACCENT, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Share of listening (%)")
    ax.grid(axis="x", visible=False)
    ax.set_title("Device mix moved from the car to smart speakers and desktop",
                 fontsize=13.5, fontweight="bold", loc="left")
    for xi, (a, b) in zip(x, zip(pre, lock)):
        delta = b - a
        ax.text(xi + w/2, b + 0.6, f"{delta:+.1f} pts", ha="center",
                fontsize=9, fontweight="bold",
                color=UP if delta >= 0 else DOWN)
    ax.set_ylim(0, max(max(pre), max(lock)) * 1.22)
    ax.legend(loc="upper right", frameon=False, ncol=2)
    _source_note(fig)
    return _save(fig, "fig_device_shift.png")


# ---------------------------------------------------------------------------
# 5. Mood: valence and tempo
# ---------------------------------------------------------------------------
def fig_mood(daily: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(9, 4.6))
    l1, = ax.plot(daily["date"], _rolling(daily["mean_valence"]), color=ACCENT,
                  lw=2.2, zorder=3, label="Valence (positivity)")
    ax.set_ylabel("Mean valence (0 = somber, 1 = upbeat)", color=ACCENT)
    ax.tick_params(axis="y", labelcolor=ACCENT)
    _period_bands(ax)

    ax2 = ax.twinx()
    l2, = ax2.plot(daily["date"], _rolling(daily["mean_tempo_bpm"]), color="#c26b1f",
                   lw=2.0, zorder=3, label="Tempo (BPM)")
    ax2.set_ylabel("Mean tempo (BPM)", color="#c26b1f")
    ax2.tick_params(axis="y", labelcolor="#c26b1f")
    ax2.grid(False)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Mood cooled during lockdown: quieter, calmer, slower",
                 fontsize=14, fontweight="bold", loc="left")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend([l1, l2], [l1.get_label(), l2.get_label()], loc="lower right",
              frameon=False)
    _source_note(fig)
    return _save(fig, "fig_mood.png")


# ---------------------------------------------------------------------------
# 6. Catalog vs new release
# ---------------------------------------------------------------------------
def fig_catalog(daily: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(9, 4.6))
    cat = _rolling(daily["catalog_share"]) * 100
    ax.plot(daily["date"], cat, color="#6a3d9a", lw=2.3, zorder=3,
            label="Catalog (older releases)")
    ax.fill_between(daily["date"], 50, cat, color="#e7ddf2", alpha=0.7, zorder=1)
    ax.axhline(50, color=MUTED, lw=1, ls=":")
    _period_bands(ax)
    ax.set_title("Listeners leaned on familiar catalog over new releases",
                 fontsize=14, fontweight="bold", loc="left")
    ax.set_ylabel("Catalog share of streams (%)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(loc="lower right", frameon=False)
    _source_note(fig)
    return _save(fig, "fig_catalog.png")


def _fmt_p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


# ---------------------------------------------------------------------------
# 3b. Featured device and context discontinuities (reuse fig_rdd_series)
# ---------------------------------------------------------------------------
def fig_rdd_car(findings: dict) -> str:
    return fig_rdd_series(
        findings, "car",
        ylabel="Car share of listening (%)",
        title="Regression discontinuity: car listening broke sharply at lockdown",
        filename="fig_rdd_car.png", is_share=True, unit="pts")


def fig_rdd_smart_speaker(findings: dict) -> str:
    return fig_rdd_series(
        findings, "smart_speaker",
        ylabel="Smart-speaker share of listening (%)",
        title="Regression discontinuity: smart-speaker listening rose at lockdown",
        filename="fig_rdd_smart_speaker.png", is_share=True, unit="pts")


def fig_rdd_focus_work(findings: dict) -> str:
    return fig_rdd_series(
        findings, "focus_work",
        ylabel="Focus / work share of listening (%)",
        title="Regression discontinuity: focus and work listening jumped at lockdown",
        filename="fig_rdd_focus_work.png", is_share=True, unit="pts")


def fig_rdd_cooking_home(findings: dict) -> str:
    return fig_rdd_series(
        findings, "cooking_home",
        ylabel="Cooking / home share of listening (%)",
        title="Regression discontinuity: cooking and home listening jumped at lockdown",
        filename="fig_rdd_cooking_home.png", is_share=True, unit="pts")


def fig_rdd_catalog(findings: dict) -> str:
    return fig_rdd_series(
        findings, "catalog_share",
        ylabel="Catalog share of streams (%)",
        title="Regression discontinuity: catalog share stepped up at lockdown",
        filename="fig_rdd_catalog.png", is_share=True, unit="pts")


def fig_rdd_valence(findings: dict) -> str:
    return fig_rdd_series(
        findings, "mean_valence",
        ylabel="Mean valence (0 = somber, 1 = upbeat)",
        title="Regression discontinuity: valence dropped at lockdown",
        filename="fig_rdd_valence.png", is_share=False, unit="", decimals=3)


# ---------------------------------------------------------------------------
# 7. Genre before/after shift
# ---------------------------------------------------------------------------
def fig_genre_shift(findings: dict) -> str:
    rows = sorted(findings["genre"], key=lambda r: r["pct_change"])
    labels = [r["label"] for r in rows]
    pct = [r["pct_change"] for r in rows]
    colors = [UP if v >= 0 else DOWN for v in pct]

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    y = np.arange(len(rows))
    ax.barh(y, pct, color=colors, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_xlabel("Change in share of listening, pre-lockdown to lockdown (%)")
    ax.set_title("Genre shift: ambient, lo-fi, and classical up, dance down",
                 fontsize=14, fontweight="bold", loc="left")
    ax.grid(axis="y", visible=False)
    for yi, v in zip(y, pct):
        ax.text(v + (1.0 if v >= 0 else -1.0), yi, f"{v:+.0f}%",
                va="center", ha="left" if v >= 0 else "right",
                fontsize=10, fontweight="bold",
                color=UP if v >= 0 else DOWN)
    xmax = max(abs(min(pct)), abs(max(pct))) * 1.30
    ax.set_xlim(-xmax, xmax)
    _source_note(fig)
    return _save(fig, "fig_genre_shift.png")


# ---------------------------------------------------------------------------
# 8. Summary of every RDD level break (diverging bars anchored at zero)
# ---------------------------------------------------------------------------
def _rdd_break_row(findings: dict, key: str, label: str, scale: float) -> dict:
    r = findings["rdd"][key]
    lo, hi = r["level_break_ci"]
    val = r["level_break"] * scale
    return {
        "label": label,
        "value": val,
        "err_low": val - lo * scale,
        "err_high": hi * scale - val,
        "p": r["level_break_pvalue"],
    }


def _draw_break_panel(ax, rows: list[dict], xlabel: str, title: str):
    y = np.arange(len(rows))[::-1]  # first row at top
    vals = [r["value"] for r in rows]
    colors = [UP if v >= 0 else DOWN for v in vals]
    xerr = np.array([[r["err_low"] for r in rows],
                     [r["err_high"] for r in rows]])
    ax.barh(y, vals, color=colors, zorder=3)
    ax.errorbar(vals, y, xerr=xerr, fmt="none", ecolor=MUTED, elinewidth=1.1,
                capsize=3, zorder=4)
    ax.axvline(0, color=INK, lw=1.2, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels([r["label"] for r in rows], fontsize=9.5)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
    ax.grid(axis="y", visible=False)
    xmax = max(abs(r["value"] - r["err_low"]) for r in rows)
    xmax = max(xmax, max(abs(r["value"] + r["err_high"]) for r in rows)) * 1.18
    ax.set_xlim(-xmax, xmax)


def fig_rdd_summary(findings: dict) -> str:
    # Share-based series in percentage points, grouped: contexts, devices,
    # catalog, then genres. Order top to bottom is the list order below.
    share_rows: list[dict] = []
    for c in C.CONTEXTS:
        share_rows.append(_rdd_break_row(findings, c, C.CONTEXT_LABELS[c], 100.0))
    for d in C.DEVICES:
        share_rows.append(_rdd_break_row(findings, d, C.DEVICE_LABELS[d], 100.0))
    share_rows.append(_rdd_break_row(findings, "catalog_share", "Catalog share", 100.0))
    for g in C.GENRES:
        share_rows.append(
            _rdd_break_row(findings, f"genre_{g}", C.GENRE_LABELS[g], 100.0))

    # Mood series in native units, one small panel each.
    valence_rows = [_rdd_break_row(findings, "mean_valence", "Valence (0 to 1)", 1.0)]
    tempo_rows = [_rdd_break_row(findings, "mean_tempo_bpm", "Tempo (BPM)", 1.0)]

    fig = plt.figure(figsize=(11.5, 8.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.15, 1.0],
                          height_ratios=[1.0, 1.0], wspace=0.35, hspace=0.45,
                          top=0.86)
    ax_share = fig.add_subplot(gs[:, 0])
    ax_val = fig.add_subplot(gs[0, 1])
    ax_tempo = fig.add_subplot(gs[1, 1])

    _draw_break_panel(
        ax_share, share_rows,
        xlabel="Level break at lockdown (percentage points of share)",
        title="Share metrics: contexts, devices, catalog, genres")
    _draw_break_panel(
        ax_val, valence_rows,
        xlabel="Level break (valence units)",
        title="Mood: valence")
    _draw_break_panel(
        ax_tempo, tempo_rows,
        xlabel="Level break (BPM)",
        title="Mood: tempo")

    # Group separators and labels on the share panel.
    n = len(share_rows)
    # boundaries after contexts (5), devices (4 more = 9), catalog (1 more = 10)
    for boundary in (len(C.CONTEXTS), len(C.CONTEXTS) + len(C.DEVICES),
                     len(C.CONTEXTS) + len(C.DEVICES) + 1):
        ypos = (n - 1 - boundary) + 0.5
        ax_share.axhline(ypos, color=GRID, lw=1.0, zorder=1)

    fig.suptitle("All regression discontinuity level breaks at the lockdown cutoff",
                 fontsize=15, fontweight="bold", x=0.02, ha="left", y=0.965)
    fig.text(0.02, 0.925,
             "Bars anchored at zero, whiskers show the 95% confidence interval. "
             "Green rose, red fell.",
             fontsize=9.5, color=MUTED, ha="left")
    _source_note(fig)
    C.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = C.IMAGES_DIR / "fig_rdd_summary.png"
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return str(path)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def generate_all(findings: dict | None = None) -> dict[str, str]:
    daily = A.load_daily()
    if findings is None:
        findings = A.build_findings(daily=daily)
    paths = {
        "total_streams": fig_total_streams(daily),
        "context_shift": fig_context_shift(findings),
        "context_shares": fig_context_shares(findings),
        "rdd_commute": fig_rdd_commute(findings),
        "rdd_car": fig_rdd_car(findings),
        "rdd_smart_speaker": fig_rdd_smart_speaker(findings),
        "rdd_focus_work": fig_rdd_focus_work(findings),
        "rdd_cooking_home": fig_rdd_cooking_home(findings),
        "rdd_catalog": fig_rdd_catalog(findings),
        "rdd_valence": fig_rdd_valence(findings),
        "device_shift": fig_device_shift(findings),
        "genre_shift": fig_genre_shift(findings),
        "rdd_summary": fig_rdd_summary(findings),
        "mood": fig_mood(daily),
        "catalog": fig_catalog(daily),
    }
    return paths


if __name__ == "__main__":
    for k, v in generate_all().items():
        print(f"wrote {k}: {v}")
