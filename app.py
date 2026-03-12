import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Vehicle Telemetry Dashboard", layout="wide")

st.title("🚗 Vehicle Telemetry Analytics Dashboard")

# Sidebar uploader
st.sidebar.header("Upload Telemetry File")

uploaded_file = st.sidebar.file_uploader(
    "Drag and drop Excel or CSV file",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except:
        st.error("File could not be read.")
        st.stop()

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

    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")

    df_filtered = df[df["controller_vehicle_status"] == 2]

    if df_filtered.empty:
        st.warning("No records where controller_vehicle_status = 2")
        st.stop()

    df_filtered = df_filtered.sort_values("createdAt")

    # SOC calculations
    start_soc = df_filtered["battery_state_of_charge"].iloc[0]
    end_soc = df_filtered["battery_state_of_charge"].iloc[-1]
    soc_consumed = round(start_soc - end_soc, 2)

    # ODO calculations
    start_odo = round(df_filtered["vehicle_calculated_odo"].iloc[0], 2)
    end_odo = round(df_filtered["vehicle_calculated_odo"].iloc[-1], 2)

    vehicle_drive = round(end_odo - start_odo, 2)

    st.subheader("Key Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Records", len(df_filtered))
    col2.metric("SOC Consumed (%)", soc_consumed)
    col3.metric("Start ODO", start_odo)
    col4.metric("End ODO", end_odo)
    col5.metric("Vehicle Drive (km)", vehicle_drive)

    st.divider()

    st.subheader("SOC and Odometer Trend")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_filtered["createdAt"],
            y=df_filtered["battery_state_of_charge"],
            name="SOC (%)",
            yaxis="y1",
            mode="lines"
        )
    )

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
            title="SOC (%)",
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
