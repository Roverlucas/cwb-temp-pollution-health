# The Climate-Health Cascade: Assessing the Impact of Temperature Extremes and Particulate Air Pollution on Hospital Admissions

**Authors:** Felipe Baglioli, Lucas Rover, et al.

**Target journal:** The Lancet Regional Health — Americas

**Status:** Under revision — see [`review/PLANO_REVISAO_LANCET.md`](../review/PLANO_REVISAO_LANCET.md) for the full action plan.

---

<!-- TODO [C2]: O manuscrito .docx tinha dois abstracts (informal + formal). Manter apenas o estruturado abaixo. -->

## Abstract

<!-- TODO [STROBE item 2]: Abstract precisa ser estruturado no formato Lancet (Background / Methods / Findings / Interpretation, max 300 palavras). Redigir após análises reais estarem prontas. -->

*Abstract a ser redigido após conclusão das análises (Fase 4 do plano de revisão).*

---

## Introduction

The relation between temperature extremes and human health has long been recognized. Historical records report increased mortality during heatwaves across different regions of the world (DUTHIE, 1998; MCMICHAEL; WOODRUFF; HALES, 2006; MESTITZ; BRIAN GOUGH, 1959; POUMADÈRE et al., 2005; SCHUMAN, 1972; TRENBERTH; FASULLO, 2012). As early as 1959, the acute effects of elevated temperatures on health were already described as recently observed, with even earlier mentions in nonscientific literature (MESTITZ; BRIAN GOUGH, 1959). Since then, many other reports can be found on the subject, both aiming to describe the phenomena and its statistics (KALKSTEIN, 1995; KATSOUYANNI et al., 1988; SCHUMAN, 1972), and investigate cause effect relationship between heat and mortality (DUTHIE, 1998; LYE; KAMAL, 1977; MCMICHAEL; WOODRUFF; HALES, 2006). In general, the main consensus was the fact that some groups are more susceptible to be badly affected, with many authors highlighting the impacts on the elderly and children, as well as pregnant women and people with preexisting illnesses (DUTHIE, 1998; LYE; KAMAL, 1977; SCHUMAN, 1972).

<!-- TODO [C4]: Placeholder do autor — escrever parágrafo sobre coldwaves -->
> **[PLACEHOLDER]** Mesmo paragrafo mas para coldwaves

In the context of climate change, it is understood that although heatwaves, coldwaves and other extreme events can occur naturally, anthropogenic activities have been increasing their frequency and intensity (BELL; GASPARRINI; BENJAMIN, 2024; MARX; HAUNSCHILD; BORNMANN, 2021; MCMICHAEL; WOODRUFF; HALES, 2006). Consequently, their associated impacts have also been intensified over time (THE LANCET, 2018). In recent years, episodes of intense heatwaves in Europe, India, China, USA and Saudi Arabia have drawn heightened attention from the scientific community (MARX; HAUNSCHILD; BORNMANN, 2021; NASHWAN; ALDOSARI; HENDY, 2024; ROWLAND et al., 2021; THE LANCET, 2022). On the other hand, coldwaves have also been reported in ...

Since the industrial revolution, one of the main drivers of anthropogenic climate change has been the emission of air pollutants (BEEVERS et al., 2025; MCMICHAEL; WOODRUFF; HALES, 2006). Given what was presented above regarding heat extremes, one can infer that air pollution has an indirect impact on human health. In addition, different gaseous and particulate pollutants have been described to directly affect respiratory, cardiovascular and neural systems of exposed humans (LINARES et al., 2025; SETHI et al., 2024). Despite improvements in air quality in some parts of the world (GONG et al., 2025; GOPIKRISHNAN; KUTTIPPURATH, 2025), extreme pollution episodes still occur and are associated with increased hospital admissions, morbidity, and mortality (GARDAŠEVIĆ et al., 2024; HERTZOG et al., 2024; REQUIA et al., 2024; TSENG et al., 2024). As with heatwaves, vulnerable groups are more acutely affected by poor air quality (HERTZOG et al., 2024; LINARES et al., 2025; NASHWAN; ALDOSARI; HENDY, 2024).

