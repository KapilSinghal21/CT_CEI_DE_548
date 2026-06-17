# Week 5 - Spark Assignment

## Objective
Understand Spark architecture and perform efficient data processing using transformations, filtering, schema handling, and optimized file formats.

## Dataset
Sample Superstore dataset (`data/sample_data.csv`) - retail sales data with orders, customers, products, regions, sales, and profit.

## Topics Covered
- Spark Architecture (Driver, Cluster Manager, Executors) and execution modes
- Lazy Evaluation and DAG (Lineage Graph)
- Reading CSV/Parquet with schema handling
- Filtering and column selection
- DataFrame modification (rename, cast, add columns)
- Wide transformations, Shuffle, Predicate Pushdown
- CSV vs Parquet performance
- Null handling
- Full pipeline: read → transform → filter → write
- Best practices (avoiding collect(), using show())

## Project Structure
```
Week-5-Spark/
├── README.md
├── data/sample_data.csv
├── notebooks/week5_spark.ipynb
├── src/
│   ├── theory_answers.md
│   └── spark_queries.py
└── outputs/query_results/results.md
```

## How to Run
**Option A - Databricks (recommended)**
1. Upload `data/sample_data.csv` to a Volume.
2. Import `notebooks/week5_spark.ipynb`.
3. Attach to Serverless compute and run all cells.

**Option B - Local/Jupyter**
1. `pip install pyspark`
2. Run `src/spark_queries.py` or open the notebook.

## Output
PySpark code + execution results + performance/architecture insights — see `outputs/query_results/results.md`.

## Author 
Kapil Singhal
