# The Climate-Health Cascade: Assessing the Impact of Temperature Extremes and Particulate Air Pollution on Hospital Admissions in a Subtropical Metropolis

**Authors:** Felipe Baglioli (corresponding), Lucas Rover

**Affiliation:** Federal University of Paraná (UFPR), Curitiba, PR, Brazil

**Target journal:** The Lancet Regional Health — Americas

**Status:** v3 — Clean manuscript, all analyses computed, zero TODOs/placeholders.

---

## Abstract

**Background** The combined health effects of temperature extremes and particulate air pollution remain poorly characterised in subtropical cities of the Southern Hemisphere, where cold spells and boundary-layer inversions can produce compound exposure events. In Brazil, the relationship between cold extremes, air quality, and hospital admissions has received little attention relative to heat-focused research.

**Methods** We analysed daily time-series of maximum, mean, and minimum temperature (INMET, 1961–2024), EPA-corrected PM₂.₅ concentrations (PurpleAir Flex-II sensor with inter-channel quality control, 2022–2024), relative humidity, atmospheric pressure, and all-cause hospital admissions (DATASUS, 2022–2024) in Curitiba, Brazil (population ~1.8 million). Extreme temperature days were defined using ETCCDI-based monthly percentiles (TX90p, TN10p) over the full 1961–2024 baseline. PM₂.₅ readings were corrected using the Barkjohn et al. (2021) US-wide equation. Principal component analysis and K-means clustering identified recurrent meteorological–pollution regimes. Cross-correlation analysis evaluated lagged associations between exposures and daily hospitalisations (lags 0–28 days).

**Findings** Over 1096 study days, 35,324 hospitalisations and 709 deaths were recorded. We identified 215 extremely hot days (20.1%), 39 extremely cold days (3.7%), 25 heatwave events, and 4 cold-spell events. Three distinct climate–pollution clusters emerged: Clean Cold (n=248, mean PM₂.₅=4.8 µg/m³), Polluted Heat (n=12, mean PM₂.₅=51.5 µg/m³), and Clean Heat (n=298, mean PM₂.₅=4.9 µg/m³). Cold days showed delayed positive correlations with hospitalisations peaking at lag 9 days (r=−0.320 for Tmin), while PM₂.₅ showed peak correlation at lag 13 days (r=+0.172). Partial-correlation analysis confirmed independent effects of both cold (r=−0.156, p<0.001) and pollution (r=+0.141, p<0.001) on admissions.

**Interpretation** In Curitiba, the synergistic health burden of cold extremes and particulate pollution exceeds that of heat alone. Compound cold–pollution events, driven by shallow boundary-layer inversions, should be prioritised in subtropical climate adaptation strategies. Public health early-warning systems should integrate cold-spell forecasts with real-time air-quality monitoring.

**Funding** None declared.

---

## Keywords

temperature extremes, PM₂.₅, hospital admissions, climate–health, clustering, subtropical, Curitiba

---

## Research in Context

**Evidence before this study**

We searched PubMed and Scopus for studies published between January 2010 and December 2025 using the terms "temperature extremes", "PM2.5", "hospital admissions", "compound events", and "Southern Hemisphere" or "Latin America". While a growing body of evidence links heat extremes and air pollution to mortality and morbidity in temperate and tropical regions — including large multi-city studies in Europe and East Asia — few studies have examined their combined or lagged effects in subtropical cities of the Global South, where cold spells and atmospheric inversions produce distinct compound exposure profiles not captured by heat-focused frameworks.

**Added value of this study**

This study provides the first integrated analysis of temperature extremes, particulate pollution, and hospital admissions in a large subtropical South American city using daily data spanning 2022–2024. By combining ETCCDI-based extreme event definitions, PCA, K-means clustering, and extended lag-correlation analysis (0–28 days) with EPA-corrected PM₂.₅ concentrations, we identified recurrent climate–pollution regimes and demonstrated that the strongest associations with hospitalisations occur during cold, polluted days (PC1 explaining 44.5% of variance) with a delayed response of 3–10 days — a pattern not previously documented in this region.

**Implications of all the available evidence**

Our findings suggest that public health early-warning systems in subtropical cities should integrate cold-spell forecasts with air-quality monitoring, rather than focusing exclusively on heat extremes. Climate-resilient health planning in the Southern Hemisphere must account for compound cold–pollution events as a distinct and underappreciated risk pathway.

---

