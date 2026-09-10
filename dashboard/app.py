from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    prepare_master_data,
    prepare_forecasts,
    prepare_phase11_2_predictions,
    prepare_model_comparison,
    prepare_walk_forward_results,
    prepare_cpi_wpi_ppi,
    prepare_diagnostics,
    prepare_residual_diagnostics,
    prepare_transmission_data,
    prepare_lagged_correlations,
    prepare_lagged_correlation_summary,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Indian Inflation Forecasting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .research-note {
        padding: 1rem 1.2rem;
        border-radius: 0.65rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PRICE TRANSMISSION COMMON SAMPLE — DIRECT DATA LOAD
# ============================================================

COMMON_YOY_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "mnt"
    / "data"
    / "phase11_results"
    / "phase11_common_yoy_sample.csv"
)


def load_common_yoy_sample():
    """Load the retained 21-observation CPI-WPI-PPI common sample directly."""

    if not COMMON_YOY_FILE.exists():
        return pd.DataFrame(
            columns=[
                "date",
                "cpi_inflation",
                "wpi_inflation",
                "ppi_inflation",
            ]
        )

    common = pd.read_csv(COMMON_YOY_FILE)

    required = {
        "date",
        "cpi_inflation",
        "wpi_inflation",
        "ppi_inflation",
    }

    if not required.issubset(common.columns):
        return pd.DataFrame(
            columns=[
                "date",
                "cpi_inflation",
                "wpi_inflation",
                "ppi_inflation",
            ]
        )

    common["date"] = pd.to_datetime(
        common["date"],
        errors="coerce",
    )

    for column in [
        "cpi_inflation",
        "wpi_inflation",
        "ppi_inflation",
    ]:
        common[column] = pd.to_numeric(
            common[column],
            errors="coerce",
        )

    common = (
        common[
            [
                "date",
                "cpi_inflation",
                "wpi_inflation",
                "ppi_inflation",
            ]
        ]
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")
        .reset_index(drop=True)
    )

    return common



# ============================================================
# LOAD ALL DASHBOARD DATA
# ============================================================

@st.cache_data
def load_all_data():

    master = prepare_master_data()
    forecasts = prepare_forecasts()
    phase11_2 = prepare_phase11_2_predictions()
    models = prepare_model_comparison()
    walk_forward = prepare_walk_forward_results()
    cpi_wpi_ppi = prepare_cpi_wpi_ppi()
    diagnostics = prepare_diagnostics()
    residuals = prepare_residual_diagnostics()
    transmission = prepare_transmission_data()
    common_yoy = load_common_yoy_sample()
    lagged = prepare_lagged_correlations()
    lagged_summary = prepare_lagged_correlation_summary()

    return (
        master,
        forecasts,
        phase11_2,
        models,
        walk_forward,
        cpi_wpi_ppi,
        diagnostics,
        residuals,
        transmission,
        common_yoy,
        lagged,
        lagged_summary,
    )


(
    master,
    forecasts,
    phase11_2,
    models,
    walk_forward,
    cpi_wpi_ppi,
    diagnostics,
    residuals,
    transmission,
    common_yoy,
    lagged,
    lagged_summary,
) = load_all_data()

# IMPORTANT: load_all_data() is cached for the rest of the dashboard.
# Refresh the retained common CPI-WPI-PPI sample independently so the
# Price Transmission chart cannot reuse a stale cached 10-row dataset.
common_yoy = load_common_yoy_sample()


# ============================================================
# CURRENT CPI (2024 BASE) — DISPLAY SERIES
# ============================================================

CURRENT_CPI_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "cpi_combined_current_2024base.csv"
)


@st.cache_data
def load_current_cpi():
    """Load the latest official CPI inflation series on the 2024=100 base."""

    if not CURRENT_CPI_FILE.exists():
        return pd.DataFrame(columns=["date", "cpi_yoy"])

    current_cpi = pd.read_csv(CURRENT_CPI_FILE)

    if "date" not in current_cpi.columns or "cpi_yoy" not in current_cpi.columns:
        return pd.DataFrame(columns=["date", "cpi_yoy"])

    current_cpi["date"] = pd.to_datetime(
        current_cpi["date"],
        errors="coerce",
    )
    current_cpi["cpi_yoy"] = pd.to_numeric(
        current_cpi["cpi_yoy"],
        errors="coerce",
    )

    current_cpi = (
        current_cpi[["date", "cpi_yoy"]]
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")
        .reset_index(drop=True)
    )

    return current_cpi