<!-- TODO [C4]: "falta citar algo aqui" — adicionar referência sobre dias mais poluídos não serem os mais quentes -->
Although temperature extremes and poor air quality are often studied independently, they share similar vulnerability profiles and may produce cumulative or interacting effects. Notably, days with the worst air quality are not usually the hottest. They tend to occur in winter or during colder periods when the atmospheric boundary layer is shallower, reducing the vertical dispersion of pollutants (LINARES et al., 2025; XIA; YEH; LEI, 2024). Moreover, unlike heatwaves, the health effects of air pollution often exhibit a lagged response, emerging days or even weeks after exposure (CHENG et al., 2024; PASCAL et al., 2021).

Despite this potential overlap, few studies have quantitatively examined the combined or lagged effects of extreme heat and air pollution on public health, particularly in large urban centers of the Southern Hemisphere. Curitiba, a subtropical metropolis in southern Brazil, offers a relevant case study due to its climatic variability, seasonal pollution episodes, and availability of organized public health records.

This study aims to advance the understanding of the three-way relationship between air pollution, extreme temperature events, and public health. To this end, time-series of surface air temperature, particulate matter (PM2.5), and hospital admissions in the city of Curitiba (2021-2024) were analyzed. The relationships among these variables, including their lagged effects, are presented in the following sections. By addressing this interaction in a subtropical urban context, the findings contribute to a growing body of evidence necessary for climate-resilient public health strategies.

---

## Methods

### Study Area

<!-- TODO [C4]: "da pra por uma ref ou algo, nao sei" — adicionar referência ao DATASUS -->
To address the proposed problem, three different datasets were needed: hospitalization, atmospheric pollution, and surface air temperature. Considering the former, Brazil's national health system (SUS) provides timeseries of hospitalizations by city, in a daily frequency, via a system referred to as DATASUS. To ensure a dataset with consistent and expressive values, the city of Curitiba, capital of the state of Parana, was chosen as the focal point of the study.

This city, located in the southern region of Brazil, is one of the largest by population in the country. With circa 1.8 million inhabitants, its population is comparable to cities such as Warsaw, Vienna and Philadelphia. Also, when compared to other large Brazilian cities, Curitiba's climate is more temperate, even though the proximity to the southern tropic is relevant. In this way, the municipality's climate is affected by both subtropical and temperate meteorological systems, e.g. cold fronts, polar masses, and dry spells. During winter (June to August), the influence of subtropical climate can drop temperatures down to 5°C and below, and it is not uncommon for dry and cold days to happen. In contrast, temperatures during summer are commonly closer to 30°C, elucidating the high amplitude of temperature variability in the region.

In the city, climate data is recorded by a series of pluviometers and meteorological stations. In the present study, the temperature information was obtained from a meteorological station located at -25.45, -49.23. An atmospheric pollution sensor (PurpleAir Flex-II) was also placed at this location, aiming to ensure spatial alignment of pollution and meteorological data. More information regarding these measurements, as well as the hospitalizations timeseries, can be found in the next subsections.

### Datasets and Definitions

As aforementioned, three datasets containing public health, meteorological and atmospheric pollution data were used during the study. For public health data, the number of total hospitalizations was selected as the response indicator to extreme pollution and climate events. In this regard, the time series used to represent public health was taken from DATASUS, considering total daily hospitalizations within the territory of Curitiba, for the period 2021 to 2024.

Meterological data was obtained from an automatic station code A807, located at -25.45, -49.23, operated by INMET. Variables used were temperature (minimum, mean and maximum), relative humidity and air pressure, all measured at ground level. For the definition of descriptive statistics such as mean values, standard deviation, and quartiles, the series were considered in their full available length, from 1961 to 2024. However, when combining with other information, the period considered was 2021 to 2024.

In order to select extreme temperature events, a method involving quartiles was applied. Considering month-wide daily temperature series, 90% and 10% quartiles (Q90 for maximum temperatures and Q10 for minimum temperatures, respectively) were calculated and considered thresholds for extreme temperature days. That is, days where the maximum temperature recorded was higher than Q95 for the considered month were considered extremely hot days. Analogously, days with minimum temperatures under Q1 for the considered month were considered extremely cold days. For heatwaves and coldwaves definition, an event of at least 3 consecutive extreme temperature days was considered.

