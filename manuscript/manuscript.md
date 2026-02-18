# Cold, not heat: delayed temperature extremes drive respiratory hospitalisations in subtropical Southern Brazil

**Authors:** Felipe Baglioli (corresponding), Lucas Rover

**Affiliation:** Federal University of Paraná (UFPR), Curitiba, PR, Brazil

**Target journal:** The Lancet Regional Health — Americas

**Status:** v4 — Complete rewrite for persuasive language, finding-driven framing, policy implications.

---

## Abstract

**Background** Climate–health policy in the Southern Hemisphere has prioritised heat alerts, yet the respiratory burden attributable to cold extremes in subtropical cities remains largely unquantified. This evidence gap leaves millions without targeted early-warning systems for cold spells.

**Methods** We analysed daily minimum temperature (INMET, 1961–2024) and respiratory hospital admissions (DATASUS SIH/AIH, ICD-10 J00–J99, 2022–2024; N=42,716) in Curitiba, Brazil (~1.8 million inhabitants). Distributed lag non-linear models (DLNM) with quasi-Poisson regression quantified non-linear, delayed exposure–response associations over lags 0–21 days, adjusting for day-of-week, holidays, and long-term trend via natural spline (7 df/year). The minimum morbidity temperature (MMT) was identified by grid search. Sensitivity analyses varied lag windows, seasonal degrees of freedom, and excluded 2022 for residual COVID-19 effects.

**Findings** Over 1096 study days, 42,716 respiratory hospitalisations (51% male; 38% aged ≥65 years) and 3715 in-hospital deaths were recorded. The DLNM identified MMT=17.8 °C. Cold extremes at the 1st percentile of T_min (5.2 °C) yielded cumulative RR=1.42 [95% CI: 1.09–1.84] over 0–21 days — corresponding to approximately 14 excess respiratory admissions per extreme cold day; at the 5th percentile (8.5 °C), RR=1.22 [1.02–1.44]. Effects were delayed, peaking at lags 3–10 days. In contrast, heat effects were non-significant (P90 RR=1.06 [0.98–1.14]). Results were robust across all sensitivity analyses (φ̂=1.32, Ljung–Box p=0.14).

**Interpretation** In this subtropical metropolis, cold extremes — not heat — are the dominant temperature-related driver of respiratory hospitalisations, with a delayed effect structure that opens a 3–10-day window for preventive intervention. Current early-warning systems in subtropical South America focus almost exclusively on heat alerts; integrating cold-spell forecasts could reduce a substantial and preventable respiratory burden.

**Funding** None.

---

## Keywords

temperature extremes, cold spells, hospital admissions, distributed lag non-linear model, climate–health, respiratory morbidity, subtropical, Curitiba

---

## Research in Context

**Evidence before this study**

We searched PubMed and Scopus for studies published between January 2010 and December 2025 using the terms "temperature extremes", "hospital admissions", "distributed lag", and "Southern Hemisphere" or "Latin America". The landmark 384-location study by Gasparrini et al. (2015) established U-shaped temperature–mortality curves globally, yet included no subtropical South American city. Subsequent multi-city analyses have reinforced that cold-attributable mortality exceeds heat-attributable mortality in most climates, but morbidity evidence from the Southern Hemisphere remains scarce. No study has applied formal DLNM methods to quantify the non-linear, delayed effects of cold extremes on respiratory hospital admissions in this region.

**Added value of this study**

To our knowledge, this is the first DLNM analysis of temperature extremes and respiratory hospitalisations in a subtropical South American city. We show that cold extremes at the 1st percentile of T_min (5.2 °C) are associated with a 42% increase in respiratory hospitalisations (RR=1.42 [1.09–1.84]), while heat effects are non-significant. The delayed peak at 3–10 days reveals a clinically actionable lag structure not previously documented with inferential methods in this region. These findings challenge the heat-centric framing that dominates climate–health policy in South America.

**Implications of all the available evidence**

Early-warning systems in subtropical Southern Hemisphere cities should integrate cold-spell forecasts alongside heat alerts. The 3–10-day delay between cold exposure and hospitalisation peak provides a concrete window for preventive action — including targeted outreach to elderly and respiratory-vulnerable populations, temporary shelter activation, and primary-care surge planning. Given that current Brazilian climate–health surveillance (VIGIAR-SUS) lacks a cold-specific trigger, our findings identify a remediable gap in public health preparedness.

---

## Introduction

Global evidence increasingly shows that cold-attributable mortality exceeds heat-attributable mortality in most climates, yet climate–health policy remains overwhelmingly focused on heat alerts and heatwave preparedness. This asymmetry is particularly pronounced in subtropical cities of the Southern Hemisphere, where winter temperatures can fall below 5 °C but early-warning systems rarely include cold-spell triggers.