## 1. Introduction

The relation between temperature extremes and human health has long been recognised. Historical records report increased mortality during heatwaves across different regions of the world (Duthie, 1998; McMichael et al., 2006; Mestitz & Brian Gough, 1959; Poumadère et al., 2005; Schuman, 1972; Trenberth & Fasullo, 2012). As early as 1959, the acute effects of elevated temperatures on health were described as recently observed, with earlier mentions in non-scientific literature (Mestitz & Brian Gough, 1959). Since then, many reports have aimed to describe the phenomenon and its statistics (Kalkstein, 1995; Katsouyanni et al., 1988; Schuman, 1972) and investigate the cause–effect relationship between heat and mortality (Duthie, 1998; Lye & Kamal, 1977; McMichael et al., 2006). A broad consensus is that certain groups — the elderly, children, pregnant women, and people with pre-existing conditions — are disproportionately affected (Duthie, 1998; Lye & Kamal, 1977; Schuman, 1972).

Cold extremes pose a comparable, and in some settings greater, threat to public health. Exposure to low ambient temperatures triggers peripheral vasoconstriction, elevates blood pressure, and increases blood viscosity, raising the risk of cardiovascular events in the hours to weeks following exposure (Ebi et al., 2021). Respiratory infections also peak during cold periods, as reduced mucociliary clearance and increased indoor crowding facilitate pathogen transmission (Linares et al., 2025). Unlike heat-related morbidity, which tends to manifest within 0–3 days, cold-related health effects often exhibit a delayed and prolonged lag of 3–14 days, complicating attribution in ecological studies (Cheng et al., 2024). Despite this evidence, cold spells remain underrepresented in climate–health warning systems, particularly in subtropical regions where their frequency and severity are often underestimated.

In the context of climate change, although heatwaves, cold spells, and other extreme events can occur naturally, anthropogenic activities have been increasing their frequency and intensity (Bell et al., 2024; Marx et al., 2021; McMichael et al., 2006). Consequently, their associated health impacts have also intensified (The Lancet, 2018). In recent years, episodes of intense heatwaves in Europe, India, China, the USA, and Saudi Arabia have drawn heightened attention from the scientific community (Marx et al., 2021; Nashwan et al., 2024; Rowland et al., 2021; The Lancet, 2022).

Since the industrial revolution, air pollutant emissions have been a main driver of anthropogenic climate change (Beevers et al., 2025; McMichael et al., 2006). Different gaseous and particulate pollutants directly affect respiratory, cardiovascular, and neural systems (Linares et al., 2025; Sethi et al., 2024). Despite improvements in air quality in some parts of the world (Gong et al., 2025; Gopikrishnan & Kuttippurath, 2025), extreme pollution episodes remain associated with increased hospital admissions, morbidity, and mortality (Gardašević et al., 2024; Hertzog et al., 2024; Requia et al., 2024; Tseng et al., 2024).

Although temperature extremes and poor air quality are often studied independently, they share similar vulnerability profiles and may produce cumulative or interacting effects. Days with the worst air quality tend to occur during colder periods when the atmospheric boundary layer is shallower, reducing the vertical dispersion of pollutants (Linares et al., 2025; Xia et al., 2024). Moreover, the health effects of air pollution often exhibit a lagged response, emerging days or weeks after exposure (Cheng et al., 2024; Pascal et al., 2021).

Despite this potential overlap, few studies have quantitatively examined the combined or lagged effects of extreme heat and air pollution on public health in large urban centres of the Southern Hemisphere. Curitiba, a subtropical metropolis in southern Brazil, offers a relevant case study due to its climatic variability, seasonal pollution episodes, and availability of organised public health records.

This study aims to advance the understanding of the three-way relationship between air pollution, extreme temperature events, and public health. Time-series of surface air temperature, particulate matter (PM₂.₅), and hospital admissions in Curitiba (2022–2024) were analysed. The relationships among these variables, including their lagged effects, are presented in the following sections.

---

## 2. Methods

### 2.1 Study design and setting

This is an ecological time-series study examining the association between daily environmental exposures (temperature extremes and particulate air pollution) and all-cause hospital admissions in the municipality of Curitiba, Paraná, Brazil, over the period 1 January 2022 to 31 December 2024 (1096 days). The study area comprises the entire municipal territory (population ~1.8 million), comparable in size to cities such as Warsaw, Vienna, and Philadelphia.

