# Spark Assignment — Week 5

## Objective
Understand Spark fundamentals and perform data cleaning, transformation, and aggregation using DataFrames, using the Sample Superstore dataset (9,994 retail order records).

## Folder Structure
```
spark-assignment/
│── data/
│   └── dataset.csv          # Source data (Sample Superstore)
│── notebook/
│   └── spark_basics.ipynb   # Full PySpark pipeline with explanations + output
│── output/
│   └── results.csv          # Output of the final pipeline (Step 10)
|   
|── Spark_Questions_Answers.md
│── README.md
```

## How to Run
1. Install dependencies:
   ```
   pip install pyspark jupyter
   ```
   (Requires Java 8+ installed and on PATH — Spark runs on the JVM.)
2. Open the notebook:
   ```
   jupyter notebook notebook/spark_basics.ipynb
   ```
3. Run all cells top to bottom. The notebook runs in local mode (`local[*]`), so no cluster setup is needed.

## What This Covers
- Spark vs MapReduce (concept)
- Creating a Spark session
- Loading a CSV into a DataFrame, inspecting schema/rows
- Data cleaning: duplicate removal, null checks, and fixing a real CSV-parsing/schema issue found in the raw file
- Filtering by Region, Category, and Sales thresholds
- Renaming columns and casting/parsing inconsistent date formats
- Aggregations: count, sum, avg, min, max
- `groupBy()` with a condition applied to the aggregated result
- Wide transformations & shuffle (concept)
- A combined end-to-end pipeline (load → clean → transform → filter → aggregate), saved to `output/results.csv`

## Key Findings
- The raw CSV had ~300 rows with unescaped quotes inside `Product Name`, which broke Spark's default CSV parser and corrupted the inferred types of `Sales`, `Quantity`, and `Discount`. Fixed with `escape='"'` and `multiLine=True` on the CSV reader.
- `Order Date` / `Ship Date` mix two date formats in the same column; parsed safely using `try_to_date` + `coalesce`.
- West region leads in total sales; Central region has the lowest average profit per order.
- Technology, Office Supplies, and Furniture each exceed $200K in total sales.
