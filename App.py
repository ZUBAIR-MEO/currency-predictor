# Databricks notebook source
# MAGIC %pip install streamlit pandas plotly
# MAGIC
# MAGIC import streamlit as st
# MAGIC import pandas as pd
# MAGIC
# MAGIC # Load data from Delta tables
# MAGIC df_clean = spark.table(
# MAGIC     "currency_project.cleaned_data.exchange_rates"
# MAGIC ).toPandas()
# MAGIC df_stats = spark.table(
# MAGIC     "currency_project.analytics.currency_statistics"
# MAGIC ).toPandas()
# MAGIC df_daily = spark.table(
# MAGIC     "currency_project.analytics.daily_summary"
# MAGIC ).toPandas()
# MAGIC
# MAGIC # Sidebar filters
# MAGIC st.sidebar.header("Filters")
# MAGIC currencies = st.sidebar.multiselect(
# MAGIC     "Select Currencies",
# MAGIC     options=df_clean['target_currency'].unique(),
# MAGIC     default=['USD']
# MAGIC )
# MAGIC
# MAGIC start_date = st.sidebar.date_input(
# MAGIC     "Start Date",
# MAGIC     value=df_clean['date'].min()
# MAGIC )
# MAGIC end_date = st.sidebar.date_input(
# MAGIC     "End Date",
# MAGIC     value=df_clean['date'].max()
# MAGIC )
# MAGIC
# MAGIC # Convert DataFrame date column to datetime.date for comparison
# MAGIC df_clean['date'] = pd.to_datetime(df_clean['date'])
# MAGIC df_clean['date_only'] = df_clean['date'].dt.date
# MAGIC
# MAGIC df_filtered = df_clean[
# MAGIC     (df_clean['target_currency'].isin(currencies)) &
# MAGIC     (df_clean['date_only'] >= start_date) &
# MAGIC     (df_clean['date_only'] <= end_date)
# MAGIC ]
# MAGIC
# MAGIC # Main Dashboard
# MAGIC st.title("💱 Currency Analytics Dashboard")
# MAGIC
# MAGIC # KPI Cards
# MAGIC st.subheader("Latest EUR/USD Rate")
# MAGIC latest_eur_usd = df_filtered[
# MAGIC     df_filtered['target_currency'] == 'USD'
# MAGIC ].sort_values('date', ascending=False).iloc[0]
# MAGIC st.metric(
# MAGIC     label="EUR/USD",
# MAGIC     value=latest_eur_usd['exchange_rate_rounded']
# MAGIC )
# MAGIC
# MAGIC # Line chart: EUR/USD trend
# MAGIC st.subheader("EUR/USD Trend")
# MAGIC eur_usd_trend = df_filtered[
# MAGIC     df_filtered['target_currency'] == 'USD'
# MAGIC ].sort_values('date')
# MAGIC st.line_chart(
# MAGIC     eur_usd_trend.set_index('date')['exchange_rate_rounded']
# MAGIC )
# MAGIC
# MAGIC # Bar chart: Currency volatility
# MAGIC st.subheader("Currency Volatility")
# MAGIC st.bar_chart(
# MAGIC     df_stats.set_index('target_currency')['volatility']
# MAGIC )
# MAGIC
# MAGIC # Daily summary table
# MAGIC st.subheader("Daily Summary")
# MAGIC st.dataframe(
# MAGIC     df_filtered[
# MAGIC         [
# MAGIC             'date',
# MAGIC             'target_currency',
# MAGIC             'exchange_rate_rounded',
# MAGIC             'daily_change_percent'
# MAGIC         ]
# MAGIC     ]
# MAGIC )