current_cpi = load_current_cpi()


# ============================================================
# CURRENT CPI COMPONENT DATA FOR DISPLAY
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_current_cpi_components():
    """
    Load the current 2024=100 rural and urban CPI General indices
    for dashboard display only.

    The loader accepts the project's CSV formats. A small official
    Jan-Jul 2026 fallback is also included so the visualization stays
    current even if an uploaded component CSV is stale or missing.
    The fallback is display-only and never changes the econometric data.
    """

    frames = []

    for filename, label in [
        ("cpi_rural_current_2024base.csv", "cpi_rural"),
        ("cpi_urban_current_2024base.csv", "cpi_urban"),
    ]:
        path = RAW_DATA_DIR / filename

        if not path.exists():
            continue

        try:
            df = pd.read_csv(path)
        except Exception:
            continue

        # Current normalized files use date + index; older files may use year/month.
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        elif {"year", "month"}.issubset(df.columns):
            month_map = {
                "january": 1, "february": 2, "march": 3,
                "april": 4, "may": 5, "june": 6,
                "july": 7, "august": 8, "september": 9,
                "october": 10, "november": 11, "december": 12,
            }
            df["month_num"] = df["month"].astype(str).str.strip().str.lower().map(month_map)
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df["date"] = pd.to_datetime(
                dict(year=df["year"], month=df["month_num"], day=1),
                errors="coerce",
            )
        else:
            continue

        if "series" in df.columns:
            mask = df["series"].astype(str).str.strip().str.lower() == "current"
            if mask.any():
                df = df.loc[mask].copy()

        if "state" in df.columns:
            mask = df["state"].astype(str).str.strip().str.lower() == "all india"
            if mask.any():
                df = df.loc[mask].copy()

        value_col = next((c for c in ["index", "value"] if c in df.columns), None)
        if value_col is None:
            continue

        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
        out = (
            df[["date", value_col]]
            .rename(columns={value_col: label})
            .dropna(subset=["date", label])
            .sort_values("date")
            .drop_duplicates(subset="date", keep="last")
        )
        frames.append(out)

    if frames:
        components = frames[0]
        for frame in frames[1:]:
            components = components.merge(frame, on="date", how="outer")
    else:
        components = pd.DataFrame(columns=["date", "cpi_rural", "cpi_urban"])

    # Official MoSPI/PIB 2024=100 CPI General indices, Jan-Jul 2026.
    # Values are rounded published indices; July 2026 is provisional.
    official_2026 = pd.DataFrame({
        "date": pd.to_datetime([
            "2026-01-01", "2026-02-01", "2026-03-01",
            "2026-04-01", "2026-05-01", "2026-06-01",
            "2026-07-01",
        ]),
        "cpi_rural": [104.59, 104.74, 105.02, 105.28, 106.11, 107.24, 108.34],
        "cpi_urban": [104.28, 104.36, 104.62, 104.92, 105.66, 106.69, 107.45],
    })

    components = pd.concat([components, official_2026], ignore_index=True)
    components = (
        components
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")
        .reset_index(drop=True)
    )
    return components


current_cpi_components = load_current_cpi_components()


# ============================================================
# MASTER DATA PREPARATION
# ============================================================

master = master.copy()

master["date"] = pd.to_datetime(
    master["date"],
    errors="coerce"
)

master = (
    master
    .dropna(subset=["date"])
    .sort_values("date")
)

# Project target: CPI inflation YoY (%)
master["cpi_yoy"] = (
    master["cpi_combined"]
    .pct_change(12)
    * 100
)


# Build a display-only CPI series by combining:
# - historical 2012=100 CPI-derived YoY inflation, and
# - official published YoY inflation from the current 2024=100 CPI series.
#
# We deliberately do NOT calculate pct_change(12) across the base-year
# revision, because the old and new CPI series are not directly comparable.
cpi_display = (
    master[["date", "cpi_yoy"]]
    .dropna()
    .copy()
)

