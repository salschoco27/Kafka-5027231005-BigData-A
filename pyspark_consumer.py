# gudang_monitoring/app/pyspark_consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, expr, when, window, lit, concat
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType

KAFKA_BROKERS_PYSPARK = "kafka:9092" # Inside Docker network
SUHU_TOPIC = "sensor-suhu-gudang"
KELEMBABAN_TOPIC = "sensor-kelembaban-gudang"

# Define schemas for the incoming JSON data
# Note: Kafka messages from producers don't have timestamps, Spark adds one upon reading.
schema_suhu = StructType([
    StructField("gudang_id", StringType(), True),
    StructField("suhu", IntegerType(), True) # Or DoubleType if more precision
])

schema_kelembaban = StructType([
    StructField("gudang_id", StringType(), True),
    StructField("kelembaban", IntegerType(), True) # Or DoubleType
])

def process_critical_alerts_batch(batch_df, epoch_id):
    """
    Processes a micro-batch of joined data to print critical alerts and statuses.
    """
    if batch_df.count() == 0:
        return

    print(f"\n--- Batch {epoch_id} ---")
    
    # Collect data to driver for printing (for small batch sizes in demo)
    # In production, you'd write this to another sink (e.g., database, another Kafka topic)
    alerts_data = batch_df.collect()

    for row in alerts_data:
        gudang_id = row.gudang_id
        suhu = row.suhu
        kelembaban = row.kelembaban
        status_msg = row.status_message

        if "Bahaya tinggi!" in status_msg:
            print("[PERINGATAN KRITIS]")
            print(f"Gudang {gudang_id}:")
            print(f"  - Suhu: {suhu}°C")
            print(f"  - Kelembaban: {kelembaban}%")
            print(f"  - Status: {status_msg}")
        else:
            # Example of how to print other statuses from the joined stream
            print(f"[INFO GUDANG {gudang_id}] Suhu: {suhu}°C, Kelembaban: {kelembaban}%, Status: {status_msg}")
    print("--- End Batch ---\n")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("GudangSensorProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.4") \
        .config("spark.sql.session.timeZone", "UTC") \
        .getOrCreate()

    # Set log level to WARN to reduce verbosity (optional)
    spark.sparkContext.setLogLevel("WARN")
    print("Spark Session Created.")

    # 1. Read from Kafka topics
    df_suhu_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKERS_PYSPARK) \
        .option("subscribe", SUHU_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    df_kelembaban_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKERS_PYSPARK) \
        .option("subscribe", KELEMBABAN_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    # 2. Parse JSON and add Kafka timestamp
    df_suhu = df_suhu_raw.select(
            from_json(col("value").cast("string"), schema_suhu).alias("data"),
            col("timestamp").alias("timestamp_suhu") # Kafka message timestamp
        ).select("data.*", "timestamp_suhu")

    df_kelembaban = df_kelembaban_raw.select(
            from_json(col("value").cast("string"), schema_kelembaban).alias("data"),
            col("timestamp").alias("timestamp_kelembaban")
        ).select("data.*", "timestamp_kelembaban")

    # 3. Individual Filtering and Alerting (Console Output)
    # a. Peringatan Suhu Tinggi
    query_suhu_alert = df_suhu \
        .filter(col("suhu") > 80) \
        .select(
            lit("[Peringatan Suhu Tinggi]").alias("alert_type"),
            concat(lit("Gudang "), col("gudang_id"), lit(": Suhu "), col("suhu").cast("string"), lit("°C")).alias("message")
        ) \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # b. Peringatan Kelembaban Tinggi
    query_kelembaban_alert = df_kelembaban \
        .filter(col("kelembaban") > 70) \
        .select(
            lit("[Peringatan Kelembaban Tinggi]").alias("alert_type"),
            concat(lit("Gudang "), col("gudang_id"), lit(": Kelembaban "), col("kelembaban").cast("string"), lit("%")).alias("message")
        ) \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # 4. Gabungkan Stream dari Dua Sensor (Stream-Stream Join)
    # Watermarking is essential for stateful operations like joins on unbounded streams
    # It tells Spark how late data can be before it's dropped for a given window
    df_suhu_watermarked = df_suhu.withWatermark("timestamp_suhu", "10 seconds")
    df_kelembaban_watermarked = df_kelembaban.withWatermark("timestamp_kelembaban", "10 seconds")

    # Join condition: same gudang_id and timestamps within a 10-second window of each other.
    # The choice of interval in the join condition (e.g., "interval 5 seconds") should be related to
    # how close in time you expect related events to be. The watermark handles overall lateness.
    joined_df = df_suhu_watermarked.alias("s").join(
        df_kelembaban_watermarked.alias("k"),
        expr("""
            s.gudang_id = k.gudang_id AND
            s.timestamp_suhu >= k.timestamp_kelembaban - interval 5 seconds AND
            s.timestamp_suhu <= k.timestamp_kelembaban + interval 5 seconds
        """),
        "inner" # Use "inner" to get only matching pairs
    ).select(
        col("s.gudang_id").alias("gudang_id"),
        col("s.suhu").alias("suhu"),
        col("k.kelembaban").alias("kelembaban")
        # Optionally select one of the timestamps or `greatest(s.timestamp_suhu, k.timestamp_kelembaban)` as event_time
    )

    # 5. Buat Peringatan Gabungan
    # Define conditions and status messages
    # Suhu > 80°C dan Kelembaban > 70% → peringatan kritis
    # Else, provide other statuses
    alerts_df = joined_df.withColumn(
        "status_message",
        when((col("suhu") > 80) & (col("kelembaban") > 70), "Bahaya tinggi! Barang berisiko rusak")
        .when((col("suhu") > 80) & (col("kelembaban") <= 70), "Suhu tinggi, kelembaban normal")
        .when((col("suhu") <= 80) & (col("kelembaban") > 70), "Kelembaban tinggi, suhu aman")
        .otherwise("Aman")
    )

    # Write the combined alerts/status to console using foreachBatch for custom printing
    query_combined_alerts = alerts_df \
        .writeStream \
        .outputMode("append") \
        .foreachBatch(process_critical_alerts_batch) \
        .option("checkpointLocation", "/tmp/spark_checkpoints/gudang_combined_alerts") \
        .trigger(processingTime="10 seconds") \
        .start()

    print("All streams started. Awaiting termination...")
    spark.streams.awaitAnyTermination()