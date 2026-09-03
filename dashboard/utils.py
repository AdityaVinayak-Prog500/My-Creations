from pathlib import Path
import pandas as pd

from config import (
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
)


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV and raise a clear error if it cannot be read."""

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"CSV is empty: {path}")

    return df


def prepare_master_data() -> pd.DataFrame:
    """Load and prepare the main monthly dataset."""

    df = load_csv(MASTER_DATA)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = (
        df
        .dropna(subset=["date"])
        .sort_values("date")
    )

    return df


def prepare_forecasts() -> pd.DataFrame:
    """Load the main walk-forward forecast output."""

    df = load_csv(BEST_FORECASTS)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    return df


def prepare_phase11_2_predictions() -> pd.DataFrame:
    """Load dated Phase 11.2 forecasting-contribution results."""

    df = load_csv(PHASE11_2_PREDICTIONS)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    return df.sort_values("date")


def prepare_model_comparison() -> pd.DataFrame:
    """Load initial model comparison metrics."""

    return load_csv(MODEL_COMPARISON)


def prepare_walk_forward_results() -> pd.DataFrame:
    """Load rolling-origin ARIMA/SARIMA results."""

    return load_csv(ARIMA_SARIMA_RESULTS)


def prepare_cpi_wpi_ppi() -> pd.DataFrame:
    """Load CPI-WPI-PPI modelling sample."""

    df = load_csv(CPI_WPI_PPI_DATA)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df = df.sort_values("date")

    return df


def prepare_diagnostics() -> pd.DataFrame:
    """Load econometric diagnostic summary."""

    return load_csv(DIAGNOSTIC_SUMMARY)


def prepare_residual_diagnostics() -> pd.DataFrame:
    """Load residual diagnostics."""

    return load_csv(RESIDUAL_DIAGNOSTICS)


def prepare_transmission_data() -> pd.DataFrame:
    """Load Phase 11 transmission dataset."""

    df = load_csv(TRANSMISSION_DATA)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df = df.sort_values("date")

    return df


def prepare_common_yoy_sample() -> pd.DataFrame:
    """Load the complete CPI-WPI-PPI common YoY sample."""

    df = load_csv(COMMON_YOY_SAMPLE)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df = df.sort_values("date")

    return df


def prepare_lagged_correlations() -> pd.DataFrame:
    """Load all lagged correlations."""

    return load_csv(LAGGED_CORRELATIONS)


def prepare_lagged_correlation_summary() -> pd.DataFrame:
    """Load maximum absolute lagged correlation summary."""

    return load_csv(LAGGED_CORRELATION_SUMMARY)


def latest_value(
    df: pd.DataFrame,
    column: str,
) -> float | None:
    """Return the latest non-null value of a column."""

    if column not in df.columns:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if values.empty:
        return None

    return float(values.iloc[-1])


def format_percent(
    value: float | None,
    decimals: int = 2,
) -> str:
    """Format a numeric value as a percentage."""

    if value is None:
        return "N/A"

    return f"{value:.{decimals}f}%"