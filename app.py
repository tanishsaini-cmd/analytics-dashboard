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

    # ==============================
    # ⏱ Convert datetime
    # ==============================
    if "createdat" in df.columns:
        df["createdat"] = pd.to_datetime(df["createdat"], errors="coerce")
    else:
        st.error("createdAt column not found")
        st.stop()

    # Sort full dataset first
    df = df.sort_values("createdat")

    # ==============================
    # 🚦 Detect status column
    # ==============================
    if "controllervehiclestatus" in df.columns:
        status_col = "controllervehiclestatus"
    elif "vehiclestate" in df.columns:
        status_col = "vehiclestate"
    else:
        st.error("No vehicle status column found")
        st.stop()

    # ==============================
    # 🎯 Find FIRST & LAST state = 2
    # ==============================
    state_2_df = df[df[status_col] == 2]

    if state_2_df.empty:
        st.warning("No vehicleState = 2 found")
        st.stop()

    first_index = state_2_df.index[0]
    last_index = state_2_df.index[-1]

    # Slice continuous data
    df_filtered = df.loc[first_index:last_index].copy()

    # ==============================
    # 🧹 Clean required columns
    # ==============================
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

    # Drop null ODO
    df_filtered = df_filtered.dropna(subset=["vehiclecalculatedodo"])

    if df_filtered.empty:
        st.warning("No valid ODO data")
        st.stop()

    # ==============================
    # 🔋 SOC Calculations
    # ==============================
    start_soc = df_filtered["batterystateofcharge"].iloc[0]
    end_soc = df_filtered["batterystateofcharge"].iloc[-1]
    soc_consumed = round(start_soc - end_soc, 2)

    # ==============================
    # 🚗 ODO Calculations (CORE LOGIC)
    # ==============================
    start_odo = df_filtered["vehiclecalculatedodo"].iloc[0]
    end_odo = df_filtered["vehiclecalculatedodo"].iloc[-1]

    basic_distance = end_odo - start_odo

    # Smart diff method (handles reset/jumps)
    df_filtered["odo_diff"] = df_filtered["vehiclecalculatedodo"].diff()
    smart_distance = df_filtered[df_filtered["odo_diff"] > 0]["odo_diff"].sum()

    # Choose best
    if basic_distance < 0:
        st.warning("⚠️ Odometer reset detected → Using smart calculation")
        vehicle_drive = smart_distance
    else:
        vehicle_drive = basic_distance

    # Round
    start_odo = round(start_odo, 2)
    end_odo = round(end_odo, 2)
    vehicle_drive = round(vehicle_drive, 2)

    # ==============================
    # ⚡ Current
    # ==============================
    avg_amp = round(df_filtered["batterycurrent"].mean(), 2)

    # ==============================
    # 📊 Metrics UI
    # ==============================
    st.subheader("Key Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total Records", len(df_filtered))
    col2.metric("SOC Consumed (%)", soc_consumed)
    col3.metric("Start ODO", start_odo)
    col4.metric("End ODO", end_odo)
    col5.metric("Vehicle Drive (km)", vehicle_drive)
    col6.metric("Average Current (A)", avg_amp)

    st.divider()

    # ==============================
    # 📈 Chart 1: SOC + ODO
    # ==============================
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

    # ==============================
    # 📈 Chart 2: Speed + ODO
    # ==============================
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

else:
    st.info("👈 Upload telemetry files to get started")
