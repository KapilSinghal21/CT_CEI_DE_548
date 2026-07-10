"""
SCD Type 2 - History Tracking on Delta Lake
Tracks changes on customers & products dimensions using MERGE INTO.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from delta.tables import DeltaTable

spark = SparkSession.builder.appName("SCD2_Merge").getOrCreate()

SILVER_PATH = "/Volumes/workspace/default/raw_data/silver"
GOLD_DIM_PATH = "/Volumes/workspace/default/raw_data/gold/dim"


def init_scd2_table(df, key_col, path):
    """First-time load: add SCD2 tracking columns."""
    df = df.withColumn("effective_date", current_timestamp()) \
           .withColumn("end_date", lit(None).cast("timestamp")) \
           .withColumn("is_current", lit(True))
    df.write.format("delta").mode("overwrite").save(path)


def scd2_merge(new_df, key_col, path, compare_cols):
    """
    Incoming batch (new_df) merged into existing SCD2 dimension.
    - If key exists and any compare_col changed -> close old row, insert new row
    - If key is new -> insert as new current row
    """
    target = DeltaTable.forPath(spark, path)

    staged = new_df.withColumn("effective_date", current_timestamp()) \
                    .withColumn("end_date", lit(None).cast("timestamp")) \
                    .withColumn("is_current", lit(True)) \
                    .withColumn("merge_key", col(key_col))

    change_condition = " OR ".join([f"target.{c} <> staged.{c}" for c in compare_cols])

    # Step 1: expire old rows where data changed
    (target.alias("target")
        .merge(
            staged.alias("staged"),
            f"target.{key_col} = staged.merge_key AND target.is_current = true"
        )
        .whenMatchedUpdate(
            condition=change_condition,
            set={
                "is_current": "false",
                "end_date": "current_timestamp()"
            }
        )
        .execute())

    # Step 2: insert new current rows (new keys OR changed records)
    existing_current = spark.read.format("delta").load(path).filter(col("is_current") == True)
    to_insert = staged.join(
        existing_current.select(key_col, *compare_cols).withColumnRenamed(key_col, "existing_key"),
        staged.merge_key == col("existing_key"),
        "left_anti"
    ).drop("merge_key")

    to_insert.write.format("delta").mode("append").save(path)

    print(f"[SCD2] Merge complete for {path}: {to_insert.count()} new/changed rows inserted")


def path_exists(path):
    try:
        dbutils.fs.ls(path)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Customers dimension
    customers_new = spark.read.format("delta").load(f"{SILVER_PATH}/customers")

    if not path_exists(f"{GOLD_DIM_PATH}/customers"):
        init_scd2_table(customers_new, "customer_id", f"{GOLD_DIM_PATH}/customers")
    else:
        scd2_merge(
            customers_new,
            key_col="customer_id",
            path=f"{GOLD_DIM_PATH}/customers",
            compare_cols=["customer_city", "customer_state", "customer_zip_code_prefix"]
        )

    # Products dimension
    products_new = spark.read.format("delta").load(f"{SILVER_PATH}/products")

    if not path_exists(f"{GOLD_DIM_PATH}/products"):
        init_scd2_table(products_new, "product_id", f"{GOLD_DIM_PATH}/products")
    else:
        scd2_merge(
            products_new,
            key_col="product_id",
            path=f"{GOLD_DIM_PATH}/products",
            compare_cols=["product_category_name_english", "product_weight_g"]
        )
