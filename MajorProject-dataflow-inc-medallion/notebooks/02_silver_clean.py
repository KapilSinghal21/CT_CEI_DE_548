"""
Silver Layer
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lpad, when, lit, avg

spark = SparkSession.builder.appName("Silver_Clean").getOrCreate()

BRONZE_DIR = "/Volumes/workspace/default/raw_data/bronze"
SILVER_DIR = "/Volumes/workspace/default/raw_data/silver"


def load(table):
    return spark.read.format("delta").load(f"{BRONZE_DIR}/{table}")


def clean_customers():
    df = load("customers").dropDuplicates(["customer_id"])
    df = df.withColumn("customer_zip_code_prefix", lpad(col("customer_zip_code_prefix").cast("string"), 5, "0"))
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/customers")


def clean_orders():
    df = load("orders").dropDuplicates(["order_id"])
    for c in ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
              "order_delivered_customer_date", "order_estimated_delivery_date"]:
        df = df.withColumn(c, to_timestamp(col(c)))
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/orders")


def clean_order_items():
    df = load("order_items").dropDuplicates()
    df = df.withColumn("shipping_limit_date", to_timestamp(col("shipping_limit_date")))
    df = df.filter(col("price") > 0)
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/order_items")


def clean_payments():
    df = load("order_payments").dropDuplicates()
    df = df.filter(col("payment_value") >= 0)
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/order_payments")


def clean_reviews():
    df = load("order_reviews").dropDuplicates(["review_id"])
    df = df.fillna({"review_comment_message": "", "review_comment_title": ""})
    df = df.withColumn("review_creation_date", to_timestamp(col("review_creation_date")))
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/order_reviews")


def clean_products():
    df = load("products").dropDuplicates(["product_id"])
    translation = load("product_category_name_translation").drop("_ingestion_timestamp", "_source_file")
    df = df.join(translation, on="product_category_name", how="left")
    df = df.withColumn(
        "product_category_name_english",
        when(col("product_category_name_english").isNull(), lit("unknown"))
        .otherwise(col("product_category_name_english"))
    )
    for c in ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        med = df.select(c).na.drop().approxQuantile(c, [0.5], 0.01)[0]
        df = df.fillna({c: med})
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/products")


def clean_sellers():
    df = load("sellers").dropDuplicates(["seller_id"])
    df = df.withColumn("seller_zip_code_prefix", lpad(col("seller_zip_code_prefix").cast("string"), 5, "0"))
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/sellers")


def clean_geolocation():
    df = load("geolocation").dropDuplicates()
    df = df.groupBy("geolocation_zip_code_prefix").agg(
        avg("geolocation_lat").alias("geolocation_lat"),
        avg("geolocation_lng").alias("geolocation_lng"),
    )
    df.write.format("delta").mode("overwrite").save(f"{SILVER_DIR}/geolocation")


if __name__ == "__main__":
    clean_customers()
    clean_orders()
    clean_order_items()
    clean_payments()
    clean_reviews()
    clean_products()
    clean_sellers()
    clean_geolocation()
    print("[SILVER] Done.")
