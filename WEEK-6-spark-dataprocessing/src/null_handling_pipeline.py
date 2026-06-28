"""
Q12: Load Parquet, filter null user_id, save as CSV
Also demonstrates null handling / efficient filtering.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder \
    .appName("Week6_NullHandling") \
    .master("local[*]") \
    .getOrCreate()

# First create a sample parquet input from source.csv (acts as "path/to/input")
df_csv = spark.read.csv("data/source.csv", header=True, inferSchema=True)
df_csv.write.mode("overwrite").parquet("data/input_parquet")

# Q12: Load Parquet, filter rows where user_id is null, save as CSV
df = spark.read.parquet("data/input_parquet")

print("=== Rows with null user_id (to be removed) ===")
df.filter(col("user_id").isNull()).show()

clean_df = df.filter(col("user_id").isNotNull())

clean_df.write.mode("overwrite").option("header", True).csv("output/cleaned_output_csv")

print("=== Q12 complete: null user_id rows filtered, result saved as CSV ===")

spark.stop()