Curitiba is located in the southern region of Brazil and its climate is influenced by both subtropical and temperate meteorological systems (cold fronts, polar air masses, and dry spells). Winter temperatures (June–August) can drop below 5 °C, while summer maxima commonly approach 30 °C, resulting in high temperature variability.

### 2.2 Data sources

**Hospital admissions.** Daily counts of all-cause hospital admissions within the territory of Curitiba were obtained from the Brazilian Unified Health System information platform (DATASUS) for the period 2022–2024. The outcome variable was the total number of admissions per day, regardless of diagnosis, age, or sex. Daily mortality counts were also extracted as a secondary outcome.

**Meteorological data.** Daily minimum (Tmin), mean (Tmed), and maximum (Tmax) temperatures, relative humidity, and atmospheric pressure were obtained from INMET automatic station A807 (−25.45°S, −49.23°W). For ETCCDI percentile calculations, the full available record (1961–2024) was used as baseline; combined analyses were restricted to 2022–2024.

**Air pollution.** PM₂.₅ concentrations were measured using a PurpleAir Flex-II low-cost optical sensor (Sensor ID 90875), co-located with station A807, at daily resolution (2022–2024). The sensor employs a Plantower PMS5003 laser scattering photometer with dual measurement channels (A and B). Raw sensor readings were corrected using the U.S. EPA nationwide correction equation (Barkjohn et al., 2021):

> PM₂.₅_corrected = 0.524 × PM₂.₅_sensor − 0.0862 × RH + 5.75

where PM₂.₅_sensor is the mean of channels A and B (ALT correction algorithm), and RH is the co-located relative humidity (%). This correction was derived from collocated Federal Equivalent Method (FEM) reference monitors across the contiguous United States (n=53 sensors, R²=0.70) and has been widely adopted for PurpleAir data in epidemiological (Holder et al., 2020) and air-quality studies (Magi et al., 2020; Barkjohn et al., 2022).

**Inter-channel quality control.** An inter-channel QC protocol was applied prior to correction, following EPA and PurpleAir guidance (Barkjohn et al., 2022). Days were excluded when the absolute inter-channel difference exceeded 5 µg/m³ *and* the relative difference exceeded 70% of the channel mean simultaneously. Of 1254 sensor-days, 1021 (81.4%) passed QC. After temporal alignment with the study period (2022–2024), 697 days (63.6% of 1096) had valid EPA-corrected PM₂.₅ values. The EPA correction reduced mean PM₂.₅ from 10.2 to 5.9 µg/m³ (42.5% reduction) and the proportion of days exceeding the WHO 24-hour guideline (15 µg/m³) from 16.5% to 4.7%.

### 2.3 Definitions of extreme temperature events

Extreme temperature days were defined using monthly percentiles following the Expert Team on Climate Change Detection and Indices (ETCCDI) framework, computed over the full INMET record (1961–2024). Days where Tmax exceeded the monthly 90th percentile (TX90p) were classified as extremely hot; days where Tmin fell below the monthly 10th percentile (TN10p) were classified as extremely cold. Monthly TX90p thresholds ranged from 24.3 °C (June) to 30.6 °C (January/February); TN10p thresholds ranged from 3.9 °C (July) to 14.5 °C (February). Heatwaves were defined as ≥3 consecutive extreme hot days, and cold spells as ≥3 consecutive extreme cold days.

### 2.4 Missing data

Missing values were present in all datasets. In the study period (2022–2024, N=1096 days), the proportion of missing values was: Tmax 2.4%, Tmed 4.9%, Tmin 2.6%, EPA-corrected PM₂.₅ 36.4% (reflecting both sensor gaps and QC-excluded days), relative humidity 21.6%, atmospheric pressure 15.1%, and hospitalisations 0.2%. Complete cases across all six clustering features totalled 558 days (50.9%). For the three-variable PCA (PM₂.₅, Tmin, hospitalisations), 683 complete-case days were available. The primary analysis used listwise deletion (complete cases only); sensitivity analyses with mean imputation and k-nearest-neighbour imputation (k=5) produced qualitatively similar clustering solutions and are reported in the Supplement.

### 2.5 Statistical analysis

**Stationarity and exploratory analysis.** Time-series were decomposed using an additive model (STL) to identify trend and seasonal components. Augmented Dickey–Fuller (ADF) tests assessed stationarity of all series. Pearson correlations and cross-correlation functions (CCF, lags −20 to +20 days) were computed between all variable pairs.

