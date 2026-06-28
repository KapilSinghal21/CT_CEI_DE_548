"""
Week 6 - Spark Assignment
Pipeline: read -> transform -> filter -> write
Covers Q3, Q5, Q6, Q8, Q10, Q12, Q14
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round as spark_round

spark = SparkSession.builder \
    .appName("Week6_Spark_Assignment") \
    .master("local[*]") \
    .getOrCreate()

# ---------------------------------------------------------
# Q3: Read CSV with header + inferSchema
# ---------------------------------------------------------
df = spark.read.csv("data/source.csv", header=True, inferSchema=True)
print("=== Raw Data Schema ===")
df.printSchema()
df.show(5)

# ---------------------------------------------------------
# Q5: Select product_id, price where category == 'Electronics'
# ---------------------------------------------------------
electronics_df = df.select("product_id", "price").filter(col("category") == "Electronics")
print("=== Q5: Electronics products (product_id, price) ===")
electronics_df.show(5)

# ---------------------------------------------------------
# Q6: Rename column + cast price to Double
# ---------------------------------------------------------
revised_df = df.withColumnRenamed("old_name", "new_name") \
               .withColumn("price", col("price").cast("double"))
print("=== Q6: Renamed column + price cast to Double ===")
revised_df.printSchema()
revised_df.show(5)

# ---------------------------------------------------------
# Q8: Filter status == 'Completed' AND amount > 1000
# ---------------------------------------------------------
completed_high_value = df.filter((col("status") == "Completed") & (col("amount") > 1000))
print("=== Q8: Completed orders with amount > 1000 ===")
completed_high_value.show(5)

# ---------------------------------------------------------
# Q10: Add final_price = base_price * 1.18 (18% tax)
# ---------------------------------------------------------
with_tax_df = df.withColumn("final_price", spark_round(col("base_price") * 1.18, 2))
print("=== Q10: Added final_price column (18% tax) ===")
with_tax_df.select("product_id", "base_price", "final_price").show(5)

# ---------------------------------------------------------
# Q14: Filter region == 'North' OR priority == 'High'
# ---------------------------------------------------------
region_priority_df = df.filter((col("region") == "North") | (col("priority") == "High"))
print("=== Q14: region = North OR priority = High ===")
region_priority_df.show(10)

# ---------------------------------------------------------
# Pipeline: write transformed result as Parquet and CSV (Step: read -> transform -> filter -> write)
# ---------------------------------------------------------
final_pipeline_df = with_tax_df.filter(col("user_id").isNotNull())

final_pipeline_df.write.mode("overwrite").parquet("output/processed_parquet")
final_pipeline_df.write.mode("overwrite").option("header", True).csv("output/processed_csv")

print("=== Pipeline complete: data written to output/processed_parquet and output/processed_csv ===")

spark.stop()
