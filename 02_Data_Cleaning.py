# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.window import Window

df = spark.table("currency_project.raw_data.historical_rates")

print(f"Loaded {df.count()} records")

# Schema validation (A+ addition)
required_cols = {"date","base_currency","target_currency","exchange_rate"}
if not required_cols.issubset(df.columns):
    raise Exception("❌ Schema mismatch in raw table.")

df_clean = (
    df
    .withColumn("date", to_date("date"))
    .withColumn("exchange_rate_rounded", round(col("exchange_rate"), 4))
    .withColumn("rate_category",
                when(col("exchange_rate") < 0.5, "Very Low")
               .when(col("exchange_rate") < 1, "Low")
               .when(col("exchange_rate") < 2, "Medium")
               .when(col("exchange_rate") < 5, "High")
               .otherwise("Very High"))
    .withColumn("is_major_currency",
                col("target_currency").isin(["USD","GBP","JPY","CHF","CAD","AUD"]))
    .na.drop()
)

# Window for daily changes
window_spec = Window.partitionBy("target_currency").orderBy("date")

df_clean = df_clean \
    .withColumn("prev_rate", lag("exchange_rate").over(window_spec)) \
    .withColumn("daily_change", col("exchange_rate") - col("prev_rate")) \
    .withColumn("daily_change_percent",
                when(col("prev_rate").isNotNull(),
                     (col("exchange_rate") - col("prev_rate")) / col("prev_rate") * 100)
                .otherwise(0))

df_clean.write.format("delta").mode("overwrite").saveAsTable(
    "currency_project.cleaned_data.exchange_rates"
)

# Analytics tables
currency_stats = df_clean.groupBy("target_currency").agg(
    count("*").alias("record_count"),
    min("exchange_rate").alias("min_rate"),
    max("exchange_rate").alias("max_rate"),
    avg("exchange_rate").alias("avg_rate"),
    stddev("exchange_rate").alias("volatility"),
    avg("daily_change_percent").alias("avg_daily_change")
)

currency_stats.write.format("delta").mode("overwrite").saveAsTable(
    "currency_project.analytics.currency_statistics"
)

daily_summary = df_clean.groupBy("date","target_currency").agg(
    avg("exchange_rate").alias("daily_avg"),
    min("exchange_rate").alias("daily_min"),
    max("exchange_rate").alias("daily_max"),
    avg("daily_change_percent").alias("avg_daily_change")
)

daily_summary.write.format("delta").mode("overwrite").saveAsTable(
    "currency_project.analytics.daily_summary"
)

print("✅ Cleaning + Analytics Layer Complete")
