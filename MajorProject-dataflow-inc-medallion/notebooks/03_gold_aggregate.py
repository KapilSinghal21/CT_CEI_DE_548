"""
Gold Layer 
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, countDistinct, avg, datediff, max as _max, lit

spark = SparkSession.builder.appName("Gold_Aggregate").getOrCreate()

SILVER_DIR = "/Volumes/workspace/default/raw_data/silver"
GOLD_DIR = "/Volumes/workspace/default/raw_data/gold"


def load(table):
    return spark.read.format("delta").load(f"{SILVER_DIR}/{table}")


def sales_by_category():
    items = load("order_items")
    products = load("products")
    df = items.join(products, "product_id", "left")
    result = df.groupBy("product_category_name_english").agg(
        _sum("price").alias("total_revenue"),
        countDistinct("order_id").alias("total_orders"),
        avg("price").alias("avg_price"),
    ).orderBy(col("total_revenue").desc())
    result.write.format("delta").mode("overwrite").save(f"{GOLD_DIR}/sales_by_category")


def revenue_by_state():
    orders = load("orders")
    customers = load("customers")
    payments = load("order_payments")
    df = orders.join(customers, "customer_id").join(payments, "order_id")
    result = df.groupBy("customer_state").agg(
        _sum("payment_value").alias("total_revenue"),
        countDistinct("order_id").alias("total_orders"),
    ).orderBy(col("total_revenue").desc())
    result.write.format("delta").mode("overwrite").save(f"{GOLD_DIR}/revenue_by_state")


def seller_performance():
    items = load("order_items")
    sellers = load("sellers")
    df = items.join(sellers, "seller_id")
    result = df.groupBy("seller_id", "seller_state").agg(
        _sum("price").alias("total_revenue"),
        count("order_item_id").alias("total_items_sold"),
        avg("freight_value").alias("avg_freight"),
    ).orderBy(col("total_revenue").desc())
    result.write.format("delta").mode("overwrite").save(f"{GOLD_DIR}/seller_performance")


def customer_rfm():
    orders = load("orders")
    payments = load("order_payments")
    df = orders.join(payments, "order_id")
    snapshot = df.agg(_max("order_purchase_timestamp")).collect()[0][0]

    result = df.groupBy("customer_id").agg(
        countDistinct("order_id").alias("frequency"),
        _sum("payment_value").alias("monetary"),
        _max("order_purchase_timestamp").alias("last_order_date"),
    )
    result = result.withColumn("recency_days", datediff(lit(snapshot), col("last_order_date")))
    result.write.format("delta").mode("overwrite").save(f"{GOLD_DIR}/customer_rfm")


if __name__ == "__main__":
    sales_by_category()
    revenue_by_state()
    seller_performance()
    customer_rfm()
    print("[GOLD] Done.")