Lastly, atmospheric pollution data was collected at the same point as meteorological station A807, using a low-cost sensor PurpleAir Flex-II. This sensor uses optical measurements to estimate Particulate Matter (PM) concentrations. During prior analysis, both the coarser fraction (PM10) and the finer fraction (PM2.5) of PM were evaluated. However, in further explorations, it was chosen to consider only PM2.5, given the importance of that fraction for pollution effects on human health. As well as for the hospitalization time series, the collected air quality data spanned from 2021 to 2024, with daily frequency.

It is important to report that, even though data collection was conducted to the best capabilities, some missing values were found in all three datasets. For this reason, data inputting techniques were applied, ensuring temporal completeness for the studied period (2021-2024). This inputting was performed by ...

<!-- TODO [C4]: Placeholder do autor -->
> **[PLACEHOLDER]** Delinear a tecnica de input de dados

<!-- TODO [Auditoria item 2]: O manuscrito descreve MICE com PMM (5 datasets, Rubin's rules), mas o notebook usa dropna. Alinhar texto com realidade. -->

### Analysis

A preliminary analysis of the data was conducted in order to better comprehend the problem. This preliminary analysis, involving statistical descriptions and tests, was conducted for time series of mean daily PM2.5 concentration (PM2.5), maximum daily temperature (Tmax), minimum daily temperature (Tmin) and total daily hospitalizations (Hosp), all considering their full length.

Initially, all the series were individually decomposed to obtain trends and seasonality. Additionally, an autocorrelation function (ACF) was plotted for each dataset, and an Augmented Dickey-Fuller (ADF) test was performed to check stationarity. Those were conducted to ensure the applicability of other methods, mainly forecasting algorithms.

After preliminary analysis, the three datasets were evaluated against each other. For the analysis period (2021-2024), Pearson's correlations were calculated between the aforementioned variables of interest. Also, cross-correlation functions (CCF) were plotted, considering lags of –20 to 20 days. Deeper statistical analysis between the datasets was then conducted, namely primary component analysis (PCA) and clustering. These methods involved the three sets of information at the same time, revealing interesting patterns from the whole.

Lastly, forecasting and correlation analysis were developed using Neural Networks, aiming to further investigate the observed patterns. This was conducted using...

<!-- TODO [C4]: Placeholders do autor -->
> **[PLACEHOLDER]** Delinear a tecnica das redes neurais
>
> **[PLACEHOLDER]** Especificar os parametros de validação, hiperparametros, etc
>
> **[PLACEHOLDER]** Falar os dados de projeção do cmip6 usados

<!-- TODO [D12]: Hiperparâmetros do XGBoost não foram especificados — obrigatório para Lancet. -->
<!-- TODO [D1]: DLNM descrito em Methods mas nunca implementado — análise principal ausente. -->
<!-- TODO [D2]: Controle DOW + feriados ausente. -->

---

## Results and Discussion

Initially, the datasets were analyzed individually. Using an additive model, the series was decomposed in trend and seasonal components. This method showed that, in concordance with what has been observed throughout the world, temperatures in Curitiba are in a rising trend. This trend can be noted by comparing different subsets of the whole temperature time series (1961-2024). When considering the period from 1961 to 1985, Curitiba showed a mean daily temperature of 16.71 °C (62 °F approximately). This mean value, computed for a more recent period, 2007-2024, rose to 18.20 °C (approximately 64.8 °F). These numbers report a rise of 1.42 °C in the mean daily temperatures.

As well as temperatures, the number of hospitalizations in Curitiba reported an increasing trend. This increase is expected, given the rise in population. However, we can also observe this trend when evaluating hospitalizations per capita (number of hospitalizations by 100 thousand inhabitants, considering resident population). These results indicate that there is an increasing number of hospitalizations for the municipality of Curitiba during the period of analysis.

Interesting indications can also be noted when decomposing the series of daily mean PM2.5 concentrations. Unlike the other two datasets, this case does not report an overall trend of increase or decrease. In fact, from 2021 to 2022, PM2.5 concentrations in Curitiba tended to be reduced. This can be understood as a consequence of the world pandemic and goes along with other reports of lower air pollutant concentration throughout the world. Nevertheless, the levels of PM2.5 started to increase again after 2023, with the augmenting tendency becoming even greater during 2024. It is important to note that the year 2024 was an abnormal year for the region regarding air quality. The combined effect of a series of wildfires on different neighboring biomes, and an intensification of low-level jets (South American Low-Level Jet, or SALLJ), brought a plume of air pollutants over the whole extent of the Paraná state. Measurements from different cities reported extremely high levels of air pollution, with visibly worsened air quality.

Once the individual patterns of each dataset were investigated, the relationships between the variables were analyzed. Initially, cross-correlation functions (CCF) were plotted for each combination of two variables considering lags from –30 to 30 days. However, this approach did not produce significant results, with correlations, since all the obtained correlation factors were under 0.30 in absolute value. This indicates that a linear relationship between PM2.5 concentrations, temperatures, and hospitalizations may not be assumed without unsignificant errors. Indeed, this is further noticed when plotting a dispersion graph for the three datasets. As shown in Figure 1, no clear pattern can be observed when plotting the three sets altogether. Both days with hot and cold temperature extremes can be related to elevated numbers of hospitalizations, and their relationship with extremely polluted days are not clearly defined as well. Nonetheless, low pollution days still were noted to produce a lower number of hospitalizations.

> **Figure 1.** Dispersion plot for the three datasets employed. The horizontal axis contains temperature data, in °C; while the vertical axis contains PM2.5 concentrations, in µg/m³. The color of each dot represents total daily hospitalizations, ranging from blue (less hospitalizations) to red (more hospitalizations).

Given the complexity of the problem, further investigation involved Principal Component Analysis (PCA) of the domain. In contrast to what was observed during CCF and dispersion analysis, the PCA was able to detect more tangible patterns. For this, we focused on the two principal components (PC1 and PC2) that were detected to explain, in total, 73.70% of the variance in the whole dataset. The loading of each variable onto the PC is shown in Table 1, along with each PC explained variance.

**Table 1.** PCA Loadings (N=905 complete-case days, 2022-2024). Variables standardised prior to decomposition.

| Component | PM2.5 | T_min | Hospitalizations | Explained Variance |
|-----------|-------|-------|------------------|-------------------|
| PC1       | +0.607 | -0.538 | +0.585          | 49.3%             |
| PC2       | +0.235 | +0.824 | +0.515          | 27.0%             |

PCA on standardised PM2.5, T_min, and daily hospitalisations identified two components explaining 76.2% of total variance (Table 1). PC1 (49.3%) loaded positively on PM2.5 (+0.607) and hospitalisations (+0.585) and negatively on T_min (-0.538), associating cold, polluted days with higher admissions. PC2 (27.0%) was dominated by temperature (+0.824); its non-negligible hospitalisation loading (+0.515) is consistent with a known U-shaped temperature-health relationship whereby both heat and cold extremes elevate morbidity, but reflects substantially less variance than PC1. Partial-correlation analysis confirmed that the direct association between T_min and hospitalisations remains negative after controlling for PM2.5 (r=-0.144, p<0.001), supporting cold exposure as the dominant temperature-related driver. The dispersion plot, considering PCA space, is shown in Figure 2, with colors analogous to Figure 1.

> **Figure 2.** Dispersion plot for the three datasets employed in PCA space. The color of each dot represents total daily hospitalizations, ranging from blue (less hospitalizations) to red (more hospitalizations).

Now, when analyzing Figure 2, there is a clearer visual pattern of the influence of PC1 and PC2 on the daily number of hospitalizations. Firstly, it can be noted that, mostly when PC1 acquires positive values, we can observe more hospitalizations. As discussed before, positive PC1 days are related to high pollution and low temperatures, indicating that the concomitant occurrence of these conditions can impact public health. Additionally, the days with highest hospitalization numbers can be found in the upper right quarter, indicating that elevated temperatures can also contribute, albeit with less intensity, to health problems.

Further investigations regarding these patterns were then conducted using clustering analysis. In addition to temperature and pollution data, relative humidity and atmospheric pressure were added to the input dataset, aiming to enhance clustering results. The algorithm was able to delineate four main clusters, numbered from 0 to 3. The profile of each cluster is shown on Table 2. The allocation of each data point to a certain cluster is determined by similarity between the input variables, enabling the clearer visualization of patterns in the dataset. In this case, the 4 produced clusters represent different meteorological and air quality scenarios that are recurrent in the city of Curitiba. Cluster 0 and cluster 3 are the more extreme ones, with cluster 0 being related to hot and polluted days, while cluster 3 represent colder days, albeit with low levels of air pollution. Cluster 1 represents also hotter days, but with good air quality, and, lastly, cluster 2 encompasses more moderate occasions, both regarding air pollution and climate.

<!-- TODO [D7/A1]: DIVERGÊNCIA CRÍTICA — coluna "Temp." mostra valores em Fahrenheit rotulados como Celsius (71°C, 78°C, etc. são fisicamente impossíveis). O script `analysis/clustering/cluster_analysis.py` documenta essa divergência em `validation_report.txt`. Corrigir tabela com valores reais em °C. -->
<!-- TODO [D6/Auditoria item 6]: Nenhum código de clustering existia no repositório. Agora implementado em `analysis/clustering/cluster_analysis.py`. -->

**Table 2.** Values of the different input variables commonly observed in each cluster. tₘₐₓ = maximum temperature; tₘₑd = mean temperature; tₘᵢₙ = minimum temperature; PM₂.₅ = fine particulate matter; RH = relative humidity.

| Cluster | tₘₐₓ | tₘₑd | tₘᵢₙ | PM₂.₅ | RH | Temp. | Pressure |
|---------|------|------|------|--------|-----|-------|----------|
| 0 | High (>27 °C) | High (>20 °C) | High (>17 °C) | High (>50 µg/m³) | Moderate (≈53 %) | ~~Moderate (≈71 °C)~~ | Moderate (≈915 hPa) |
| 1 | Very High (>29 °C) | Very High (>22 °C) | Very High (>18 °C) | Low (<15 µg/m³) | High (58 %) | ~~High (78 °C)~~ | Low (911 hPa) |
| 2 | Moderate (~23 °C) | Moderate (~18 °C) | Moderate (~15 °C) | Moderate (~10 µg/m³) | High (64 %) | ~~Moderate (~70 °C)~~ | Moderate (913 hPa) |
| 3 | Low (<19 °C) | Low (<14 °C) | Low (<11 °C) | Low (~15 µg/m³) | High (65 %) | ~~Low (62 °C)~~ | High (917 hPa) |

> **ERRATA (D7):** Os valores da coluna "Temp." estão em **Fahrenheit** erroneamente rotulados como °C. Valores convertidos: 71°F = 21.7°C, 78°F = 25.6°C, 70°F = 21.1°C, 62°F = 16.7°C. Ver `analysis/clustering/validation_report.txt` para detalhes completos.

The dataset, now segregated on the four different clusters, was then reevaluated against daily hospitalizations numbers, using linear correlations. As shown in Figure 3, clusters 0 and 3 were the ones with more positive correlations with the number of hospitalizations. This further corroborates the hypothesis that extreme climate events (both hot and cold) can indeed have impacts on public health, even more so when air pollution is elevated. In addition, Figure 3 also shows how the correlations can vary considering daily lags. That is, for cluster 0 (extreme heat and pollution), the highest correlations can be observed for no-lag and a 4-day lag, indicating a more immediate response to hot and polluted air conditions. In contrast, when analyzing cluster 3 (cold days), it is noted that the correlations with hospitalizations tend to increase in the range of 3 to 10-day lags. That behavior is indicative of a delayed and more lasting response. Moreover, cluster 1 (hot days, but with good air quality) shows exclusively negative correlations to hospitalizations, for all the evaluated lags. This indicates a positive impact of good air quality on the public health system, observable even on extreme heat days.

> **Figure 3.** Correlations between each cluster and total number of daily hospitalizations, for different lags (0 to 14 days).

Combining the results obtained during PCA and clustering, two main conclusions were obtained. Firstly, it was noted that extreme heat days and heatwaves can in fact impact public health, increasing the number of daily hospitalizations. However, the synergetic effect between air temperature and atmospheric pollution over hospitalizations is better observed during cold extremes. This can be partly explained solely by the fact that, during colder days, atmospheric mixture layer is lowered, worsening air quality and, therefore, intensifying the negative impacts on public health. Nevertheless, there is also the possibility of other mechanisms allowing for this synergy between cold temperatures and air pollution, especially when considering heatwaves. Moreover, the mechanisms may vary according to seasonal parameters. That is, cold waves that happen "out of season", during commonly warmer periods, may be more impactful.

This hypothesis was further evaluated using neural network (NN) methods. For this, the next step was to investigate relationships between the three variables considering lags, as well as assessing the impact of cold extremes on future predictions of hospitalizations. Three distinct NN were trained with temperature, pollution and hospitalizations data, namely an Extreme Learning Machine (ELM), a Multilayer Perceptron (MLP) and a Cross-Gradient Boosting (XGBoost). The performance metrics for the three algorithms are shown on Figure 4, considering no days of lag between input (meteorological and air quality data) and output data (number of absolute daily hospitalizations). It is notable that, considering each one of the calculated metrics (MSE, RMSE, MAE, and MAPE), XGBoost was the network with better performance, consistently generating lower metric values. For that reason, further discussions will involve only results produced by XGBoost, with the outputs of other algorithms available on supplementary materials.

> **Figure 4.** Performance metrics used to evaluate the ELM (dark blue), MLP (light blue) and XGBoost (orange) algorithms.

<!-- TODO [C6]: Discrepância temporal — texto diz 2030, legenda diz 2050. Resolver. -->

The trained Neural network models were then employed on CMIP6 projection data, considering SSP5-8.5. This way, modeled results would describe a "worst-case scenario" to better understand changes in hospitalizations with pollution and temperature as drives. Firstly, a comparison of absolute weekly hospitalizations between the years 2023 (measured, used as baseline for comparisons) and 2030 (CMIP6 projections) was performed. Figure 5 shows this comparison, wherein blue bars represent increases from 2023 data, and correspondently red bars represent decreases. The first graph (figure 5.A) represents XGBoost Model's output, considering only CMIP6 projection data. Meanwhile, the latter two represent outputs considering randomly simulated occurrences of coldwaves and heatwaves respectively (figure 5.B and 5.C).

Initially, it is important to note that, in absolute terms, all cases predict overall increases in hospitalizations. For example, as shown in figure 5, there were 11522 hospitalizations throughout the whole year of 2023. According to the model predictions, this number would be increased to over 11700 yearly hospitalizations in 2030. Additionally, when comparing the general case with the ones where heat and coldwaves are present, it is noted that, although the presence of heatwaves does not alter significantly the hospitalizations response, the presence coldwaves can indeed increase even further this augmentation.

> **Figure 5.** Weekly comparison of total hospitalizations between 2023 (baseline, observed) and 2050 (predicted using XGBoost). Blue bars represent an increase over the baseline, and red bars represent decreases. The compared scenarios include A) general: modeled directly using CMIP6 data; B) coldwaves: added random occurrences of coldwaves to the input data; and C) heatwaves: added random occurrences of heatwaves to the input data.