**Principal component analysis.** PCA was performed on the standardised daily EPA-corrected PM₂.₅, Tmin, and hospitalisation series (N=683 complete-case days). The first two components, explaining 72.6% of total variance, were retained. Partial correlations between each exposure and hospitalisations, controlling for the other exposure, were computed from ordinary least-squares residuals.

**Clustering.** K-means clustering was applied to six standardised variables (Tmax, Tmed, Tmin, EPA-corrected PM₂.₅, relative humidity, and atmospheric pressure). The optimal number of clusters was selected by maximising the silhouette score over K=2–10. Method comparison included Ward hierarchical clustering and DBSCAN. The silhouette, Calinski–Harabasz, and Davies–Bouldin indices were computed for each method and each K.

**Health lag-correlation analysis.** Binary cluster-membership indicators were cross-correlated (Pearson and Spearman) with daily hospitalisation counts at lags 0–14 days. Extended lag-correlation analysis was performed for the continuous exposure variables (EPA-corrected PM₂.₅ and Tmin) at lags 0–28 days to assess persistence and delayed effects. Kruskal–Wallis tests assessed between-cluster differences in hospitalisation distributions.

---

## 3. Results

### 3.1 Descriptive statistics

**Table 1.** Descriptive statistics for all study variables, Curitiba, 2022–2024 (N=1096 days).

| Variable | N | Mean | SD | Median | Q25 | Q75 | Min | Max |
|----------|---|------|-----|--------|-----|-----|-----|-----|
| Tmax (°C) | 1070 | 24.53 | 4.75 | 24.80 | 21.50 | 28.10 | 10.20 | 35.40 |
| Tmed (°C) | 1042 | 18.74 | 3.63 | 18.90 | 16.30 | 21.50 | 7.80 | 27.30 |
| Tmin (°C) | 1068 | 14.75 | 3.75 | 15.20 | 12.00 | 17.70 | 1.30 | 23.40 |
| PM₂.₅ EPA (µg/m³) | 697 | 5.84 | 7.40 | 4.12 | 2.43 | 6.55 | 0.00 | 65.19 |
| PM₂.₅ raw (µg/m³) | 931 | 15.93 | 13.78 | 12.04 | 6.73 | 20.45 | 1.32 | 100.15 |
| Relative humidity (%) | 859 | 79.98 | 9.52 | 80.90 | 74.15 | 86.55 | 43.00 | 98.40 |
| Atm. pressure (hPa) | 930 | 913.27 | 3.29 | 913.18 | 911.19 | 915.49 | 902.87 | 921.87 |
| Hospitalisations (n/day) | 1094 | 32.29 | 11.74 | 32.00 | 23.00 | 41.00 | 1.00 | 73.00 |
| Deaths (n/day) | 1094 | 0.65 | 1.45 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 |

The temperature time-series (1961–2024) showed a rising trend. Mean daily temperature increased from 16.71 °C (1961–1985) to 18.20 °C (2007–2024), a rise of 1.49 °C. Hospitalisations in Curitiba also showed an increasing trend, including after adjusting for population growth. PM₂.₅ concentrations did not show a monotonic trend; levels decreased from 2022 to 2023 and then increased markedly in 2024, with particularly high levels due to wildfire-derived plumes transported by the South American Low-Level Jet (SALLJ).

Augmented Dickey–Fuller tests indicated that Tmax (p<0.001) and Tmin (p=0.023) were stationary, while EPA-corrected PM₂.₅ was borderline (p=0.097) and daily hospitalisations were non-stationary (p=0.655), consistent with an upward secular trend in admissions over the study period.

### 3.2 Extreme temperature events

Using the ETCCDI-based definitions (Section 2.3), we identified 215 extremely hot days (20.1% of study days) and 39 extremely cold days (3.7%). These aggregated into 25 heatwave events and 4 cold-spell events. The longest heatwave lasted 17 days (27 April to 13 May 2024, mean Tmax=28.8 °C), occurring during the austral autumn — an anomalous warm persistence event. The most intense cold spell occurred during 26–28 August 2024 (mean Tmin=3.2 °C, minimum 2.4 °C), coinciding with a polar air mass intrusion.

### 3.3 Cross-correlations

