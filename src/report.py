"""Render the PR-ready press report (outputs/press_report.md).

The report is the star deliverable: a headline, key findings each backed by a
chart, and an honest methods and limitations note. Text is generated from the
findings object so numbers always match the committed data and figures.
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import config as C

IMG = "../docs/images"  # relative path from outputs/ to the images


def _p(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def _get(rows, key, val, field):
    return next(r for r in rows if r[key] == val)[field]


def render(findings: dict) -> str:
    m = findings["meta"]
    ctx = findings["context"]
    dev = findings["device"]
    rdd = findings["rdd"]

    commute = next(r for r in ctx if r["context"] == "commute")
    workout = next(r for r in ctx if r["context"] == "workout")
    focus = next(r for r in ctx if r["context"] == "focus_work")
    cooking = next(r for r in ctx if r["context"] == "cooking_home")
    relax = next(r for r in ctx if r["context"] == "relaxation")

    car = next(r for r in dev if r["device"] == "car")
    speaker = next(r for r in dev if r["device"] == "smart_speaker")
    desktop = next(r for r in dev if r["device"] == "desktop")

    total = findings["totals"]
    catalog = findings["catalog"]
    valence = findings["mood"]["valence"]
    tempo = findings["mood"]["tempo_bpm"]

    rdd_commute = rdd["commute"]
    rdd_catalog = rdd["catalog_share"]
    rdd_valence = rdd["mean_valence"]

    lines: list[str] = []
    A = lines.append

    A("# How the pandemic reshaped music listening")
    A("")
    A("**A market-research briefing for public relations and label partners**")
    A("")
    A(f"_Generated {datetime.now(timezone.utc):%Y-%m-%d}._")
    A("")
    A("> **Note on the data.** " + m["disclaimer"] + " The figures below are "
      "produced by a reproducible pipeline on a fixed random seed. They are "
      "designed to be plausible and internally consistent so they can carry a "
      "communications narrative, not to represent actual streaming volumes.")
    A("")

    # --- Headline ----------------------------------------------------------
    A("## Headline")
    A("")
    A(findings["headline"])
    A("")
    A("When lockdowns began in March 2020, the question from press and partners "
      "was blunt: is the music market shrinking. The short answer is no. People "
      "kept listening just as much, but they listened in different moments, on "
      "different devices, and reached for different music. Below are six shifts, "
      "each measured against the pre-lockdown baseline and, where it matters, "
      "confirmed with a regression-discontinuity test at the lockdown date.")
    A("")

    # --- Finding 1 ---------------------------------------------------------
    A("## 1. The market held: total streaming did not fall")
    A("")
    A(f"Daily streaming volume moved {total['pct_change']:+.1f}% from the "
      f"pre-lockdown baseline into the lockdown period, and stayed within a "
      f"narrow band throughout. Lost listening moments (the commute, the gym) "
      f"were replaced almost one for one by listening at home. The takeaway for "
      f"partners: the audience did not disappear, it moved.")
    A("")
    A(f"![Total streaming over time]({IMG}/fig_total_streams.png)")
    A("")
    A("**Data behind this chart.** The chart plots total streams per day in "
      "millions. The faint line is the raw daily value from the "
      "`total_streams_millions` field, and the bold line is its 7-day centered "
      "rolling average. In a real setting this is the daily count of completed "
      "plays across the catalog, taken from streaming and distribution "
      "consumption logs.")
    A("")

    # --- Finding 2 ---------------------------------------------------------
    A("## 2. Listening relocated from the commute and the gym to the home")
    A("")
    A(f"The sharpest structural change was where listening happened. Commute "
      f"listening fell {abs(commute['pct_change']):.0f}% and workout listening "
      f"fell {abs(workout['pct_change']):.0f}% as a share of all streaming. That "
      f"attention "
      f"moved into the home: focus-and-work listening rose "
      f"{focus['pct_change']:+.0f}%, cooking-and-home rose "
      f"{cooking['pct_change']:+.0f}%, and relaxation rose "
      f"{relax['pct_change']:+.0f}%.")
    A("")
    A(f"![Listening context shift]({IMG}/fig_context_shift.png)")
    A("")
    A("**Data behind this chart.** Each bar is the percent change in a listening "
      "context's share of streams, comparing the pre-lockdown period to the "
      "lockdown period. The inputs are the five context fields (`ctx_commute`, "
      "`ctx_workout`, `ctx_focus_work`, `ctx_relaxation`, `ctx_cooking_home`), "
      "daily shares that sum to 1 across contexts. For each context we average "
      "the daily share within each period, then report the lockdown mean minus "
      "the pre mean, divided by the pre mean. In reality the context of a "
      "session is inferred from time of day, day of week, device, motion or "
      "activity signals, and playlist or session type. See the data dictionary "
      "for what each context means.")
    A("")

    # --- Finding 3 ---------------------------------------------------------
    A("## 3. The break was abrupt, not gradual")
    A("")
    A(f"A regression discontinuity in time (an interrupted time series fitted "
      f"around the March 11, 2020 cutoff) confirms the commute drop was a sharp "
      f"level break, not a slow drift. The estimated immediate break is "
      f"{rdd_commute['level_break']*100:+.1f} percentage points of listening "
      f"share (95% CI "
      f"[{rdd_commute['level_break_ci'][0]*100:+.1f}, "
      f"{rdd_commute['level_break_ci'][1]*100:+.1f}], "
      f"{_p(rdd_commute['level_break_pvalue'])}). In plain terms: the shift "
      f"happened the week lockdowns started, which is exactly the story the data "
      f"lets us tell with confidence.")
    A("")
    A(f"![Regression discontinuity for commute listening]({IMG}/fig_rdd_commute.png)")
    A("")
    A("**Data behind this chart.** Points are the daily commute share of streams "
      "(the `ctx_commute` field, shown in percent) in a window from 120 days "
      "before to 111 days after the March 11, 2020 cutoff. The lines come from "
      "an interrupted-time-series fit: commute share is modeled on a time "
      "trend, a post-cutoff indicator, a post-cutoff change in slope, and "
      "weekday controls, with Newey-West standard errors that allow for "
      "day-to-day autocorrelation. The blue line is the pre-cutoff trend, the "
      "dotted line extends it as a no-lockdown counterfactual, and the red line "
      "is the fitted lockdown trend. The labeled jump is the coefficient on the "
      "post-cutoff indicator. The commute signal is inferred the same way as in "
      "the context chart above.")
    A("")

    # --- Finding 4 ---------------------------------------------------------
    A("## 4. The car gave way to the smart speaker and the desktop")
    A("")
    A(f"Device usage followed people home. Car listening fell "
      f"{car['abs_change_pp']:+.1f} percentage points of share, while smart "
      f"speakers gained {speaker['abs_change_pp']:+.1f} points and desktop "
      f"gained {desktop['abs_change_pp']:+.1f} points as home and work-from-home "
      f"listening grew. Mobile stayed the dominant device throughout.")
    A("")
    A(f"![Device mix shift]({IMG}/fig_device_shift.png)")
    A("")
    A("**Data behind this chart.** Bars show each device's share of streams in "
      "percent, the pre-lockdown period mean beside the lockdown period mean, "
      "with the point change labeled. The inputs are the four device fields "
      "(`dev_mobile`, `dev_desktop`, `dev_smart_speaker`, `dev_car`), daily "
      "shares that sum to 1 across devices, averaged within each period. In "
      "reality the device type is reported by the client app or SDK on each "
      "stream.")
    A("")

    # --- Finding 5 ---------------------------------------------------------
    A("## 5. The mood cooled: calmer, slower, more somber")
    A("")
    A(f"The emotional texture of listening changed. Average valence (a measure "
      f"of musical positivity) fell from {valence['pre_mean']:.2f} to "
      f"{valence['lockdown_mean']:.2f}, and average tempo slowed from "
      f"{tempo['pre_mean']:.0f} to {tempo['lockdown_mean']:.0f} BPM. The "
      f"discontinuity test on valence shows a clear break at lockdown "
      f"({rdd_valence['level_break']:+.3f}, {_p(rdd_valence['level_break_pvalue'])}). "
      f"Ambient, lo-fi, and classical listening rose while high-energy dance "
      f"music receded, consistent with a shift toward focus and calm.")
    A("")
    A(f"![Mood: valence and tempo]({IMG}/fig_mood.png)")
    A("")
    A("**Data behind this chart.** Two daily metrics, each shown as a 7-day "
      "rolling average: mean valence on a 0 to 1 scale on the left axis "
      "(`mean_valence`) and mean tempo in beats per minute on the right axis "
      "(`mean_tempo_bpm`). Valence measures musical positivity, where values "
      "near 0 are somber and values near 1 are upbeat. Each field is the "
      "average across the tracks played that day, weighted by streams. In "
      "reality both come from per-track audio-analysis features joined to each "
      "play, then averaged over the day's listening.")
    A("")

    # --- Finding 6 ---------------------------------------------------------
    A("## 6. Listeners reached for familiar catalog over new releases")
    A("")
    A(f"Comfort listening rose. The catalog share of streams (music older than "
      f"the current release window) climbed from {catalog['pre_mean']*100:.1f}% "
      f"to {catalog['lockdown_mean']*100:.1f}% during lockdown, a break of "
      f"{rdd_catalog['level_break']*100:+.1f} points "
      f"({_p(rdd_catalog['level_break_pvalue'])}). This matters for release "
      f"strategy and for how we frame catalog value to partners and press.")
    A("")
    A(f"![Catalog vs new release]({IMG}/fig_catalog.png)")
    A("")
    A("**Data behind this chart.** The line plots the catalog share of streams "
      "in percent as a 7-day rolling average (`catalog_share`, with "
      "`new_release_share` equal to 1 minus that value). It is the fraction of "
      "daily streams that go to catalog tracks. Catalog means a track older "
      "than 18 months since its release date, the cutoff defined in the data "
      "dictionary. In reality each play is tagged as catalog or new release by "
      "comparing the track's release date to the play date, and the catalog "
      "fraction of daily plays is taken.")
    A("")

    # --- What to expect next ----------------------------------------------
    A("## What to expect next: partial reversion, not a full rewind")
    A("")
    A("As markets reopened, the shifts eased but did not fully reverse within "
      "the window studied. Recovery toward the pre-lockdown baseline was "
      "partial:")
    A("")
    A("| Listening context | Lockdown change | Recovered by reopening |")
    A("| --- | ---: | ---: |")
    for r in ctx:
        rec = r["recovery_pct_of_drop"]
        rec_txt = f"{rec:.0f}% of the shift" if rec == rec else "n/a"
        A(f"| {r['label']} | {r['pct_change']:+.0f}% | {rec_txt} |")
    A("")
    A("The practical read for planning: hybrid and work-from-home listening "
      "habits proved sticky, so home, focus, and smart-speaker contexts remained "
      "structurally larger than before, even as commuting and workout listening "
      "recovered.")
    A("")

    # --- Cross-region robustness ------------------------------------------
    A("## Robustness: the commute drop held across regions")
    A("")
    A("The commute decline was not a single-market artifact. It appears in every "
      "region studied, with magnitude varying by local lockdown stringency. The "
      "region view uses a simplified commute-versus-home split, so its baseline "
      "share is not directly comparable to the five-way context breakdown above.")
    A("")
    A("| Region | Pre-lockdown commute share | Lockdown change |")
    A("| --- | ---: | ---: |")
    for r in findings["region_commute"]:
        A(f"| {r['label']} | {r['pre_mean']*100:.1f}% | {r['pct_change']:+.0f}% |")
    A("")

    # --- Data dictionary ---------------------------------------------------
    A("## Data dictionary")
    A("")
    A("Every field below is synthetic and generated from a fixed seed for this "
      "demonstration. Each entry states what the term means, how the synthetic "
      "value is constructed, and what real-world signal it stands in for. Where "
      "a dimension is expressed as shares, the shares sum to 1 within that "
      "dimension on each day.")
    A("")
    A("**Total streams.** Field `total_streams_millions`. The daily count of "
      "completed plays across the catalog, in millions. Synthetic construction: "
      "a base level with a gentle upward trend, a weekend lift, a modest "
      "lockdown bump, and daily noise. Real-world source: aggregated play-event "
      "logs from the streaming and distribution platforms.")
    A("")
    A("**Listening context.** Fields `ctx_commute`, `ctx_workout`, "
      "`ctx_focus_work`, `ctx_relaxation`, `ctx_cooking_home`. The share of a "
      "day's streams that happen in each context. Meanings:")
    A("")
    A("- Commute: listening while traveling to or from work or school, usually "
      "on weekday mornings and evenings.")
    A("- Workout: listening during exercise.")
    A("- Focus or work: listening while working or studying, often instrumental "
      "or low-distraction.")
    A("- Relaxation: unwinding, calm or background listening.")
    A("- Cooking or home: listening during chores and time spent at home.")
    A("")
    A("Synthetic construction: daily context shares drawn from a softmax over "
      "context-specific baselines, with weekly seasonality, a lockdown level "
      "break, and a partial reopening reversion. Real-world source: context is "
      "inferred per session from time of day, day of week, device, motion or "
      "activity signals from the phone, and playlist or session type. No single "
      "raw field carries it, so it is a modeled label rather than a logged value.")
    A("")
    A("**Device.** Fields `dev_mobile`, `dev_desktop`, `dev_smart_speaker`, "
      "`dev_car`. The share of a day's streams on each device type. Categories: "
      "mobile (phone or tablet app), desktop (computer app or web player), "
      "smart speaker (a voice-controlled home speaker), and car (an in-vehicle "
      "app or dashboard integration). Synthetic construction: daily shares from "
      "a softmax with a rising smart-speaker trend and a lockdown break that "
      "moves listening off the car. Real-world source: the device type reported "
      "by the client app or SDK on each stream.")
    A("")
    A("**Familiar catalog versus new release.** Fields `catalog_share` and "
      "`new_release_share`, which sum to 1. Cutoff definition: a track counts as "
      "a new release for the first 18 months after its release date, and as "
      "catalog after that. The 18-month mark is a common industry definition of "
      "catalog. The age of a track is known from the release date in its "
      "metadata, compared to the date of each play. Familiar catalog means "
      "older, established music that a listener is more likely to already know, "
      "which is why a rise in catalog share reads as a move toward comfort and "
      "familiarity. Synthetic construction: a daily catalog share modeled "
      "directly with a lockdown break and partial reversion, rather than built "
      "up from per-track release dates. Real-world source: tag each play as "
      "catalog or new release using the release-date age at play time, then take "
      "the catalog fraction of daily plays.")
    A("")
    A("**Mood: valence and tempo.** Fields `mean_valence` and `mean_tempo_bpm`. "
      "Valence is a 0 to 1 measure of musical positivity, where values near 0 "
      "are somber or downbeat and values near 1 are cheerful or upbeat. Tempo "
      "is the speed of the music in beats per minute. Each field is the average "
      "across the tracks played that day, weighted by streams. Synthetic "
      "construction: daily means modeled with a lockdown dip and partial "
      "recovery plus noise. Real-world source: per-track audio-analysis "
      "features (valence and tempo computed from the audio) joined to plays and "
      "averaged over the day.")
    A("")
    A("**Region and the region split.** File `region_daily.csv`, field `region` "
      "with values north_america, europe, latin_america, and asia_pacific, plus "
      "`total_streams_millions`, `commute_share`, and `home_share` for each "
      "region and day. To keep the regional view simple, this table splits "
      "listening two ways, commute versus home, where `commute_share` and "
      "`home_share` sum to 1. It does not use the five-way context breakdown, so "
      "the regional commute baseline is not directly comparable to the commute "
      "share in the context data. Synthetic construction: each region has its "
      "own commute baseline, lockdown drop, reopening pace, and market size. "
      "Real-world source: region is taken from the account country or from IP "
      "geolocation, and the commute-versus-home split follows the same context "
      "inference described above.")
    A("")
    A("**Periods and cutoffs.** Field `period` with values pre_lockdown, "
      "lockdown, and reopening. Pre-lockdown runs up to the WHO pandemic "
      f"declaration on {m['cutoffs']['lockdown']}, lockdown runs to "
      f"{m['cutoffs']['reopening']}, and reopening runs to the end of the window "
      f"on {m['timeline']['end']}. These cutoffs define the before and after "
      "windows for every comparison in this report.")
    A("")

    # --- Methods -----------------------------------------------------------
    A("## Methods and limitations")
    A("")
    A("**Data.** " + m["disclaimer"] + " The synthetic panel spans "
      f"{m['timeline']['start']} to {m['timeline']['end']} at daily resolution "
      "across listening context, device, genre, mood, catalog mix, and region. "
      "It is generated from a fixed seed so every number and chart in this "
      "report is reproducible.")
    A("")
    A("**Periods.** Pre-lockdown ends at the WHO pandemic declaration "
      f"({m['cutoffs']['lockdown']}). The lockdown period runs to "
      f"{m['cutoffs']['reopening']}, and reopening runs to the end of the window.")
    A("")
    A("**Analysis.** Two methods. First, a before/after comparison of period "
      "means, reported as percentage or percentage-point changes. Second, a "
      "regression discontinuity in time (interrupted time series) fitted around "
      "the lockdown cutoff with a level term, pre and post trends, and weekday "
      "controls, using Newey-West standard errors to account for "
      "autocorrelation in daily data. The level term estimates the immediate "
      "break at lockdown.")
    A("")
    A("**Limitations.** This is a demonstration on synthetic data, so the "
      "specific magnitudes are illustrative. A regression discontinuity in time "
      "attributes the break to the cutoff date, and with a single global shock it "
      "cannot fully separate the lockdown from other events coinciding with the "
      "same week. Genre and catalog definitions are simplified. A production "
      "version would use real consumption data, a proper release-window "
      "definition of catalog, seasonality controls tuned per market, and "
      "placebo cutoffs to stress-test the discontinuity.")
    A("")
    A("---")
    A("")
    A(f"_Generated {m['generated_at']} from seed {m['seed']}. "
      "All data synthetic, for demonstration only._")
    A("")
    return "\n".join(lines)


def save_report(findings: dict, path=None) -> str:
    path = (C.OUTPUTS_DIR / "press_report.md") if path is None else path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(render(findings))
    return str(path)
