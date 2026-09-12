# Indian Inflation Forecasting & Price Transmission

## Indian Inflation Forecasting and Price Transmission: An Econometric Analysis of CPI, WPI and Output PPI

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-brightgreen)](https://indian-inflation-dashboard.streamlit.app/)

An applied econometrics and time-series forecasting project examining Indian consumer-price inflation, model performance, and the relationship between consumer, wholesale, and producer prices.

---

## Project Overview

This project develops an econometric framework for forecasting Indian CPI inflation and examining whether movements in upstream wholesale and producer prices contain useful information about subsequent consumer-price inflation.

The project combines:

- Time-series exploratory analysis
- Econometric diagnostics
- ARIMA and SARIMA modelling
- Walk-forward / rolling-origin forecasting
- Out-of-sample model evaluation
- Residual diagnostics
- Lead-lag correlation analysis
- CPI, WPI and Output PPI price-transmission analysis
- Interactive Streamlit deployment

## Research Question

> How effectively can Indian CPI inflation be forecast using time-series econometric models, and to what extent do upstream wholesale and producer price movements provide useful information about subsequent consumer-price inflation?

---

## Objectives

1. Forecast Indian CPI inflation using statistical time-series models.
2. Compare competing models using walk-forward out-of-sample validation.
3. Evaluate forecasting errors using MAE and RMSE.
4. Diagnose residual behaviour and model adequacy.
5. Examine lead-lag relationships between CPI, WPI and Output PPI inflation.
6. Translate the empirical analysis into an interactive forecasting dashboard.

---

## Data

The analysis uses Indian price indices from official statistical sources.

### Consumer Price Index (CPI)

Source: Ministry of Statistics and Programme Implementation (MoSPI) / National Statistical Office (NSO)

The project distinguishes between:

- Historical CPI series based on 2012=100
- Current CPI series based on 2024=100

The base-year revision is explicitly considered when constructing the modelling datasets.

### Wholesale Price Index (WPI)

Source: Office of Economic Adviser, Department for Promotion of Industry and Internal Trade (DPIIT), Ministry of Commerce & Industry.

The analysis considers:

- WPI All Commodities
- WPI Primary Articles
- WPI Fuel & Power
- WPI Manufactured Products

### Output Producer Price Index (Output PPI)

Output PPI data are incorporated as an upstream producer-price indicator for examining price transmission and co-movement with CPI inflation.

---

## Methodology

### CPI Inflation

CPI inflation is measured using year-over-year growth:

$$
Inflation_t =
\left(
\frac{CPI_t}{CPI_{t-12}} - 1
\right)\times100
$$

This transformation reduces the effect of seasonal monthly comparisons and produces the standard year-over-year inflation measure.

### Time-Series Modelling

The modelling workflow includes:

1. Data auditing and preparation
2. Exploratory data analysis
3. Stationarity and autocorrelation diagnostics
4. ARIMA/SARIMA model specification
5. Residual diagnostics
6. Walk-forward forecasting
7. Out-of-sample model comparison
8. Forecast generation
9. Price-transmission analysis

### Model Evaluation

Forecasts are evaluated using out-of-sample errors rather than relying solely on in-sample fit.

Primary metrics:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)

Walk-forward / rolling-origin validation is used to reduce look-ahead bias and provide a more realistic assessment of forecasting performance.

---

## Price Transmission Analysis

Lead-lag correlations are calculated between CPI inflation and upstream price indicators.

The analysis examines whether WPI and Output PPI movements tend to co-move with CPI inflation at different lags.

Selected results from the common modelling sample include:

| Indicator | Strongest Lag | Correlation |
|---|---:|---:|
| Output PPI | 0 | 0.8497 |
| WPI Fuel & Power | 5 | 0.6861 |
| WPI All Commodities | 0 | 0.8975 |
| WPI Manufactured Products | 6 | -0.7941 |
| WPI Primary Articles | 0 | 0.9612 |

These results indicate strong statistical co-movement in the common sample.

**Important:** correlation and lead-lag association do not establish causality. The results should therefore be interpreted as evidence of statistical association and predictive information rather than definitive causal transmission.

---

## Key Findings

- ARIMA(1,1,1) emerged as the best-performing model in the initial model comparison by RMSE.
- Walk-forward validation provides the primary out-of-sample evaluation framework.
- In the Phase 11.2 one-step-ahead benchmark, the CPI-only specification achieved an RMSE of 0.7676.
- The CPI + WPI specification achieved an RMSE of 1.0928, while CPI + WPI + PPI achieved 1.0446.
- WPI and Output PPI exhibit substantial contemporaneous and lagged correlation with CPI inflation in the 21-observation common sample.
- These correlations are treated as descriptive evidence rather than causal estimates.

## Dashboard

The project is deployed as an interactive Streamlit application:

**[Open the Indian Inflation Forecasting Dashboard](https://indian-inflation-dashboard.streamlit.app/)**

The dashboard provides:

- Inflation trends
- Forecasts
- Model comparison
- Price transmission analysis
- Forecast diagnostics
- Methodology and interpretation

---

## Repository Structure

```text
My-Creations/
│
├── dashboard/
│   ├── app.py
│   ├── config.py
│   └── utils.py
│
├── data/
│   ├── raw/
│   ├── New Processed Results/
│   ├── Processed Result/
│   └── mnt/data/
│
├── 01_data_audit.ipynb
├── 02_build_master_dataset.ipynb
├── 03_eda.ipynb
├── 04_econometric_diagnostics.ipynb
├── 05_arima_models.ipynb
├── 06_walk_forward_backtesting.ipynb
├── 07_model_evaluation_and_comparison.ipynb
├── 08_forecasts_and_diagnostics.ipynb
├── 09_price_transmission_analysis.ipynb
│
├── .gitignore
├── README.md
└── requirements.txt
