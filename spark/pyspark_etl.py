"""PySpark ETL demonstration for Databricks-ready scaling."""

from __future__ import annotations


def main() -> None:
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import avg, col, dayofweek, hour, month, to_timestamp, year
    except ImportError:
        print("PySpark is not installed. Install pyspark or run this in Databricks to execute the ETL.")
        return

    spark = SparkSession.builder.appName("energy-intelligence-platform-etl").getOrCreate()
    raw_path = "data/raw/PJME_hourly.csv"
    output_path = "data/processed/spark_demand_features"

    df = spark.read.option("header", True).option("inferSchema", True).csv(raw_path)
    timestamp_col = df.columns[0]
    demand_col = df.columns[1]
    clean = (
        df.select(to_timestamp(col(timestamp_col)).alias("datetime"), col(demand_col).cast("double").alias("demand_mw"))
        .where(col("datetime").isNotNull() & col("demand_mw").isNotNull())
        .withColumn("hour", hour("datetime"))
        .withColumn("day_of_week", dayofweek("datetime"))
        .withColumn("month", month("datetime"))
        .withColumn("year", year("datetime"))
    )
    daily = clean.groupBy("year", "month").agg(avg("demand_mw").alias("avg_demand_mw"))
    clean.write.mode("overwrite").parquet(output_path)
    daily.write.mode("overwrite").parquet("data/processed/spark_monthly_demand")
    spark.stop()
    print("Spark ETL complete. In Databricks, replace paths with DBFS/Unity Catalog locations and optionally write Delta.")


if __name__ == "__main__":
    main()