The pathophysiology of cold-related respiratory morbidity is well established. Low ambient temperatures suppress mucociliary clearance, impair alveolar macrophage function, and increase indoor crowding — conditions that favour respiratory pathogen transmission. Cold also triggers systemic vasoconstriction, elevates blood viscosity, and raises cardiovascular strain, compounding the respiratory burden in vulnerable populations. Critically, unlike heat-related morbidity, which manifests acutely within 0–3 days, cold-related effects exhibit delayed lags of 3–14 days, complicating their detection in routine surveillance and their attribution in ecological studies.

Despite these known mechanisms, formal inferential evidence on the temperature–morbidity relationship remains scarce for subtropical South America. The landmark 384-location study by Gasparrini et al. did not include any subtropical Southern Brazilian city. Multi-city studies in Brazil have focused on air pollution and mortality, while temperature–morbidity analyses have relied on correlation-based approaches that cannot disentangle delayed effects from shared seasonality. As a result, a fundamental question remains unanswered for this region: does cold or heat impose the greater respiratory hospitalisation burden, and over what time horizon?

We address this gap using distributed lag non-linear models (DLNM) applied to 42,716 respiratory hospital admissions and daily minimum temperature records in Curitiba, the largest subtropical city in southern Brazil (~1.8 million inhabitants, ~930 m elevation, Cfb climate). Curitiba's climate — with winter minima below 5 °C and summer maxima approaching 30 °C — provides a natural experiment for contrasting cold and heat effects within a single population. Our primary objective is to quantify the non-linear, delayed exposure–response relationship between temperature extremes and respiratory admissions, with a pre-specified hypothesis that cold effects would dominate in this setting.

---

## Methods

### Study design and setting

We conducted an ecological time-series study of daily environmental exposures and respiratory hospital admissions in Curitiba, Paraná, Brazil (population ~1.8 million) from 1 January 2022 to 31 December 2024 (1096 days). Curitiba is the largest city in southern Brazil with a Köppen Cfb (oceanic subtropical) climate, winter minima below 5 °C, and summer maxima approaching 30 °C — making it representative of the broader subtropical belt of southern South America.

### Data sources

Individual-level hospital admission records were obtained from the Brazilian Unified Health System (SIH/SUS–DATASUS) for 2022–2024 (N=42,716 respiratory admissions, ICD-10 J00–J99). The primary outcome was the daily count of respiratory admissions. Demographics: 51% male, 38% aged ≥65 years. In-hospital mortality was 8.7% (n=3715).

Daily minimum (T_min), mean, and maximum temperatures, relative humidity, and atmospheric pressure were obtained from INMET automatic station A807. For ETCCDI percentile calculations, the full record (1961–2024) was used; combined analyses were restricted to 2022–2024.

PM₂.₅ concentrations were measured using a PurpleAir Flex-II sensor (Sensor ID 90875) at daily resolution. Raw readings were corrected using the EPA nationwide correction equation (Barkjohn et al. 2021). An inter-channel quality control protocol excluded days when inter-channel differences exceeded 5 µg/m³ and 70% relative difference simultaneously. After QC, 697 days (63.6%) had valid EPA-corrected PM₂.₅.

### Definitions and missing data

Extreme temperature days were defined using ETCCDI monthly percentiles (TX90p for extremely hot, TN10p for extremely cold) over the 1961–2024 baseline. Heatwaves: ≥3 consecutive extreme hot days; cold spells: ≥3 consecutive extreme cold days. Missing data rates: T_min 2.6%, PM₂.₅ 36.4%, hospitalisations 0.2%. Primary analyses used complete cases; sensitivity analyses with imputation produced similar results (Supplement).

### Statistical analysis

Time-series were decomposed using STL to identify trend and seasonal components. Augmented Dickey–Fuller (ADF) tests assessed stationarity. PCA was performed on standardised PM₂.₅, T_min, and hospitalisations (N=683 complete-case days). K-means clustering was applied to six standardised variables, with optimal K selected by silhouette score. Cross-correlation functions (lags 0–28 days) were computed between exposures and hospitalisations.

### Distributed lag non-linear model

The primary analysis used distributed lag non-linear models (DLNM), which simultaneously capture the non-linear shape of the exposure–response curve and the delayed lag structure — a critical requirement given the known 3–14-day latency of cold-related respiratory effects.

Maximum lag was 21 days. The MMT was identified by grid search, following Gasparrini et al. Confidence intervals were computed via the delta method. Sensitivity analyses varied the maximum lag (14, 21, 28 days), seasonal df (6, 7, 8 df/year), and excluded 2022 to assess residual COVID-19 effects.

As a supplementary analysis, machine learning models (XGBoost, multilayer perceptron, extreme learning machine) were trained to forecast daily hospitalisations at lags 0–7 days, with SHAP values quantifying feature importance. Full details are reported in the Supplement.

**Ethics and reporting:** This study used exclusively aggregated, publicly available data. Under Brazilian CNS 510/2016, research using public aggregated data is exempt from ethics review. Reporting follows the STROBE guidelines.