if not current_cpi.empty:
    historical_cpi = cpi_display[
        cpi_display["date"] < current_cpi["date"].min()
    ].copy()

    cpi_display = (
        pd.concat(
            [
                historical_cpi,
                current_cpi[["date", "cpi_yoy"]],
            ],
            ignore_index=True,
        )
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")
        .reset_index(drop=True)
    )


# Build a display-only rural/urban CPI series.
# Historical dashboard component values are retained through Dec 2025;
# official current 2024=100 component indices are appended from Jan 2026.
cpi_components_display = master[["date", "cpi_rural", "cpi_urban"]].copy()
cpi_components_display["date"] = pd.to_datetime(
    cpi_components_display["date"], errors="coerce"
)

if not current_cpi_components.empty:
    first_current_component_date = current_cpi_components["date"].min()
    historical_components = cpi_components_display[
        cpi_components_display["date"] < first_current_component_date
    ].copy()

    cpi_components_display = (
        pd.concat(
            [historical_components, current_cpi_components],
            ignore_index=True,
        )
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")
        .reset_index(drop=True)
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Inflation Dashboard")

st.sidebar.caption(
    "Indian Inflation Forecasting & Price Transmission"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Inflation Trends",
        "Forecasts",
        "Model Comparison",
        "Price Transmission",
        "Diagnostics",
        "Methodology",
    ],
)

st.sidebar.divider()

st.sidebar.caption("Research target")

st.sidebar.write(
    "Monthly CPI inflation (YoY, %)"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def latest_metric(df, value_col):
    """
    Return the latest available date and value
    for a specified indicator.
    """

    if value_col not in df.columns:
        return None, None

    temp = (
        df[["date", value_col]]
        .dropna()
        .sort_values("date")
    )

    if temp.empty:
        return None, None

    row = temp.iloc[-1]

    return row["date"], row[value_col]


def clean_forecasts(df):
    """
    Prepare generic forecast dataframe.
    """

    out = df.copy()

    if "date" in out.columns:

        out["date"] = pd.to_datetime(
            out["date"],
            errors="coerce"
        )

    elif isinstance(
        out.index,
        pd.DatetimeIndex
    ):

        out = out.reset_index()

        out = out.rename(
            columns={
                out.columns[0]: "date"
            }
        )

    return out


# ============================================================
# LATEST INDICATORS
# ============================================================

# CPI latest observation comes from the display series, which
# includes the current 2024=100 CPI observations.
cpi_date, cpi_yoy = latest_metric(
    cpi_display,
    "cpi_yoy"
)

# WPI and Output PPI latest observations are taken
# from the dedicated transmission dataset because
# that dataset extends further than the historical CPI data.
wpi_date, wpi_yoy = latest_metric(
    transmission,
    "wpi_inflation"
)

ppi_date, ppi_yoy = latest_metric(
    transmission,
    "ppi_inflation"
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.markdown(
        '<div class="main-title">'
        'Indian Inflation Forecasting Dashboard'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'CPI inflation forecasting, model evaluation, '
        'and upstream price transmission analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "CPI Inflation — Latest",
            f"{cpi_yoy:.2f}%"
            if cpi_yoy is not None
            else "N/A",
        )

        if cpi_date is not None:
            st.caption(
                f"Latest available: "
                f"{cpi_date.strftime('%b %Y')}"
            )

    with col2:

        st.metric(
            "WPI Inflation — Latest",
            f"{wpi_yoy:.2f}%"
            if wpi_yoy is not None
            else "N/A",
        )

        if wpi_date is not None:
            st.caption(
                f"Latest available: "
                f"{wpi_date.strftime('%b %Y')}"
            )

    with col3:

        st.metric(
            "Output PPI — Latest",
            f"{ppi_yoy:.2f}%"
            if ppi_yoy is not None
            else "N/A",
        )

        if ppi_date is not None:
            st.caption(
                f"Latest available: "
                f"{ppi_date.strftime('%b %Y')}"
            )

    with col4:

        if not models.empty:

            best_model = models.loc[
                models["RMSE"].idxmin(),
                "Model"
            ]

        else:
            best_model = "N/A"

        st.metric(
            "Best Initial Model",
            best_model,
        )

    st.caption(
        "Each indicator displays its own latest available "
        "observation; dates are not necessarily synchronized."
    )

    st.divider()

    # --------------------------------------------------------
    # CPI INFLATION TREND
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Consumer Inflation'
        '</div>',
        unsafe_allow_html=True,
    )

    cpi_plot = (
        cpi_display[
            ["date", "cpi_yoy"]
        ]
        .dropna()
        .copy()
    )

    fig_cpi = px.line(
        cpi_plot,
        x="date",
        y="cpi_yoy",
        title="Combined CPI Inflation — YoY",
    )

    fig_cpi.add_hline(
        y=0,
        line_dash="dot",
    )

    fig_cpi.update_layout(
        xaxis_title="",
        yaxis_title="Inflation (%)",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig_cpi,
        use_container_width=True,
    )

    st.caption(
        "CPI inflation combines the historical 2012=100 series with "
        "officially published YoY inflation from the current 2024=100 "
        "series from Jan 2026 onward; no growth rate is calculated "
        "across the base-year revision."
    )

    # --------------------------------------------------------
    # RESEARCH QUESTION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="research-note">
        <strong>Research question</strong><br>
        Can wholesale and producer price information improve
        forecasts of Indian consumer inflation beyond the
        information contained in CPI's own history?
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Forecasting framework"
        )

        st.write(
            """
            The project compares statistical time-series
            forecasting models using rolling-origin /
            walk-forward validation.

            The modelling framework includes ARIMA,
            SARIMA and specifications incorporating
            WPI and Output PPI information.
            """
        )

    with col2:

        st.subheader(
            "Price transmission"
        )

        st.write(
            """
            WPI and Output PPI are examined through
            descriptive contemporaneous and lagged
            relationships with CPI inflation.

            These relationships are not interpreted as
            causal estimates.
            """
        )


