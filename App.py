# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# -----------------------------
# Functions
# -----------------------------

@st.cache_data
def load_data():
    # Load data from CSV/Delta-exported files
    df_clean = pd.read_csv("cleaned_exchange_rates.csv", parse_dates=['date'])
    df_stats = pd.read_csv("currency_statistics.csv")
    df_daily = pd.read_csv("daily_summary.csv", parse_dates=['date'])
    df_clean['date_only'] = df_clean['date'].dt.date
    return df_clean, df_stats, df_daily

# -----------------------------
# Load data
# -----------------------------
df_clean, df_stats, df_daily = load_data()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

currencies = st.sidebar.multiselect(
    "Select Currencies",
    options=df_clean['target_currency'].unique(),
    default=['USD']
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=df_clean['date_only'].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df_clean['date_only'].max()
)

# Filter data
df_filtered = df_clean[
    (df_clean['target_currency'].isin(currencies)) &
    (df_clean['date_only'] >= start_date) &
    (df_clean['date_only'] <= end_date)
]

# -----------------------------
# Main Dashboard
# -----------------------------
st.title("💱 Currency Analytics Dashboard")

# KPI Card: Latest EUR/USD Rate
st.subheader("Latest EUR/USD Rate")
if not df_filtered[df_filtered['target_currency'] == 'USD'].empty:
    latest_eur_usd = df_filtered[df_filtered['target_currency'] == 'USD'].sort_values('date', ascending=False).iloc[0]
    st.metric(
        label="EUR/USD",
        value=latest_eur_usd['exchange_rate_rounded']
    )
else:
    st.warning("No data available for EUR/USD in the selected date range.")

# Line chart: EUR/USD trend
st.subheader("EUR/USD Trend")
eur_usd_trend = df_filtered[df_filtered['target_currency'] == 'USD'].sort_values('date')
if not eur_usd_trend.empty:
    st.line_chart(eur_usd_trend.set_index('date')['exchange_rate_rounded'])
else:
    st.warning("No EUR/USD trend data to display.")

# Bar chart: Currency Volatility
st.subheader("Currency Volatility")
st.bar_chart(df_stats.set_index('target_currency')['volatility'])

# Daily summary table
st.subheader("Daily Summary")
st.dataframe(
    df_filtered[[
        'date',
        'target_currency',
        'exchange_rate_rounded',
        'daily_change_percent'
    ]]
)
