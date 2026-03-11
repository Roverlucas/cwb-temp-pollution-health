# The compounding respiratory hospitalisation risk of cold spells and particulate matter in a subtropical metropolis: a time-series analysis

**Authors:** Felipe Baglioli, Lucas Rover, Pedro Augusto Breda Fontão, Leonardo José Rossoni Quadros, Eduardo Tadeu Bacalhau, Camila Carpenedo, Yara de Souza Tadano, Ricardo Henrique Moreton Godoi

**Target journal:** The Lancet Regional Health — Americas

## Project Structure

```
cwb-temp-pollution-health/
├── manuscript/               # Article manuscript (LaTeX + PDF)
├── notebooks/                # Jupyter notebooks (analysis code)
│   ├── temp_pm_saude_cwb.ipynb   # Exploratory data analysis
│   └── temp_morb_pm.ipynb        # Morbidity & mortality models
├── data/
│   ├── raw/
│   │   ├── purpleair/        # PurpleAir PM2.5 sensor data (2021-2025)
│   │   ├── datasus/          # DATASUS health records (Curitiba)
│   │   ├── inmet/            # INMET temperature data (1961-2024)
│   │   └── health/           # Aggregated morbidity/mortality counts
│   ├── processed/            # Merged analysis-ready dataset
│   └── cmip6/                # CMIP6 SSP5-8.5 climate projections
├── analysis/
│   └── dlnm/                 # DLNM results and figures
├── figures/
│   ├── exploratory/          # EDA plots (decomposition, PCA, correlations)
│   └── results/              # Model output figures (lag comparisons, predictions)
├── poster/                   # EGU conference poster
└── review/                   # Revision action plans and strategic reviews
```

## Key Findings

- **Cold extremes** at P1 of T_min (5.2 °C) yield cumulative RR = 1.42 [95% CI: 1.09–1.84] — a 42% excess in respiratory hospitalisations
- **Heat effects** are non-significant (P90 RR = 1.06 [0.98–1.14])
- **Delayed effect** peaks at lags 3–10 days, providing a window for preventive intervention
- **MMT** = 17.8 °C (75th percentile of local temperature distribution)

## Data Sources

| Source | Description | Period |
|--------|------------|--------|
| **INMET** | Daily temperature (Tmax, Tmed, Tmin) from weather station A807 | 1961–2024 |
| **DATASUS** | Respiratory hospitalization records (ICD-10 J00–J99) | 2022–2024 |
| **PurpleAir** | PM2.5 from low-cost sensor (station 90875, Curitiba) | 2022–2024 |
| **CMIP6** | SSP5-8.5 projections (supplementary) | 2015–2100 |

## Methods

- **Primary analysis:** Distributed lag non-linear models (DLNM) with quasi-Poisson regression
- **Supplementary:** K-means clustering, cross-correlation analysis, XGBoost/MLP/ELM forecasting with SHAP

## Requirements

- Python 3.10+
- R 4.x (for DLNM via `dlnm` package)
- Jupyter Notebook
- Key packages: pandas, numpy, scikit-learn, matplotlib, seaborn, xgboost, shap

## Status

Under review — target: The Lancet Regional Health — Americas.
