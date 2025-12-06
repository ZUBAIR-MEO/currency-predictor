# Databricks notebook source
spark.sql("CREATE CATALOG IF NOT EXISTS currency_project")
spark.sql("CREATE SCHEMA IF NOT EXISTS currency_project.raw_data")
spark.sql("CREATE SCHEMA IF NOT EXISTS currency_project.cleaned_data")
spark.sql("CREATE SCHEMA IF NOT EXISTS currency_project.analytics")

print("✅ Database setup complete")
display(spark.sql("SHOW SCHEMAS IN currency_project"))
