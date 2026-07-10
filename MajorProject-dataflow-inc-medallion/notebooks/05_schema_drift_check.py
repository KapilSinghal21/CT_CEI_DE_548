"""
Schema Drift Detection
"""
import json
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Schema_Drift").getOrCreate()

BRONZE_DIR = "/Volumes/workspace/default/raw_data/bronze"
SCHEMA_LOG_DIR = "/Volumes/workspace/default/raw_data/schema_history"

TABLES = ["customers", "geolocation", "order_items", "order_payments",
          "order_reviews", "orders", "products", "sellers",
          "product_category_name_translation"]


def path_exists(path):
    try:
        dbutils.fs.ls(path)
        return True
    except:
        return False


def get_current_schema(table):
    df = spark.read.format("delta").load(f"{BRONZE_DIR}/{table}")
    return {f.name: str(f.dataType) for f in df.schema.fields}


def check_drift(table):
    current_schema = get_current_schema(table)
    log_path = f"{SCHEMA_LOG_DIR}/{table}_schema.json"

    if not path_exists(log_path):
        dbutils.fs.mkdirs(SCHEMA_LOG_DIR)
        dbutils.fs.put(log_path, json.dumps(current_schema, indent=2), overwrite=True)
        print(f"[SCHEMA] {table}: baseline recorded ({len(current_schema)} columns)")
        return

    last = json.loads("".join([r.value for r in spark.read.text(log_path).collect()]))

    new_cols = set(current_schema) - set(last)
    missing_cols = set(last) - set(current_schema)
    type_changes = {
        c: (last[c], current_schema[c])
        for c in current_schema.keys() & last.keys()
        if current_schema[c] != last[c]
    }

    if new_cols or missing_cols or type_changes:
        print(f"[DRIFT DETECTED] {table}:")
        if new_cols:
            print(f"  New columns: {new_cols}")
        if missing_cols:
            print(f"  Missing columns: {missing_cols}")
        if type_changes:
            print(f"  Type changes: {type_changes}")
    else:
        print(f"[SCHEMA] {table}: no drift")

    dbutils.fs.put(log_path, json.dumps(current_schema, indent=2), overwrite=True)


if __name__ == "__main__":
    for table in TABLES:
        check_drift(table)
