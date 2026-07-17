# How the pandemic reshaped music listening

**A market-research briefing for public relations and label partners**

_Generated 2026-07-17._

> **Note on the data.** Synthetic data generated for portfolio demonstration. Not real data from any music distributor or streaming service. The figures below are produced by a reproducible pipeline on a fixed random seed. They are designed to be plausible and internally consistent so they can carry a communications narrative, not to represent actual streaming volumes.

## Headline

Listening did not shrink during lockdown, it relocated. Total streaming held up (about +7.2% pre to lockdown, no collapse) while commute listening fell 74% and focus-and-home listening rose 51%.

When lockdowns began in March 2020, the question from press and partners was blunt: is the music market shrinking. The short answer is no. People kept listening just as much, but they listened in different moments, on different devices, and reached for different music. Below are six shifts, each measured against the pre-lockdown baseline and, where it matters, confirmed with a regression-discontinuity test at the lockdown date.

## 1. The market held: total streaming did not fall

Daily streaming volume moved +7.2% from the pre-lockdown baseline into the lockdown period, and stayed within a narrow band throughout. Lost listening moments (the commute, the gym) were replaced almost one for one by listening at home. The takeaway for partners: the audience did not disappear, it moved.

![Total streaming over time](../docs/images/fig_total_streams.png)

**Data behind this chart.** The chart plots total streams per day in millions. The faint line is the raw daily value from the `total_streams_millions` field, and the bold line is its 7-day centered rolling average. In a real setting this is the daily count of completed plays across the catalog, taken from streaming and distribution consumption logs.

## 2. Listening relocated from the commute and the gym to the home

The sharpest structural change was where listening happened. Commute listening fell 74% and workout listening fell 55% as a share of all streaming. That attention moved into the home: focus-and-work listening rose +51%, cooking-and-home rose +65%, and relaxation rose +9%.

![Listening context shift](../docs/images/fig_context_shift.png)

**Data behind this chart.** Each bar is the percent change in a listening context's share of streams, comparing the pre-lockdown period to the lockdown period. The inputs are the five context fields (`ctx_commute`, `ctx_workout`, `ctx_focus_work`, `ctx_relaxation`, `ctx_cooking_home`), daily shares that sum to 1 across contexts. For each context we average the daily share within each period, then report the lockdown mean minus the pre mean, divided by the pre mean. In reality the context of a session is inferred from time of day, day of week, device, motion or activity signals, and playlist or session type. See the data dictionary for what each context means.

## 3. The break was abrupt, not gradual

A regression discontinuity in time (an interrupted time series fitted around the March 11, 2020 cutoff) confirms the commute drop was a sharp level break, not a slow drift. The estimated immediate break is -14.0 percentage points of listening share (95% CI [-17.1, -10.8], p < 0.001). In plain terms: the shift happened the week lockdowns started, which is exactly the story the data lets us tell with confidence.

![Regression discontinuity for commute listening](../docs/images/fig_rdd_commute.png)

**Data behind this chart.** Points are the daily commute share of streams (the `ctx_commute` field, shown in percent) in a window from 120 days before to 111 days after the March 11, 2020 cutoff. The lines come from an interrupted-time-series fit: commute share is modeled on a time trend, a post-cutoff indicator, a post-cutoff change in slope, and weekday controls, with Newey-West standard errors that allow for day-to-day autocorrelation. The blue line is the pre-cutoff trend, the dotted line extends it as a no-lockdown counterfactual, and the red line is the fitted lockdown trend. The labeled jump is the coefficient on the post-cutoff indicator. The commute signal is inferred the same way as in the context chart above.

## 4. The car gave way to the smart speaker and the desktop

Device usage followed people home. Car listening fell -18.0 percentage points of share, while smart speakers gained +15.9 points and desktop gained +7.6 points as home and work-from-home listening grew. Mobile stayed the dominant device throughout.

![Device mix shift](../docs/images/fig_device_shift.png)

**Data behind this chart.** Bars show each device's share of streams in percent, the pre-lockdown period mean beside the lockdown period mean, with the point change labeled. The inputs are the four device fields (`dev_mobile`, `dev_desktop`, `dev_smart_speaker`, `dev_car`), daily shares that sum to 1 across devices, averaged within each period. In reality the device type is reported by the client app or SDK on each stream.

