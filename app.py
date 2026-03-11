import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Vehicle Telemetry Dashboard", layout="wide")

st.title("🚗 Vehicle Telemetry Analytics Dashboard")

uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:

    # Read file safely
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error("File could not be read.")
        st.stop()

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # Required columns
    required_cols = [
        "createdAt",
        "battery_state_of_charge",
        "vehicle_calculated_odo",
        "controller_vehicle_status"
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
        st.stop()

    # Convert time column
    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")

    # Filter vehicle status = 2
    df_filtered = df[df["controller_vehicle_status"] == 2]

    if df_filtered.empty:
        st.warning("No data where controller_vehicle_status = 2")
        st.stop()

    # Sort by time
    df_filtered = df_filtered.sort_values("createdAt")

    # KPI Metrics
    st.subheader("Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(df_filtered))
    col2.metric("Average SOC", round(df_filtered["battery_state_of_charge"].mean(), 2))
    col3.metric("Max Odometer", round(df_filtered["vehicle_calculated_odo"].max(), 2))

    st.divider()

    # Single Chart with Dual Axis
    st.subheader("SOC and Odometer Trend")

    fig = go.Figure()

    # SOC Line
    fig.add_trace(
        go.Scatter(
            x=df_filtered["createdAt"],
            y=df_filtered["battery_state_of_charge"],
            name="SOC (%)",
            yaxis="y1",
            mode="lines"
        )
    )

    # Odometer Line
    fig.add_trace(
        go.Scatter(
            x=df_filtered["createdAt"],
            y=df_filtered["vehicle_calculated_odo"],
            name="Odometer",
            yaxis="y2",
            mode="lines"
        )
    )

    fig.update_layout(
        xaxis=dict(title="Time"),
        yaxis=dict(
            title="Battery SOC (%)",
            side="left"
        ),
        yaxis2=dict(
            title="Odometer",
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Filtered Data Table")
    st.dataframe(df_filtered)
                 