The second observable pattern in Figure 5 is related to an analysis between general, coldwaves and heatwaves scenarios. Given what is shown in figures 5.A, 5.B and 5.C, increases and decreases in hospitalizations according to the baseline commonly happen during the same periods for the three different scenarios. However, increases during weeks 46, 50, and 51 are only present in the coldwave scenario. Indeed, these increases are concomitant to three of the generated coldwaves over CMIP6 data and therefore can be attributed to them. Moreover, it is important to remark that the period in which these occur tends to be hot in Curitiba. When other coldwaves occur during commonly cold periods, the response is not so significant. In this case, we show only the comparison for no lag, but this pattern is also present in other simulations, as shown on the supplementary material. That indicates that, in order to evaluate public health response to extreme pollution and temperature events, the variation of temperature is also important, maybe even more so than absolute temperature values.

Figure 6 shows an extended simulation period, comparing 2023 data to projections for 2050. In this case, there are no absolute increases in hospitalizations for general and heatwaves scenarios, with only a slight increase observable on coldwaves scenario. Also, this is related to a higher intensity of weekly increases, and not to increases on different periods than the other scenarios. This points to a different behavior of the modeled outputs when comparing longer time deltas, indicating time limitations.

---

## Conclusion

This study examined the interconnected effects of extreme temperatures, particulate air pollution, and public health in the city of Curitiba using time-series data from 2021 to 2024. By integrating meteorological, air quality, and hospitalization datasets, the analysis revealed complex but consistent relationships, particularly under extreme climatic conditions.

