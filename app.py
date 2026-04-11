import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Vehicle Telemetry Dashboard", layout="wide")

st.title("🚗 Vehicle Telemetry Analytics Dashboard")

st.sidebar.header("Upload Telemetry Files")

uploaded_files = st.sidebar.file_uploader(
    "Drag and drop Excel or CSV files",
    type=["xlsx", "csv"],
    accept_multiple_files=True
)

if uploaded_files:

    dataframes = []

    for file in uploaded_files:

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Normalize column names
            df.columns = (
                df.columns
                .str.lower()
                .str.replace(" ", "", regex=False)
                .str.replace("_", "", regex=False)
            )

            dataframes.append(df)

        except:
            st.error(f"File could not be read: {file.name}")
            st.stop()

    df = pd.concat(dataframes, ignore_index=True)

    # Convert datetime
    if "createdat" in df.columns:
        df["createdat"] = pd.to_datetime(df["createdat"], errors="coerce")
    else:
        st.error("createdAt column not found")
        st.stop()

    # Smart filtering logic
    if "controllervehiclestatus" in df.columns:
        df_filtered = df[df["controllervehiclestatus"] == 2]

    elif "vehiclestate" in df.columns:
        df_filtered = df[df["vehiclestate"] == 2]

    else:
        st.error("Neither controller_vehicle_status nor vehicleState column found")
        st.stop()

    if df_filtered.empty:
        st.warning("No matching records after filtering")
        st.stop()

    df_filtered = df_filtered.sort_values("createdat")

    # Required analytics columns
    required_cols = [
        "batterystateofcharge",
        "vehiclecalculatedodo",
        "controllerspeed",
        "batterycurrent"
    ]

    missing_cols = [col for col in required_cols if col not in df_filtered.columns]

    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
        st.stop()

    # SOC calculations
    start_soc = df_filtered["batterystateofcharge"].iloc[0]
    end_soc = df_filtered["batterystateofcharge"].iloc[-1]

    soc_consumed = round(start_soc - end_soc, 2)

    # ODO calculations
    start_odo = round(df_filtered["vehiclecalculatedodo"].iloc[0], 2)
    end_odo = round(df_filtered["vehiclecalculatedodo"].iloc[-1], 2)

    vehicle_drive = round(end_odo - start_odo, 2)

    # Average current
    avg_amp = round(df_filtered["batterycurrent"].mean(), 2)

    st.subheader("Key Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total Records", len(df_filtered))
    col2.metric("SOC Consumed (%)", soc_consumed)
    col3.metric("Start ODO", start_odo)
    col4.metric("End ODO", end_odo)
    col5.metric("Vehicle Drive (km)", vehicle_drive)
    col6.metric("Average Current (A)", avg_amp)

    st.divider()

    # Chart 1
    st.subheader("SOC and Odometer Trend")

    fig1 = go.Figure()

    fig1.add_trace(
        go.Scatter(
            x=df_filtered["createdat"],
            y=df_filtered["batterystateofcharge"],
            name="SOC (%)",
            yaxis="y1",
            mode="lines"
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=df_filtered["createdat"],
            y=df_filtered["vehiclecalculatedodo"],
            name="Odometer",
            yaxis="y2",
            mode="lines"
        )
    )

    fig1.update_layout(
        xaxis=dict(title="Time"),
        yaxis=dict(title="SOC (%)"),
        yaxis2=dict(
            title="Odometer",
            overlaying="y",
            side="right"
        ),
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # Chart 2
    st.subheader("Vehicle Speed and Odometer Over Time")

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=df_filtered["createdat"],
            y=df_filtered["controllerspeed"],
            name="Speed",
            yaxis="y1",
            mode="lines"
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=df_filtered["createdat"],
            y=df_filtered["vehiclecalculatedodo"],
            name="Odometer",
            yaxis="y2",
            mode="lines"
        )
    )

    fig2.update_layout(
        xaxis=dict(title="Time"),
        yaxis=dict(title="Speed"),
        yaxis2=dict(
            title="Odometer",
            overlaying="y",
            side="right"
        ),
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