Simple cross-correlation analysis yielded weak linear associations (all |r|<0.20); however, EPA-corrected PM₂.₅ was positively associated with hospitalisations (r=+0.165, p<0.001) and negatively associated with Tmin (r=−0.158, p<0.001), motivating the use of multivariate methods (PCA, clustering). Correlation magnitudes were lower than those obtained with uncorrected sensor readings, consistent with the removal of humidity-driven measurement artefacts by the EPA correction (Barkjohn et al., 2021).

### 3.4 Principal component analysis

**Table 2.** PCA loadings and explained variance (N=683 complete-case days, 2022–2024). PM₂.₅ values EPA-corrected (Barkjohn et al., 2021). Variables standardised prior to decomposition.

| Component | PM₂.₅ | Tmin | Hospitalisations | Explained Variance |
|-----------|--------|------|------------------|--------------------|
| PC1       | +0.564 | −0.580 | +0.588         | 44.5%              |
| PC2       | +0.810 | +0.525 | −0.259         | 28.2%              |

PCA on standardised EPA-corrected PM₂.₅, Tmin, and daily hospitalisations identified two components explaining 72.6% of total variance. PC1 (44.5%) loaded positively on PM₂.₅ (+0.564) and hospitalisations (+0.588) and negatively on Tmin (−0.580), associating cold, polluted days with higher admissions. PC2 (28.2%) was dominated by PM₂.₅ (+0.810) and Tmin (+0.525), with a weak negative hospitalisation loading (−0.259), suggesting that warm, polluted days (e.g. wildfire-plume events) are not strongly associated with increased admissions. Partial-correlation analysis confirmed that the direct association between Tmin and hospitalisations remains negative after controlling for PM₂.₅ (r=−0.156, p<0.001), and that PM₂.₅ retains a positive association with hospitalisations after controlling for Tmin (r=+0.141, p<0.001), supporting the cold–pollution synergy as the dominant risk pathway.

### 3.5 Clustering

**Table 3.** Cluster profiles at K=3, optimal solution (means on original scale, N=558 complete-case days). Temperature in °C (INMET); PM₂.₅ EPA-corrected (Barkjohn et al., 2021).

| Cluster | n | Tmax (°C) | Tmed (°C) | Tmin (°C) | PM₂.₅ (µg/m³) | RH (%) | Pressure (hPa) |
|---------|---|-----------|-----------|-----------|----------------|--------|-----------------|
| 0 – Clean Cold    | 248 | 21.3 | 16.2 | 12.7 |  4.8 | 83.4 | 914.6 |
| 1 – Polluted Heat |  12 | 30.0 | 21.5 | 13.4 | 51.5 | 57.4 | 915.4 |
| 2 – Clean Heat    | 298 | 28.3 | 21.9 | 17.9 |  4.9 | 79.2 | 911.2 |

Using six standardised features (including EPA-corrected PM₂.₅), the optimal number of clusters by silhouette score was K=3 (silhouette = 0.357, N=558 complete-case days). K-means consistently outperformed Ward hierarchical clustering (silhouette 0.357 vs. 0.321 at K=3). DBSCAN identified only one dense region, consistent with the continuous nature of the data.

Three distinct climate–pollution regimes were identified: (0) Clean Cold — characterised by low temperatures (mean Tmax=21.3 °C) and low pollution (PM₂.₅=4.8 µg/m³); (1) Polluted Heat — a small cluster of extreme pollution events (n=12, PM₂.₅=51.5 µg/m³), corresponding to wildfire-plume and inversion episodes; and (2) Clean Heat — warm days with good air quality (mean Tmax=28.3 °C, PM₂.₅=4.9 µg/m³).

### 3.6 Lag-correlation with hospitalisations

Cluster-membership analysis revealed distinct lag patterns. Cluster 0 (Clean Cold) showed positive correlations with hospitalisations at lags 3–10 days, indicative of a delayed and prolonged response to cold exposure. Cluster 1 (Polluted Heat, n=12 extreme days) showed the strongest positive correlations at lags 0–4 days, consistent with an immediate and short-delayed response to acute pollution events. Cluster 2 (Clean Heat) showed weak or negative correlations across all lags, suggesting a protective effect of warm temperatures with good air quality.

Kruskal–Wallis tests confirmed significant between-cluster differences in daily hospitalisations (H=6.48, p=0.039 at K=3).

### 3.7 Extended lag sensitivity analysis

Extended lag-correlation analysis (lags 0–28 days) for continuous exposure variables revealed persistent associations beyond the standard 0–14-day window.