The results demonstrated that both heatwaves and coldwaves are associated with increases in hospital admissions; however, the strongest combined effects were observed during cold extremes. These events typically coincide with degraded air quality due to a shallower atmospheric boundary layer, amplifying the adverse impacts of particulate pollution. PCA and clustering analyses confirmed that days characterized by low temperatures and high PM₂.₅ concentrations were those most strongly associated with elevated hospitalization numbers.

Neural network modeling further supported these findings. While future scenarios consistently predicted increases in hospitalizations due to changes in temperature and pollution patterns, the simulations indicated that the occurrence of coldwaves—especially those happening outside the usual cold season—may intensify this trend more than heatwaves. This result suggests that temperature variability and seasonal anomalies may be more relevant to health impacts than absolute temperature alone.

Overall, this work highlights the need for integrated public health and environmental monitoring strategies that consider the combined and lagged effects of temperature extremes and air pollution. These results reinforce the importance of climate-resilient health planning, especially in subtropical urban centers where both heat and cold extremes coexist and interact with local air quality dynamics.

---

## References

1. BEEVERS, S. et al. Climate change policies reduce air pollution and increase physical activity: Benefits, costs, inequalities, and indoor exposures. *Environment International*, v. 195, p. 109164, jan. 2025.

2. BELL, M. L.; GASPARRINI, A.; BENJAMIN, G. C. Climate Change, Extreme Heat, and Health. *New England Journal of Medicine*, v. 390, n. 19, p. 1793–1801, 16 maio 2024.

