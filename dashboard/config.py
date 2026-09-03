from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

PROCESSED_DIR = DATA_DIR / "Processed Result"

PHASE11_DIR = (
    DATA_DIR
    / "mnt"
    / "data"
    / "phase11_results"
)

PHASE11_2_DIR = (
    DATA_DIR
    / "mnt"
    / "data"
    / "phase11"
    / "phase11_2"
)


# ============================================================
# CORE DATASETS
# ============================================================

MASTER_DATA = (
    PROCESSED_DIR
    / "master_monthly_dataset.csv"
)

BEST_FORECASTS = (
    PROCESSED_DIR
    / "best_walk_forward_predictions.csv"
)

MODEL_COMPARISON = (
    PROCESSED_DIR
    / "initial_model_comparison.csv"
)

ARIMA_SARIMA_RESULTS = (
    PROCESSED_DIR
    / "walk_forward_arima_sarima_results.csv"
)

CPI_WPI_PPI_DATA = (
    PROCESSED_DIR
    / "model_sample_cpi_wpi_ppi.csv"
)

DIAGNOSTIC_SUMMARY = (
    PROCESSED_DIR
    / "diagnostic_summary.csv"
)

RESIDUAL_DIAGNOSTICS = (
    PROCESSED_DIR
    / "residual_diagnostics.csv"
)


# ============================================================
# PHASE 11 — PRICE TRANSMISSION
# ============================================================

TRANSMISSION_DATA = (
    PHASE11_DIR
    / "phase11_transmission_dataset.csv"
)

COMMON_YOY_SAMPLE = (
    PHASE11_DIR
    / "phase11_common_yoy_sample.csv"
)

LAGGED_CORRELATIONS = (
    PHASE11_DIR
    / "02_lagged_correlations.csv"
)

LAGGED_CORRELATION_SUMMARY = (
    PHASE11_DIR
    / "03_lagged_correlation_summary.csv"
)


# ============================================================
# PHASE 11.2 — DATED FORECASTING CONTRIBUTION
# ============================================================

PHASE11_2_PREDICTIONS = (
    PHASE11_2_DIR
    / "phase11_2_one_step_predictions.csv"
)


# ============================================================
# DASHBOARD METADATA
# ============================================================

APP_TITLE = (
    "Indian Inflation Forecasting Dashboard"
)

APP_SUBTITLE = (
    "CPI inflation forecasting, model evaluation, "
    "and price transmission analysis"
)

TARGET_VARIABLE = (
    "CPI Inflation (YoY, %)"
)


# ============================================================
# REQUIRED FILES
# ============================================================

ALL_REQUIRED_FILES = [

    MASTER_DATA,

    BEST_FORECASTS,

    MODEL_COMPARISON,

    ARIMA_SARIMA_RESULTS,

    CPI_WPI_PPI_DATA,

    DIAGNOSTIC_SUMMARY,

    RESIDUAL_DIAGNOSTICS,

    TRANSMISSION_DATA,

    COMMON_YOY_SAMPLE,

    LAGGED_CORRELATIONS,

    LAGGED_CORRELATION_SUMMARY,

    PHASE11_2_PREDICTIONS,

]


# ============================================================
# VALIDATION FUNCTION
# ============================================================

def validate_paths():
    """
    Check whether all required dashboard
    data files exist.

    Returns
    -------
    dict
        Dictionary containing missing file names
        and their expected paths.
    """

    missing = {}

    for path in ALL_REQUIRED_FILES:

        if not path.exists():

            missing[path.name] = str(path)

    return missing