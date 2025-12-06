# Databricks notebook source
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql.functions import monotonically_increasing_id

df = spark.table("currency_project.cleaned_data.exchange_rates") \
    .filter("target_currency = 'USD'") \
    .orderBy("date")

df = df.withColumn("time_index", monotonically_increasing_id())

assembler = VectorAssembler(inputCols=["time_index"], outputCol="features")
train_data = assembler.transform(df).select("features","exchange_rate")

lr = LinearRegression(featuresCol="features", labelCol="exchange_rate")
model = lr.fit(train_data)

print("Model coefficients:", model.coefficients)

# Predict next 7 days
future = spark.range(df.count(), df.count()+7).toDF("time_index")
future = assembler.transform(future)
predictions = model.transform(future)

display(predictions)
