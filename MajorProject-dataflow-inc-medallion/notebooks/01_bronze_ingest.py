"""
Bronze Layer
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

spark = SparkSession.builder.appName("Bronze_Ingest").getOrCreate()

RAW_DIR = "/Volumes/workspace/default/raw_data"     
BRONZE_DIR = "/Volumes/workspace/default/raw_data/bronze" 

FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}

for table, filename in FILES.items():
    df = spark.read.option("header", True).option("inferSchema", True) \
        .option("multiLine", True).option("quote", '"').option("escape", '"') \
        .csv(f"{RAW_DIR}/{filename}")
    df = df.withColumn("_ingestion_timestamp", current_timestamp()) \
           .withColumn("_source_file", lit(filename))
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{BRONZE_DIR}/{table}")
    print(f"[BRONZE] {table}: {df.count()} rows")