## 5. The mood cooled: calmer, slower, more somber

The emotional texture of listening changed. Average valence (a measure of musical positivity) fell from 0.58 to 0.50, and average tempo slowed from 118 to 110 BPM. The discontinuity test on valence shows a clear break at lockdown (-0.075, p < 0.001). Ambient, lo-fi, and classical listening rose while high-energy dance music receded, consistent with a shift toward focus and calm.

![Mood: valence and tempo](../docs/images/fig_mood.png)

**Data behind this chart.** Two daily metrics, each shown as a 7-day rolling average: mean valence on a 0 to 1 scale on the left axis (`mean_valence`) and mean tempo in beats per minute on the right axis (`mean_tempo_bpm`). Valence measures musical positivity, where values near 0 are somber and values near 1 are upbeat. Each field is the average across the tracks played that day, weighted by streams. In reality both come from per-track audio-analysis features joined to each play, then averaged over the day's listening.

## 6. Listeners reached for familiar catalog over new releases

Comfort listening rose. The catalog share of streams (music older than the current release window) climbed from 63.2% to 74.2% during lockdown, a break of +10.1 points (p < 0.001). This matters for release strategy and for how we frame catalog value to partners and press.

![Catalog vs new release](../docs/images/fig_catalog.png)

**Data behind this chart.** The line plots the catalog share of streams in percent as a 7-day rolling average (`catalog_share`, with `new_release_share` equal to 1 minus that value). It is the fraction of daily streams that go to catalog tracks. Catalog means a track older than 18 months since its release date, the cutoff defined in the data dictionary. In reality each play is tagged as catalog or new release by comparing the track's release date to the play date, and the catalog fraction of daily plays is taken.

## What to expect next: partial reversion, not a full rewind

As markets reopened, the shifts eased but did not fully reverse within the window studied. Recovery toward the pre-lockdown baseline was partial:

| Listening context | Lockdown change | Recovered by reopening |
| --- | ---: | ---: |
| Commute | -74% | 45% of the shift |
| Workout | -55% | 50% of the shift |
| Relaxation | +9% | 9% of the shift |
| Focus / work | +51% | 50% of the shift |
| Cooking / home | +65% | 50% of the shift |

The practical read for planning: hybrid and work-from-home listening habits proved sticky, so home, focus, and smart-speaker contexts remained structurally larger than before, even as commuting and workout listening recovered.

## Robustness: the commute drop held across regions

The commute decline was not a single-market artifact. It appears in every region studied, with magnitude varying by local lockdown stringency. The region view uses a simplified commute-versus-home split, so its baseline share is not directly comparable to the five-way context breakdown above.

| Region | Pre-lockdown commute share | Lockdown change |
| --- | ---: | ---: |
| North America | 55.4% | -51% |
| Europe | 54.1% | -57% |
| Latin America | 55.0% | -43% |
| Asia-Pacific | 53.4% | -48% |

## Data dictionary

Every field below is synthetic and generated from a fixed seed for this demonstration. Each entry states what the term means, how the synthetic value is constructed, and what real-world signal it stands in for. Where a dimension is expressed as shares, the shares sum to 1 within that dimension on each day.

**Total streams.** Field `total_streams_millions`. The daily count of completed plays across the catalog, in millions. Synthetic construction: a base level with a gentle upward trend, a weekend lift, a modest lockdown bump, and daily noise. Real-world source: aggregated play-event logs from the streaming and distribution platforms.

**Listening context.** Fields `ctx_commute`, `ctx_workout`, `ctx_focus_work`, `ctx_relaxation`, `ctx_cooking_home`. The share of a day's streams that happen in each context. Meanings:

- Commute: listening while traveling to or from work or school, usually on weekday mornings and evenings.
- Workout: listening during exercise.
- Focus or work: listening while working or studying, often instrumental or low-distraction.
- Relaxation: unwinding, calm or background listening.
- Cooking or home: listening during chores and time spent at home.