3. CHENG, C. et al. Effects of extreme temperature events on deaths and its interaction with air pollution. *Science of The Total Environment*, v. 915, p. 170212, 2024.

4. DUTHIE, D. Heat-related illness. *The Lancet*, v. 352, n. 9137, p. 1329–1330, out. 1998.

5. EBI, K. L. et al. Hot weather and heat extremes: health risks. *The Lancet*, v. 398, n. 10301, p. 698–708, 2021.

6. GARDAŠEVIĆ, A. et al. Analysis of the dependence of the observed urban air pollution extremes in the vicinity of coal fuelled power plants on combined effects of anthropogenic and meteorological drivers. *Environmental Development*, v. 52, p. 101095, 2024.

7. GONG, J. et al. The 2023 report of the synergetic roadmap on carbon neutrality and clean air for China: Carbon reduction, pollution mitigation, greening, and growth. *Environmental Science and Ecotechnology*, v. 23, p. 100517, 2025.

8. GOPIKRISHNAN, G. S.; KUTTIPPURATH, J. Impact of the National Clean Air Programme (NCAP) on the particulate matter pollution and associated reduction in human mortalities in Indian cities. *Science of The Total Environment*, v. 968, p. 178787, 2025.

9. HERTZOG, L. et al. Mortality burden attributable to exceptional PM2.5 air pollution events in Australian cities: A health impact assessment. *Heliyon*, v. 10, n. 2, p. e24532, 2024.