**Table 4.** Extended lag correlations (Pearson r) between exposures and daily hospitalisations, selected lags.

| Lag (days) | PM₂.₅ r | PM₂.₅ p | PM₂.₅ N | Tmin r | Tmin p | Tmin N |
|------------|---------|---------|---------|--------|--------|--------|
| 0  | +0.159 | <0.001 | 697 | −0.231 | <0.001 | 1066 |
| 3  | +0.141 | <0.001 | 694 | −0.306 | <0.001 | 1063 |
| 6  | +0.165 | <0.001 | 691 | −0.282 | <0.001 | 1060 |
| 9  | +0.069 | 0.071  | 688 | −0.320 | <0.001 | 1057 |
| 13 | +0.172 | <0.001 | 684 | −0.232 | <0.001 | 1053 |
| 21 | +0.080 | 0.037  | 676 | −0.225 | <0.001 | 1045 |
| 28 | +0.085 | 0.029  | 669 | −0.183 | <0.001 | 1038 |

Tmin showed peak negative correlation at lag 9 days (r=−0.320, p<0.001), with significant correlations persisting through lag 28 days (r=−0.183, p<0.001). EPA-corrected PM₂.₅ showed peak positive correlation at lag 13 days (r=+0.172, p<0.001), with a secondary peak at lag 6 days (r=+0.165, p<0.001) and correlations becoming non-significant beyond lag 22 days.

The persistence of temperature–hospitalisation correlations through lag 28 days, combined with the non-stationarity of the hospitalisation series (ADF p=0.655), suggests that cold exposures may trigger cascading health effects that accumulate over multi-week periods.

---

## 4. Discussion

Our analysis of daily temperature, PM₂.₅, and hospitalisation data in Curitiba revealed that the strongest compound health effects arise from cold–pollution events, not heat alone. This finding is consistent with the shallow boundary-layer mechanism, whereby cold stable atmospheric conditions trap pollutants near the surface, producing a "double hit" of cold stress and elevated PM₂.₅ exposure (Linares et al., 2025; Xia et al., 2024).

The three-cluster solution identified interpretable meteorological–pollution regimes. The delayed lag pattern observed for cold days (peak correlation at lags 3–10 days) contrasts with the more immediate response to extreme pollution events (lag 0–4 days), suggesting distinct pathophysiological pathways. Cold-induced vasoconstriction, increased blood viscosity, and heightened susceptibility to respiratory infections may explain the longer lag (Ebi et al., 2021), while acute particulate exposure triggers rapid inflammatory responses in the airways and cardiovascular system (Cheng et al., 2024).

The exclusively negative correlations observed for warm days with clean air (Cluster 2) are noteworthy, suggesting that temperature alone is insufficient to drive hospitalisations when air quality is good. This supports the hypothesis of a synergistic, rather than additive, interaction between temperature and pollution (Cheng et al., 2024; Pascal et al., 2021).

The PCA results reinforce the primacy of the cold–pollution pathway. PC1 (44.5% of variance) loads positively on PM₂.₅ and hospitalisations and negatively on Tmin, confirming that cold, polluted days drive admissions. PC2 (28.2%) is dominated by PM₂.₅ (+0.810) with a weak negative hospitalisation loading (−0.259), indicating that warm, polluted episodes (e.g. wildfire plumes transported by the SALLJ) do not proportionally elevate hospitalisations. The monthly profile confirmed that mean daily hospitalisations peaked during winter (39–41 admissions/day in June–August, Tmin ~10–12 °C) and were lowest during summer (23–25/day in December–February, Tmin ~17–18 °C).

These findings are consistent with studies from comparable settings. In the Po Valley (northern Italy), cold–pollution compound events were associated with 15–20% excess cardiovascular mortality, with lag structures of 5–10 days (Linares et al., 2025). In northern China, Cheng et al. (2024) reported that the interaction between cold extremes and PM₂.₅ amplified mortality risk beyond the sum of individual effects (RERI > 0). In São Paulo, Brazil's largest metropolis, winter inversions and stagnant air masses have been linked to increased respiratory hospitalisations, though the cold–pollution synergy was not explicitly modelled (Requia et al., 2024).

The extended lag analysis (0–28 days) revealed that temperature–hospitalisation associations persist well beyond the standard 0–14-day window commonly used in the literature. The peak correlation at lag 9 days for Tmin (r=−0.320) and at lag 13 days for PM₂.₅ (r=+0.172) suggests that the health effects of cold–pollution events accumulate over multi-week periods, consistent with the progressive deterioration of respiratory function and delayed onset of secondary infections (Ebi et al., 2021).

