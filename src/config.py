"""Shared configuration: timeline, periods, dimensions, seed, paths.

Editing values here changes both the synthetic data generator and the
analysis, so the pipeline stays internally consistent.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 20200311  # WHO pandemic declaration date, used as the random seed.

# ---------------------------------------------------------------------------
# Paths (all relative to the repository root)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
IMAGES_DIR = ROOT / "docs" / "images"

# ---------------------------------------------------------------------------
# Timeline and regime cutoffs
# ---------------------------------------------------------------------------
START_DATE = "2019-06-01"
END_DATE = "2021-06-30"

# The lockdown cutoff is the discontinuity used by the regression.
LOCKDOWN_DATE = "2020-03-11"   # WHO declares COVID-19 a pandemic.
REOPENING_DATE = "2020-07-01"  # Broad, stylized reopening onset.

PERIOD_ORDER = ["pre_lockdown", "lockdown", "reopening"]
PERIOD_LABELS = {
    "pre_lockdown": "Pre-lockdown",
    "lockdown": "Lockdown",
    "reopening": "Reopening",
}

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------
CONTEXTS = ["commute", "workout", "focus_work", "relaxation", "cooking_home"]
CONTEXT_LABELS = {
    "commute": "Commute",
    "workout": "Workout",
    "focus_work": "Focus / work",
    "relaxation": "Relaxation",
    "cooking_home": "Cooking / home",
}

DEVICES = ["mobile", "desktop", "smart_speaker", "car"]
DEVICE_LABELS = {
    "mobile": "Mobile",
    "desktop": "Desktop",
    "smart_speaker": "Smart speaker",
    "car": "Car",
}

GENRES = [
    "pop",
    "hip_hop",
    "rock",
    "electronic_dance",
    "latin",
    "classical",
    "ambient_lofi",
    "country",
]
GENRE_LABELS = {
    "pop": "Pop",
    "hip_hop": "Hip-hop / R&B",
    "rock": "Rock",
    "electronic_dance": "Electronic / dance",
    "latin": "Latin",
    "classical": "Classical",
    "ambient_lofi": "Ambient / lo-fi",
    "country": "Country",
}

REGIONS = ["north_america", "europe", "latin_america", "asia_pacific"]
REGION_LABELS = {
    "north_america": "North America",
    "europe": "Europe",
    "latin_america": "Latin America",
    "asia_pacific": "Asia-Pacific",
}

DISCLAIMER = (
    "Synthetic data generated for portfolio demonstration. "
    "Not real data from any music distributor or streaming service."
)