10. KALKSTEIN, L. S. Lessons from a very hot summer. *The Lancet*, v. 346, n. 8979, p. 857–859, set. 1995.

11. KATSOUYANNI, K. et al. THE 1987 ATHENS HEATWAVE. *The Lancet*, v. 332, n. 8610, p. 573, set. 1988.

12. LINARES, C. et al. How air pollution and extreme temperatures affect emergency hospital admissions due to various respiratory causes in Spain, by age group: A nationwide study. *International Journal of Hygiene and Environmental Health*, v. 266, p. 114570, 2025.

13. LYE, M.; KAMAL, A. EFFECTS OF A HEATWAVE ON MORTALITY-RATES IN ELDERLY INPATIENTS. *The Lancet*, v. 309, n. 8010, p. 529–531, mar. 1977.

14. MARX, W.; HAUNSCHILD, R.; BORNMANN, L. Heat waves: a hot topic in climate change research. *Theoretical and Applied Climatology*, v. 146, n. 1–2, p. 781–800, 3 out. 2021.

15. MCMICHAEL, A. J.; WOODRUFF, R. E.; HALES, S. Climate change and human health: present and future risks. *The Lancet*, v. 367, n. 9513, p. 859–869, mar. 2006.

16. MESTITZ, P.; BRIAN GOUGH, W. ACUTE ANHIDROTIC HEAT EXHAUSTION. *The Lancet*, v. 274, n. 7100, p. 462, set. 1959.

