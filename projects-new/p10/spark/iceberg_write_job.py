"""Spark job for writing data to Iceberg tables with partitioning."""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year, month
import argparse

def create_spark_session(app_name: str = "IcebergWriteJob") -> SparkSession:
    """Create Spark session with Iceberg configuration."""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
        .config("spark.sql.catalog.glue_catalog.warehouse", "s3://my-data-lake/warehouse/") \
        .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
        .getOrCreate()


def write_bronze_table(
    spark: SparkSession,
    source_path: str,
    table_name: str = "glue_catalog.bronze.raw_events"
):
    """Read raw data and write to bronze Iceberg table."""
    print(f"Reading data from {source_path}")

    # Read source data
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(source_path)

    # Add metadata columns
    df = df.withColumn("ingestion_timestamp", col("current_timestamp()"))

    # Write to Iceberg table (create if not exists)
    df.writeTo(table_name) \
        .using("iceberg") \
        .tableProperty("format-version", "2") \
        .tableProperty("write.metadata.compression-codec", "gzip") \
        .createOrReplace()

    print(f"Written {df.count()} records to {table_name}")


def append_to_silver_table(
    spark: SparkSession,
    source_table: str = "glue_catalog.bronze.raw_events",
    target_table: str = "glue_catalog.silver.events",
    partition_col: str = "date"
):
    """Transform bronze data and append to partitioned silver table."""
    print(f"Transforming {source_table} to {target_table}")

    # Read from bronze
    df = spark.table(source_table)

    # Cleansing and transformations
    df = df.dropDuplicates(["id"]) \
        .filter(col("status").isNotNull()) \
        .withColumn("date", to_date(col("timestamp"))) \
        .withColumn("year", year(col("date"))) \
        .withColumn("month", month(col("date")))

    # Write to partitioned silver table
    df.writeTo(target_table) \
        .using("iceberg") \
        .partitionedBy("year", "month") \
        .tableProperty("format-version", "2") \
        .tableProperty("write.distribution-mode", "hash") \
        .option("write.format.default", "parquet") \
        .option("write.parquet.compression-codec", "snappy") \
        .append()

    print(f"Appended {df.count()} records to {target_table}")


def merge_into_gold_table(
    spark: SparkSession,
    source_table: str = "glue_catalog.silver.events",
    target_table: str = "glue_catalog.gold.daily_aggregates"
):
    """Perform MERGE (upsert) into gold table."""
    print(f"Merging from {source_table} to {target_table}")

    # Aggregate silver data
    agg_df = spark.sql(f"""
        SELECT
            date,
            category,
            COUNT(*) as event_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM {source_table}
        WHERE date >= current_date() - INTERVAL 1 DAY
        GROUP BY date, category
    """)

    # Create temporary view for merge
    agg_df.createOrReplaceTempView("source_data")

    # Perform merge (upsert)
    spark.sql(f"""
        MERGE INTO {target_table} t
        USING source_data s
        ON t.date = s.date AND t.category = s.category
        WHEN MATCHED THEN
            UPDATE SET
                event_count = s.event_count,
                total_amount = s.total_amount,
                avg_amount = s.avg_amount,
                updated_at = current_timestamp()
        WHEN NOT MATCHED THEN
            INSERT (date, category, event_count, total_amount, avg_amount, created_at)
            VALUES (s.date, s.category, s.event_count, s.total_amount, s.avg_amount, current_timestamp())
    """)

    print(f"Merge complete for {target_table}")


def main():
    parser = argparse.ArgumentParser(description="Iceberg write job")
    parser.add_argument("--source", required=True, help="Source data path (S3)")
    parser.add_argument("--table", required=True, help="Target Iceberg table")
    parser.add_argument("--mode", default="append", choices=["append", "overwrite", "merge"])
    args = parser.parse_args()

    spark = create_spark_session()

    try:
        if args.mode == "append":
            write_bronze_table(spark, args.source, args.table)
        elif args.mode == "overwrite":
            write_bronze_table(spark, args.source, args.table)
        elif args.mode == "merge":
            merge_into_gold_table(spark, args.source, args.table)

        print("Job completed successfully")
    except Exception as e:
        print(f"Job failed: {e}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