# ============================================================
# INFLATION TRENDS
# ============================================================

elif page == "Inflation Trends":

    st.markdown(
        '<div class="main-title">'
        'Inflation Trends'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Explore consumer, wholesale and producer price dynamics."
    )

    # --------------------------------------------------------
    # CPI
    # --------------------------------------------------------

    cpi_plot = (
        cpi_display[
            ["date", "cpi_yoy"]
        ]
        .dropna()
        .copy()
    )

    fig_cpi = px.line(
        cpi_plot,
        x="date",
        y="cpi_yoy",
        title="Combined CPI Inflation — YoY",
    )

    fig_cpi.add_hline(
        y=0,
        line_dash="dot",
    )

    fig_cpi.update_layout(
        xaxis_title="",
        yaxis_title="Inflation (%)",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig_cpi,
        use_container_width=True,
    )

    st.caption(
        "The CPI trend uses the historical 2012=100 series through "
        "Dec 2025 and the official 2024=100 published YoY series "
        "from Jan 2026 onward."
    )

    # --------------------------------------------------------
    # RURAL / URBAN CPI
    # --------------------------------------------------------

    st.subheader(
        "CPI Index — Rural vs Urban"
    )

    component_cols = [
        col
        for col in [
            "cpi_rural",
            "cpi_urban",
        ]
        if col in cpi_components_display.columns
    ]

    if component_cols:

        rural_urban = (
            cpi_components_display[
                ["date"] + component_cols
            ]
            .dropna(
                subset=component_cols,
                how="all"
            )
            .copy()
        )

        fig_components = px.line(
            rural_urban,
            x="date",
            y=component_cols,
            title="CPI Rural and Urban Indices",
        )

        fig_components.update_layout(
            xaxis_title="",
            yaxis_title="Index",
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_components,
            use_container_width=True,
        )

        st.caption(
            "Rural and urban CPI indices use the historical dashboard "
            "component series through Dec 2025 and official 2024=100 "
            "current component indices from Jan 2026 onward."
        )

    # --------------------------------------------------------
    # WPI / PPI — CURRENT DISPLAY SERIES
    # --------------------------------------------------------

    st.subheader(
        "Upstream Price Inflation"
    )

    def load_current_upstream_inflation():
        """
        Load current 2022-23-base WPI and Output PPI monthly indices
        and calculate display-only YoY inflation.

        This is kept separate from the transmission/econometric
        datasets so updating the dashboard does not change the
        retained research sample.
        """

        results = []

        files = [
            (
                [
                    "wpi_monthly_2022_23base.xlsx",
                    "wpi_monthly_index_202608.xlsx",
                ],
                "WPI All Commodities",
            ),
            (
                [
                    "output_ppi_monthly_2022_23base.xlsx",
                    "oppi_monthly_index_202608.xlsx",
                ],
                "Output PPI",
            ),
        ]

        for candidates, label in files:
            path = None
            for filename in candidates:
                candidate = RAW_DATA_DIR / filename
                if candidate.exists():
                    path = candidate
                    break

            if path is None:
                continue

            try:
                book = pd.ExcelFile(path)
                sheet_name = book.sheet_names[0]
                raw = pd.read_excel(
                    path,
                    sheet_name=sheet_name,
                    header=None,
                )
            except Exception:
                continue

            if raw.empty:
                continue

            # Current files use the first row for month headers.
            date_headers = pd.to_datetime(
                raw.iloc[0, 4:].astype(str).str.strip(),
                format="%b-%y",
                errors="coerce",
            )

            date_cols = {
                col_idx: date_value
                for col_idx, date_value in zip(
                    range(4, raw.shape[1]),
                    date_headers,
                )
                if pd.notna(date_value)
            }

            if not date_cols:
                continue

            # Identify the All Commodities row by commodity name.
            row_mask = pd.Series(False, index=raw.index)
            for col_idx in [1, 2]:
                if col_idx < raw.shape[1]:
                    row_mask = row_mask | raw.iloc[:, col_idx].astype(str).str.strip().str.lower().eq(
                        "all commodities"
                    )

            matches = raw.loc[row_mask]
            if matches.empty:
                continue

            row = matches.iloc[0]

            values = pd.Series(
                {
                    date_value: pd.to_numeric(
                        row.iloc[col_idx],
                        errors="coerce",
                    )
                    for col_idx, date_value in date_cols.items()
                },
                dtype="float64",
            ).sort_index()

            values = values.dropna()
            if values.empty:
                continue

            temp = pd.DataFrame(
                {
                    "date": values.index,
                    "Inflation": values.pct_change(12) * 100,
                    "Indicator": label,
                }
            ).dropna()

            results.append(temp)

        if not results:
            return pd.DataFrame(
                columns=["date", "Inflation", "Indicator"]
            )

        return (
            pd.concat(results, ignore_index=True)
            .sort_values(["date", "Indicator"])
            .reset_index(drop=True)
        )

    upstream_df = load_current_upstream_inflation()

    if not upstream_df.empty:

        fig_upstream = px.line(
            upstream_df,
            x="date",
            y="Inflation",
            color="Indicator",
            title="WPI and Output PPI — YoY",
        )

        fig_upstream.update_layout(
            xaxis_title="",
            yaxis_title="Inflation (%)",
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_upstream,
            use_container_width=True,
        )

        st.caption(
            "WPI and Output PPI use the latest available monthly "
            "2022-23-base index series for display. The econometric "
            "transmission dataset remains unchanged."
        )