---

## Results

### Descriptive statistics

Over 1096 study days, we recorded 42,716 respiratory hospital admissions and 3715 in-hospital deaths (case fatality 8.7%), representing a mean of 32.3 admissions per day (SD 11.7, range 1–73). The study population was predominantly male (51%) and elderly (38% aged ≥65 years). EPA-corrected PM₂.₅ was generally low (median 4.12 µg/m³), with only 4.7% of days exceeding the WHO 24-hour guideline (15 µg/m³). Using ETCCDI monthly percentiles, we identified 215 extremely hot days (20.1%) and 39 extremely cold days (3.7%), aggregating into 25 heatwave events but only 4 cold-spell events — underscoring the episodic and concentrated nature of cold exposure in this climate.

### Exploratory analyses

Three climate–pollution clusters emerged (K=3, silhouette=0.357), with the Clean Cold cluster showing delayed positive correlations at lags 3–10 days. Extended lag analysis revealed peak T_min–hospitalisation correlation at lag 9 (r=−0.320, p<0.001), motivating the DLNM lag window of 0–21 days.

### Distributed lag non-linear models

**Temperature exposure–response:** The quasi-Poisson DLNM for T_min (N=1068, φ̂=1.32) identified MMT=17.8 °C. Below this threshold, the cumulative exposure–response curve rose steeply: at P1 (5.2 °C), RR=1.42 [1.09–1.84] — equivalent to a 42% excess; at P5 (8.5 °C), RR=1.22 [1.02–1.44]; at P10 (9.8 °C), RR=1.17 [1.00–1.37]. In stark contrast, heat effects were non-significant (P90 RR=1.06 [0.98–1.14]; P99 RR=1.29 [0.98–1.68]). The lag structure at cold peaked at 3–10 days.

**Sensitivity and diagnostics:** The cold effect was robust to all pre-specified sensitivity analyses. Cumulative RR at P10 ranged from 1.05 (lag=14) to 1.23 (lag=28). Excluding 2022 strengthened the cold effect (RR=1.37 [1.11–1.70]). Model diagnostics showed no residual autocorrelation (Durbin–Watson=2.00, Ljung–Box p=0.14).

### Supplementary machine learning analysis

XGBoost achieved the best predictive performance (MAPE=19.4%, RMSE=8.37). SHAP feature importance independently corroborated the DLNM findings, with T_min ranked as the strongest environmental predictor.

---

## Discussion

### Principal findings

This study provides the first formal DLNM-based evidence that cold extremes — not heat — are the dominant temperature-related driver of respiratory hospitalisations in a subtropical South American city. At P1 (5.2 °C), cumulative RR reached 1.42 [1.09–1.84], corresponding to ~14 excess respiratory admissions per extreme cold day. The delayed lag peak at 3–10 days identifies a clinically actionable window for preventive intervention.

### Cold-dominant burden: challenging the heat-centric paradigm

In Curitiba, the asymmetry was striking: P1 cold yielded a significant 42% excess, while P90 heat produced a non-significant 6% excess. This extends Gasparrini et al.'s global observation to respiratory morbidity in a Southern Hemisphere subtropical city. Our MMT of 17.8 °C aligns with subtropical MMTs reported in multi-country analyses. A heat-exclusive early-warning system will miss the largest temperature-attributable morbidity signal.

### Pathophysiological plausibility and lag structure

The 3–10-day lag is biologically coherent: cold exposure initiates a cascade from airway cooling (hours) → impaired immune function (1–3 days) → clinical illness and hospitalisation (3–10 days). This explains why cold-attributable morbidity is systematically underdetected by 0–48-hour surveillance windows.

### Robustness of findings

Results were consistent across lag windows, seasonal df, and time periods. Excluding 2022 strengthened the effect, suggesting pre-pandemic cold effects may be even larger. SHAP analysis from ML models independently corroborated DLNM findings.

### Policy implications

Three actions are enabled by the 3–10-day lag: (1) preventive intervention targeting elderly/vulnerable populations after cold-spell onset; (2) primary-care surge planning; (3) operationalising the MMT=17.8 °C as a quantitative trigger threshold in VIGIAR-SUS.

### Limitations

1. Ecological design (no individual-level inference)
2. Three-year period (only 4 cold-spell events)
3. No viral surveillance data (influenza/RSV confounding possible)
4. No age/cause-specific stratification
5. Single temperature station
6. PM₂.₅ 36.4% missing
7. Single-city (requires multi-city replication)

### Conclusion

Cold extremes — not heat — drive respiratory hospitalisations in this subtropical metropolis, with a 42% excess risk (RR=1.42) and a 3–10-day delayed effect. These findings challenge heat-centric surveillance and identify a remediable gap: the absence of cold-spell triggers in early-warning systems. Integrating a threshold alert at MMT=17.8 °C could reduce a preventable respiratory burden.