Synthetic construction: daily context shares drawn from a softmax over context-specific baselines, with weekly seasonality, a lockdown level break, and a partial reopening reversion. Real-world source: context is inferred per session from time of day, day of week, device, motion or activity signals from the phone, and playlist or session type. No single raw field carries it, so it is a modeled label rather than a logged value.

**Device.** Fields `dev_mobile`, `dev_desktop`, `dev_smart_speaker`, `dev_car`. The share of a day's streams on each device type. Categories: mobile (phone or tablet app), desktop (computer app or web player), smart speaker (a voice-controlled home speaker), and car (an in-vehicle app or dashboard integration). Synthetic construction: daily shares from a softmax with a rising smart-speaker trend and a lockdown break that moves listening off the car. Real-world source: the device type reported by the client app or SDK on each stream.

**Familiar catalog versus new release.** Fields `catalog_share` and `new_release_share`, which sum to 1. Cutoff definition: a track counts as a new release for the first 18 months after its release date, and as catalog after that. The 18-month mark is a common industry definition of catalog. The age of a track is known from the release date in its metadata, compared to the date of each play. Familiar catalog means older, established music that a listener is more likely to already know, which is why a rise in catalog share reads as a move toward comfort and familiarity. Synthetic construction: a daily catalog share modeled directly with a lockdown break and partial reversion, rather than built up from per-track release dates. Real-world source: tag each play as catalog or new release using the release-date age at play time, then take the catalog fraction of daily plays.

**Mood: valence and tempo.** Fields `mean_valence` and `mean_tempo_bpm`. Valence is a 0 to 1 measure of musical positivity, where values near 0 are somber or downbeat and values near 1 are cheerful or upbeat. Tempo is the speed of the music in beats per minute. Each field is the average across the tracks played that day, weighted by streams. Synthetic construction: daily means modeled with a lockdown dip and partial recovery plus noise. Real-world source: per-track audio-analysis features (valence and tempo computed from the audio) joined to plays and averaged over the day.

**Region and the region split.** File `region_daily.csv`, field `region` with values north_america, europe, latin_america, and asia_pacific, plus `total_streams_millions`, `commute_share`, and `home_share` for each region and day. To keep the regional view simple, this table splits listening two ways, commute versus home, where `commute_share` and `home_share` sum to 1. It does not use the five-way context breakdown, so the regional commute baseline is not directly comparable to the commute share in the context data. Synthetic construction: each region has its own commute baseline, lockdown drop, reopening pace, and market size. Real-world source: region is taken from the account country or from IP geolocation, and the commute-versus-home split follows the same context inference described above.

**Periods and cutoffs.** Field `period` with values pre_lockdown, lockdown, and reopening. Pre-lockdown runs up to the WHO pandemic declaration on 2020-03-11, lockdown runs to 2020-07-01, and reopening runs to the end of the window on 2021-06-30. These cutoffs define the before and after windows for every comparison in this report.

## Methods and limitations

**Data.** Synthetic data generated for portfolio demonstration. Not real data from any music distributor or streaming service. The synthetic panel spans 2019-06-01 to 2021-06-30 at daily resolution across listening context, device, genre, mood, catalog mix, and region. It is generated from a fixed seed so every number and chart in this report is reproducible.

**Periods.** Pre-lockdown ends at the WHO pandemic declaration (2020-03-11). The lockdown period runs to 2020-07-01, and reopening runs to the end of the window.

**Analysis.** Two methods. First, a before/after comparison of period means, reported as percentage or percentage-point changes. Second, a regression discontinuity in time (interrupted time series) fitted around the lockdown cutoff with a level term, pre and post trends, and weekday controls, using Newey-West standard errors to account for autocorrelation in daily data. The level term estimates the immediate break at lockdown.

**Limitations.** This is a demonstration on synthetic data, so the specific magnitudes are illustrative. A regression discontinuity in time attributes the break to the cutoff date, and with a single global shock it cannot fully separate the lockdown from other events coinciding with the same week. Genre and catalog definitions are simplified. A production version would use real consumption data, a proper release-window definition of catalog, seasonality controls tuned per market, and placebo cutoffs to stress-test the discontinuity.

---

_Generated 2026-07-17T06:43:29+00:00 from seed 20200311. All data synthetic, for demonstration only._