17. NASHWAN, A. J.; ALDOSARI, N.; HENDY, A. Hajj 2024 heatwave: addressing health risks and safety. *The Lancet*, v. 404, n. 10451, p. 427–428, ago. 2024.

18. PASCAL, M. et al. Extreme heat and acute air pollution episodes: A need for joint public health warnings? *Atmospheric Environment*, v. 249, p. 118249, 2021.

19. POUMADÈRE, M. et al. The 2003 Heat Wave in France: Dangerous Climate Change Here and Now. *Risk Analysis*, v. 25, n. 6, p. 1483–1494, 15 dez. 2005.

20. REQUIA, W. J. et al. Short-term air pollution exposure and mortality in Brazil: Investigating the susceptible population groups. *Environmental Pollution*, v. 340, p. 122797, 2024.

21. ROWLAND, S. T. et al. The association between ambient temperature variability and myocardial infarction in a New York-State-based case-crossover study: An examination of different variability metrics. *Environmental Research*, v. 197, p. 111207, jun. 2021.

22. SCHUMAN, S. H. Patterns of urban heat-wave deaths and implications for prevention: Data from New York and St. Louis during July, 1966. *Environmental Research*, v. 5, n. 1, p. 59–75, mar. 1972.

23. SETHI, Y. et al. Impact of Air Pollution on Neurological and Psychiatric Health. *Archives of Medical Research*, v. 55, n. 7, p. 103063, 2024.

24. THE LANCET. Heatwaves and health. *The Lancet*, v. 392, n. 10145, p. 359, 2018.

25. THE LANCET. 2022 heatwaves: a failure to proactively manage the risks. *The Lancet*, v. 400, n. 10350, p. 407, 6 ago. 2022.

26. TRENBERTH, K. E.; FASULLO, J. T. Climate extremes and climate change: The Russian heat wave and other climate extremes of 2010. *Journal of Geophysical Research: Atmospheres*, v. 117, n. D17, 16 set. 2012.

27. TSENG, W.-L. et al. Compound spatial extremes of heatwaves and downstream air pollution events in East Asia. *Atmospheric Research*, v. 312, p. 107772, 2024.

28. XIA, C.; YEH, A. G.-O.; LEI, Z. Beyond hazard-induced migration: Dissecting everyday mobilities in response to air pollution and extreme cold events at multiple spatial and temporal scales. *Journal of Transport Geography*, v. 118, p. 103927, 2024.

---

## Known Issues (from audit)

This section tracks divergences identified during the repository audit. See [`review/PLANO_REVISAO_LANCET.md`](../review/PLANO_REVISAO_LANCET.md) for the complete action plan.

### Critical Data Issues

| ID | Issue | Status |
|----|-------|--------|
| A1 | PurpleAir temperature in Fahrenheit, not Celsius | Documented in `analysis/clustering/validation_report.txt` |
| A2 | PM2.5 Channel A vs B discrepancy (>61%) | Open |
| A3 | Health data not disaggregated (no ICD, age, sex) | Open |
| A4 | Title says "mortality" but outcome is hospitalization | Open |
| A5 | Hospitalization series non-stationary (ADF p=0.318) | Open |
| A6 | PCA loadings diverge between notebook and manuscript | **RESOLVED** — Recalculated with t_min; loadings corrected in manuscript |

### Placeholders Still in Manuscript

| ID | Item | Location |
|----|------|----------|
| B1 | ~~Table 2 (RERI) — "values are illustrative"~~ | Not in current version (was in extended .docx) |
| B2 | Sex stratification result | Not in current version |
| B3 | Sensor R² | Not in current version |
| B4 | ICD codes | Not in current version |
| B5 | SHAP beeswarm plot | Not in current version |

### Methodology Gaps

| ID | Missing Analysis | Priority |
|----|-----------------|----------|
| D1 | DLNM (described but never implemented) | Mandatory |
| D2 | DOW + holidays control in GLM | Mandatory |
| D3 | Sensitivity excluding 2021 (COVID) | Mandatory |
| D6 | Clustering code | **RESOLVED** — `analysis/clustering/cluster_analysis.py` |
| D7 | Cluster table F→C error | **DOCUMENTED** — `analysis/clustering/validation_report.txt` |