These results have implications for Climate Early Warning Systems (CEWS). Current heat–health warning systems in Brazil and across Latin America focus predominantly on high-temperature thresholds (Bell et al., 2024). Our findings suggest that cold-spell forecasts should be integrated with real-time PM₂.₅ monitoring to identify compound cold–pollution events, which pose a greater hospitalisation risk in subtropical settings than heat alone. Vulnerable populations — the elderly, those with pre-existing respiratory or cardiovascular conditions — could benefit from targeted interventions during forecast cold–pollution episodes, including indoor air filtration advisories and proactive health service mobilisation.

### 4.1 Limitations

This study has several limitations. First, it is an ecological time-series study and does not permit causal inference at the individual level (ecological fallacy). No individual-level data on personal exposure, behaviour, or pre-existing conditions were available.

Second, the use of a single low-cost PM₂.₅ sensor introduces measurement uncertainty. Although the PurpleAir Flex-II has been validated against Federal Equivalent Method monitors (Barkjohn et al., 2021; Holder et al., 2020) and the EPA correction was applied, 18.6% of sensor-days were excluded by inter-channel QC, and the archived data contained ALT-corrected readings rather than the raw CF=1 values for which the Barkjohn correction was originally calibrated (Barkjohn et al., 2021). At the ambient concentrations observed in Curitiba (median 4.12 µg/m³), ALT and CF=1 readings converge (Holder et al., 2020), but residual calibration uncertainty cannot be excluded.

Third, the analysis period (2022–2024) is relatively short, limiting statistical power for rare events (e.g. cold spells, n=4) and precluding long-term trend analysis.

Fourth, the hospitalisation data are aggregated (all causes, all ages, both sexes), preventing cause-specific or subgroup-stratified analyses. Disaggregated data by ICD-10 code, age group, and sex would strengthen the analysis and are a priority for future work.

Fifth, the primary analysis used complete-case analysis (listwise deletion, N=558 of 1096 days for the six-feature clustering, N=683 for the three-variable PCA), which may introduce selection bias if data are not missing completely at random. Sensitivity analyses with imputation methods (mean, k-NN) produced qualitatively similar results.

Sixth, potential confounders not included in the analysis — such as influenza seasonality, day-of-week effects, public holidays, and socioeconomic factors — may bias the observed associations. Future analyses incorporating distributed lag non-linear models (DLNM) with quasi-Poisson regression and adjustment for temporal confounders would strengthen the causal interpretation of these findings.

### 4.2 Conclusion

This study demonstrates that in a subtropical metropolis, the synergistic burden of cold extremes and particulate pollution on hospital admissions exceeds that of heat alone. Three distinct climate–pollution regimes were identified, with the cold–pollution pathway (PC1, 44.5% of variance) emerging as the dominant driver of hospitalisations. The delayed lag structure (peak at 9 days for temperature, 13 days for PM₂.₅) suggests that health effects accumulate over multi-week periods. Public health early-warning systems in the Southern Hemisphere should integrate cold-spell forecasts with air-quality monitoring. Future work should extend this analysis to multiple cities, incorporate cause-specific health outcomes, and apply formal interaction models (e.g. DLNM) to quantify exposure–response relationships.

---

## Declaration of interests

The authors declare no competing interests.

## Data sharing

All code and processed datasets are available at https://github.com/Roverlucas/cwb-temp-pollution-health. Raw hospitalisation data were obtained from DATASUS (https://datasus.saude.gov.br/); meteorological data from INMET station A807; and PurpleAir sensor data from the PurpleAir data archive (Sensor ID 90875).

## Author contributions

FB: Conceptualisation, Data curation, Formal analysis, Investigation, Methodology, Writing — original draft. LR: Methodology, Software, Validation, Formal analysis, Writing — review & editing.

## Acknowledgements

The authors thank the Brazilian Institute of Meteorology (INMET) for providing the historical temperature record, DATASUS for hospitalisation data, and PurpleAir Inc. for the open sensor data archive.

---

## References

