# Databricks notebook source
df = spark.table("currency_project.cleaned_data.exchange_rates")
df_stats = spark.table("currency_project.analytics.currency_statistics")

print("Schema:")
df.printSchema()

print("Currency counts:")
display(df.groupBy("target_currency").count())

print("Daily changes distribution:")
display(df.select("daily_change_percent"))

# Chart: EUR/USD trend
eur_usd = df.filter("target_currency = 'USD'")
display(eur_usd)

# Chart: Volatility comparison
display(df_stats)
