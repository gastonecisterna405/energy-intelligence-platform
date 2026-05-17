# Databricks notebook source
# COMMAND ----------
# Load raw demand data
from pyspark.sql import functions as F

raw_path = "dbfs:/FileStore/energy/raw/PJME_hourly.csv"
df = spark.read.option("header", True).option("inferSchema", True).csv(raw_path)

# COMMAND ----------
# Clean data
timestamp_col = df.columns[0]
demand_col = df.columns[1]
clean = (
    df.select(F.to_timestamp(F.col(timestamp_col)).alias("datetime"), F.col(demand_col).cast("double").alias("demand_mw"))
    .where(F.col("datetime").isNotNull() & F.col("demand_mw").isNotNull())
)

# COMMAND ----------
# Create features
features = (
    clean.withColumn("hour", F.hour("datetime"))
    .withColumn("day_of_week", F.dayofweek("datetime"))
    .withColumn("month", F.month("datetime"))
    .withColumn("year", F.year("datetime"))
)

# COMMAND ----------
# Save Delta/Parquet
features.write.mode("overwrite").format("delta").saveAsTable("energy_intelligence.demand_features")

# COMMAND ----------
# Run basic aggregations
display(features.groupBy("month").agg(F.avg("demand_mw").alias("avg_demand_mw")).orderBy("month"))