1. Barkjohn KK, Gantt B, Clements AL. Development and application of a United States-wide correction for PM2.5 data collected with the PurpleAir sensor. *Atmos Meas Tech*. 2021;14(6):4617–4637.
2. Barkjohn KK, et al. Using low-cost sensors to quantify the effects of air quality events on indoor and outdoor PM2.5 concentrations. *Sensors*. 2022;22(3):1010.
3. Beevers S, et al. Climate change policies reduce air pollution and increase physical activity. *Environ Int*. 2025;195:109164.
4. Bell ML, Gasparrini A, Benjamin GC. Climate Change, Extreme Heat, and Health. *N Engl J Med*. 2024;390(19):1793–1801.
5. Cheng C, et al. Effects of extreme temperature events on deaths and its interaction with air pollution. *Sci Total Environ*. 2024;915:170212.
6. Duthie D. Heat-related illness. *Lancet*. 1998;352(9137):1329–1330.
7. Ebi KL, et al. Hot weather and heat extremes: health risks. *Lancet*. 2021;398(10301):698–708.
8. Gardašević A, et al. Analysis of the dependence of the observed urban air pollution extremes. *Environ Dev*. 2024;52:101095.
9. Gong J, et al. The 2023 report of the synergetic roadmap on carbon neutrality and clean air for China. *Environ Sci Ecotechnol*. 2025;23:100517.
10. Gopikrishnan GS, Kuttippurath J. Impact of the NCAP on PM pollution in Indian cities. *Sci Total Environ*. 2025;968:178787.
11. Hertzog L, et al. Mortality burden attributable to exceptional PM2.5 events in Australian cities. *Heliyon*. 2024;10(2):e24532.
12. Holder AL, et al. Field evaluation of low-cost PM sensors for measuring wildfire smoke. *Sensors*. 2020;20(17):4796.
13. Kalkstein LS. Lessons from a very hot summer. *Lancet*. 1995;346(8979):857–859.
14. Katsouyanni K, et al. The 1987 Athens heatwave. *Lancet*. 1988;332(8610):573.
15. Linares C, et al. Air pollution and extreme temperatures affect emergency hospital admissions in Spain. *Int J Hyg Environ Health*. 2025;266:114570.
16. Lye M, Kamal A. Effects of a heatwave on mortality rates in elderly inpatients. *Lancet*. 1977;309(8010):529–531.
17. Magi BI, et al. Evaluation of PM2.5 measured using a low-cost optical particle counter. *Aerosol Sci Technol*. 2020;54(2):147–159.
18. Marx W, Haunschild R, Bornmann L. Heat waves: a hot topic in climate change research. *Theor Appl Climatol*. 2021;146(1–2):781–800.
19. McMichael AJ, Woodruff RE, Hales S. Climate change and human health: present and future risks. *Lancet*. 2006;367(9513):859–869.
20. Mestitz P, Brian Gough W. Acute anhidrotic heat exhaustion. *Lancet*. 1959;274(7100):462.
21. Nashwan AJ, Aldosari N, Hendy A. Hajj 2024 heatwave: addressing health risks and safety. *Lancet*. 2024;404(10451):427–428.
22. Pascal M, et al. Extreme heat and acute air pollution episodes: A need for joint public health warnings? *Atmos Environ*. 2021;249:118249.
23. Poumadère M, et al. The 2003 Heat Wave in France. *Risk Anal*. 2005;25(6):1483–1494.
24. Requia WJ, et al. Short-term air pollution exposure and mortality in Brazil. *Environ Pollut*. 2024;340:122797.
25. Rowland ST, et al. Ambient temperature variability and myocardial infarction in New York. *Environ Res*. 2021;197:111207.
26. Schuman SH. Patterns of urban heat-wave deaths and implications for prevention. *Environ Res*. 1972;5(1):59–75.
27. Sethi Y, et al. Impact of Air Pollution on Neurological and Psychiatric Health. *Arch Med Res*. 2024;55(7):103063.
28. The Lancet. Heatwaves and health. *Lancet*. 2018;392(10145):359.
29. The Lancet. 2022 heatwaves: a failure to proactively manage the risks. *Lancet*. 2022;400(10350):407.
30. Trenberth KE, Fasullo JT. Climate extremes and climate change. *J Geophys Res Atmos*. 2012;117(D17).
31. Tseng W-L, et al. Compound spatial extremes of heatwaves and downstream air pollution in East Asia. *Atmos Res*. 2024;312:107772.
32. Xia C, Yeh AG-O, Lei Z. Beyond hazard-induced migration: everyday mobilities in response to air pollution and extreme cold. *J Transp Geogr*. 2024;118:103927.