# ============================================================
# FORECASTS
# ============================================================

elif page == "Forecasts":

    st.markdown(
        '<div class="main-title">'
        'Inflation Forecasts'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Compare dated one-step-ahead forecasts across
        CPI-only and price-augmented specifications.
        """
    )

    forecast_df = phase11_2.copy()

    forecast_df["date"] = pd.to_datetime(
        forecast_df["date"],
        errors="coerce"
    )

    forecast_df = (
        forecast_df
        .dropna(subset=["date"])
        .sort_values("date")
    )

    available_models = (
        forecast_df["model"]
        .dropna()
        .unique()
        .tolist()
    )

    if available_models:

        selected_model = st.selectbox(
            "Forecast specification",
            available_models,
        )

        selected = forecast_df[
            forecast_df["model"] == selected_model
        ].copy()

        # ----------------------------------------------------
        # SUMMARY METRICS
        # ----------------------------------------------------

        mae = (
            selected["error"]
            .abs()
            .mean()
        )

        rmse = (
            selected["error"]
            .pow(2)
            .mean()
            ** 0.5
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Forecasts",
                len(selected),
            )

        with col2:

            st.metric(
                "MAE",
                f"{mae:.3f}",
            )

        with col3:

            st.metric(
                "RMSE",
                f"{rmse:.3f}",
            )

        st.divider()

        # ----------------------------------------------------
        # ACTUAL VS FORECAST
        # ----------------------------------------------------

        fig_forecast = go.Figure()

        fig_forecast.add_trace(
            go.Scatter(
                x=selected["date"],
                y=selected["actual_cpi"],
                mode="lines+markers",
                name="Actual CPI",
            )
        )

        fig_forecast.add_trace(
            go.Scatter(
                x=selected["date"],
                y=selected["forecast_cpi"],
                mode="lines+markers",
                name="Forecast CPI",
            )
        )

        fig_forecast.update_layout(
            title=(
                f"Actual vs Forecast — "
                f"{selected_model}"
            ),
            xaxis_title="Date",
            yaxis_title="CPI Inflation (%)",
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_forecast,
            use_container_width=True,
        )

        # ----------------------------------------------------
        # FORECAST ERRORS
        # ----------------------------------------------------

        st.subheader(
            "Forecast Errors"
        )

        error_fig = px.bar(
            selected,
            x="date",
            y="error",
            title="Forecast Error",
        )

        error_fig.add_hline(
            y=0,
            line_dash="dot",
        )

        error_fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Actual − Forecast",
        )

        st.plotly_chart(
            error_fig,
            use_container_width=True,
        )

        # ----------------------------------------------------
        # FORECAST DATA
        # ----------------------------------------------------

        st.subheader(
            "Forecast Evaluation Data"
        )

        display_df = selected[
            [
                "date",
                "model",
                "actual_cpi",
                "forecast_cpi",
                "error",
            ]
        ].copy()

        display_df["date"] = (
            display_df["date"]
            .dt.strftime("%b %Y")
        )

        display_df = display_df.rename(
            columns={
                "date": "Date",
                "model": "Model",
                "actual_cpi": "Actual CPI",
                "forecast_cpi": "Forecast CPI",
                "error": "Error",
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            """
            These are one-step-ahead forecasts from the
            Phase 11.2 small-sample forecasting-contribution
            exercise. They are not presented as the project's
            final multi-horizon production forecasts.
            """
        )

    else:

        st.warning(
            "No dated Phase 11.2 forecasts are available."
        )


# ============================================================
# MODEL COMPARISON
# ============================================================

elif page == "Model Comparison":

    st.markdown(
        '<div class="main-title">'
        'Model Comparison'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Compare statistical models using forecast accuracy metrics."
    )

    # --------------------------------------------------------
    # INITIAL MODEL COMPARISON
    # --------------------------------------------------------

    st.subheader(
        "Initial ARIMA / SARIMA Model Comparison"
    )

    if not models.empty:

        metric = st.selectbox(
            "Metric",
            [
                "RMSE",
                "MAE",
                "AIC",
                "BIC",
            ],
        )

        metric_sorted = models.sort_values(
            metric,
            ascending=True
        )

        fig = px.bar(
            metric_sorted,
            x="Model",
            y=metric,
            title=f"Model Ranking — {metric}",
            text_auto=".3f",
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title=metric,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        st.dataframe(
            models.sort_values(
                "RMSE"
            ),
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # WALK-FORWARD RESULTS
    # --------------------------------------------------------

    st.subheader(
        "Walk-Forward ARIMA / SARIMA Results"
    )

    if not walk_forward.empty:

        wf_sorted = walk_forward.sort_values(
            "RMSE"
        )

        fig_wf = px.bar(
            wf_sorted,
            x="Model",
            y="RMSE",
            title="Rolling-Origin RMSE",
            text_auto=".3f",
        )

        fig_wf.update_layout(
            xaxis_title="",
            yaxis_title="RMSE",
        )

        st.plotly_chart(
            fig_wf,
            use_container_width=True,
        )

        st.dataframe(
            wf_sorted,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # PHASE 11.2 BENCHMARK
    # --------------------------------------------------------

    st.subheader(
        "Price-Augmented Forecasting Benchmark"
    )

    st.caption(
        "One-step-ahead small-sample benchmark using the "
        "common CPI–WPI–PPI evaluation window."
    )

    phase11_summary = (
        phase11_2
        .groupby("model")
        .agg(
            MAE=(
                "error",
                lambda x: x.abs().mean()
            ),
            RMSE=(
                "error",
                lambda x: (
                    x.pow(2).mean()
                ) ** 0.5
            ),
            Forecasts=(
                "error",
                "count"
            ),
        )
        .reset_index()
        .sort_values("RMSE")
    )

    st.dataframe(
        phase11_summary,
        use_container_width=True,
        hide_index=True,
    )

    fig_phase11 = px.bar(
        phase11_summary,
        x="model",
        y="RMSE",
        text_auto=".3f",
        title="One-Step-Ahead RMSE",
    )

    fig_phase11.update_layout(
        xaxis_title="",
        yaxis_title="RMSE",
    )

    st.plotly_chart(
        fig_phase11,
        use_container_width=True,
    )

    st.caption(
        "The price-augmented benchmark is exploratory because "
        "the common evaluation sample is small."
    )


# ============================================================
# PRICE TRANSMISSION
# ============================================================

elif page == "Price Transmission":

    st.markdown(
        '<div class="main-title">'
        'Price Transmission'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Explore the relationship between upstream prices
        and CPI inflation.
        """
    )

    # --------------------------------------------------------
    # COMMON SAMPLE
    # --------------------------------------------------------

    common = common_yoy.copy()

    # Temporary QA readout: confirms exactly which common-sample data
    # reached the dashboard before chart rendering.
    if "date" in common.columns and not common.empty:
        common["date"] = pd.to_datetime(
            common["date"],
            errors="coerce"
        )
        st.caption(
            f"QA — Common sample loaded: {len(common)} rows | "
            f"{common['date'].min():%b %Y} → {common['date'].max():%b %Y}"
        )

    if "date" in common.columns:

        common["date"] = pd.to_datetime(
            common["date"],
            errors="coerce"
        )

        common = common.sort_values(
            "date"
        )

    st.subheader(
        "CPI, WPI and Output PPI — Common Sample"
    )

    required = [
        "date",
        "cpi_inflation",
        "wpi_inflation",
        "ppi_inflation",
    ]

    if all(
        col in common.columns
        for col in required
    ):

        common_plot = (
            common[
                required
            ]
            .dropna()
        )

        fig = px.line(
            common_plot,
            x="date",
            y=[
                "cpi_inflation",
                "wpi_inflation",
                "ppi_inflation",
            ],
            title="CPI, WPI and Output PPI Inflation",
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Inflation (%)",
            hovermode="x unified",
        )

        # Show the complete Apr 2024-Dec 2025 common sample
        # clearly on the x-axis instead of letting Plotly omit
        # the later date labels due to automatic tick selection.
        fig.update_xaxes(
            dtick="M3",
            tickformat="%b %Y",
            range=[
                pd.Timestamp("2024-03-15"),
                pd.Timestamp("2026-01-15"),
            ],
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        if not common_plot.empty:
            st.caption(
                f"Common sample shown: {common_plot['date'].min():%b %Y} to "
                f"{common_plot['date'].max():%b %Y} — "
                f"{len(common_plot)} complete observations."
            )

    # --------------------------------------------------------
    # LAGGED CORRELATIONS
    # --------------------------------------------------------

    st.subheader(
        "Lagged Correlations with CPI Inflation"
    )

    variable_map = {
        "wpi_inflation":
            "WPI All Commodities",
        "wpi_primary_inflation":
            "WPI Primary Articles",
        "wpi_fuel_inflation":
            "WPI Fuel & Power",
        "wpi_manufacturing_inflation":
            "WPI Manufactured Products",
        "ppi_inflation":
            "Output PPI",
    }

    if not lagged.empty:

        lag_plot = lagged.copy()

        lag_plot["Indicator"] = (
            lag_plot["variable"]
            .map(variable_map)
            .fillna(
                lag_plot["variable"]
            )
        )

        indicators = (
            lag_plot["Indicator"]
            .dropna()
            .unique()
            .tolist()
        )

        if indicators:

            selected_indicator = st.selectbox(
                "Indicator",
                indicators,
            )

            selected = lag_plot[
                lag_plot["Indicator"]
                == selected_indicator
            ]

            fig_lag = px.line(
                selected,
                x="lag_months",
                y="correlation",
                markers=True,
                title=(
                    f"{selected_indicator} — "
                    "Correlation with CPI"
                ),
            )

            fig_lag.add_hline(
                y=0,
                line_dash="dot",
            )

            fig_lag.update_layout(
                xaxis_title="Lag (months)",
                yaxis_title="Correlation",
            )

            st.plotly_chart(
                fig_lag,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # LAG SUMMARY
    # --------------------------------------------------------

    st.subheader(
        "Maximum Absolute Lagged Correlation"
    )

    if not lagged_summary.empty:

        summary = lagged_summary.copy()

        summary["Indicator"] = (
            summary["variable"]
            .map(variable_map)
            .fillna(
                summary["variable"]
            )
        )

        summary = summary[
            [
                "Indicator",
                "lag_months",
                "n",
                "correlation",
            ]
        ]

        summary = summary.rename(
            columns={
                "lag_months":
                    "Lag (months)",
                "n":
                    "Observations",
                "correlation":
                    "Correlation",
            }
        )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

    st.info(
        """
        These are descriptive correlations rather than
        causal estimates. The valid common CPI-WPI-Output
        PPI YoY sample contains only 21 complete observations.
        """
    )


# ============================================================
# DIAGNOSTICS
# ============================================================

elif page == "Diagnostics":

    st.markdown(
        '<div class="main-title">'
        'Econometric Diagnostics'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Model and residual diagnostics from the
        forecasting workflow.
        """
    )

    # --------------------------------------------------------
    # STATIONARITY
    # --------------------------------------------------------

    st.subheader(
        "Stationarity Diagnostics"
    )

    if not diagnostics.empty:

        st.dataframe(
            diagnostics,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # RESIDUAL DIAGNOSTICS
    # --------------------------------------------------------

    st.subheader(
        "Residual Diagnostics"
    )

    if not residuals.empty:

        st.dataframe(
            residuals,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        """
        Diagnostic results should be interpreted jointly
        with the underlying model specifications and
        forecasting validation.
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

elif page == "Methodology":

    st.markdown(
        '<div class="main-title">'
        'Methodology'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ## Research Question

        **Can wholesale and producer price information improve
        forecasts of Indian consumer inflation beyond the
        information contained in CPI's own history?**

        ## Target Variable

        Monthly Combined CPI inflation measured as the
        year-on-year percentage change.

        ## Forecast Horizons

        The research design considers:

        - 1-month ahead
        - 3-month ahead
        - 6-month ahead

        ## Model Framework

        The modelling workflow includes:

        - Naïve / seasonal benchmarks
        - ARIMA
        - SARIMA
        - ETS
        - SARIMAX with WPI
        - SARIMAX with WPI and Output PPI
        - XGBoost benchmark

        ## Validation

        Model performance is evaluated using
        **rolling-origin / walk-forward validation**.

        Primary metrics include:

        - Mean Absolute Error (MAE)
        - Root Mean Squared Error (RMSE)

        ## Price Transmission

        WPI and Output PPI are transformed to their
        year-on-year inflation rates before comparison
        with CPI.

        Lagged correlations are examined over a
        0–6 month window.

        ## Important Limitation

        The currently retained CPI-WPI-Output PPI data
        provide only 21 complete common YoY observations.

        Therefore, the transmission analysis is exploratory
        and formal Granger-causality inference is not
        presented as a headline result.

        ## Interpretation Principle

        **Correlation does not establish causality, and
        contemporaneous association does not automatically
        imply incremental forecasting value.**

        The dashboard therefore separates:

        **Price co-movement**

        from

        **Incremental forecasting performance.**
        """
    )

    st.divider()

    st.caption(
        "Indian Inflation Forecasting & Price Transmission Dashboard"
    )

    st.caption(
        "Research and portfolio project"
    )
