# Structural Adaptation Gaps Amplify the Synergistic Mortality Risk of Cold Spells and Particulate Matter in a Subtropical Metropolis

**Authors:** Felipe Baglioli, Lucas Rover, et al.

**Target journal:** The Lancet Regional Health — Americas

## Project Structure

```
cwb-temp-pollution-health/
├── manuscript/               # Article manuscript (.docx)
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
├── figures/
│   ├── exploratory/          # EDA plots (decomposition, PCA, correlations)
│   └── results/              # Model output figures (lag comparisons, predictions)
├── poster/                   # EGU conference poster
└── review/                   # Revision action plans and strategic reviews
```

## Data Sources

| Source | Description | Period |
|--------|------------|--------|
| **PurpleAir** | PM2.5 from low-cost sensor (station 90875, Curitiba) | 2021–2025 |
| **DATASUS** | Hospitalization and mortality records (ICD-filtered) | 2021–2024 |
| **INMET** | Daily temperature (Tmax, Tmed, Tmin) from weather station | 1961–2024 |
| **CMIP6** | SSP5-8.5 projections (EC-Earth3-Veg-LR, TaiESM1) | 2015–2100 |

## Requirements

- Python 3.10+
- Jupyter Notebook
- Key packages: pandas, numpy, scikit-learn, matplotlib, seaborn, xgboost, shap

## Status

Under revision — see `review/` for detailed action plans.
