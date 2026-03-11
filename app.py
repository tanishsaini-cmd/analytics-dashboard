import streamlit as st
import pandas as pd

st.title("Excel Analytics Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx","csv"])

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df)

    st.subheader("Basic Metrics")

    st.write("Total Rows:", len(df))
    st.write("Total Columns:", len(df.columns))

    numeric_columns = df.select_dtypes(include='number')

    if not numeric_columns.empty:
        st.subheader("Sum of Numeric Columns")
        st.write(numeric_columns.sum())

        st.subheader("Charts")
        st.line_chart(numeric_columns)