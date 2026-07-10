# Data Engineering Internship @ Celebal Technologies

Data Engineering track (Celebal Excellence Internship) and a major project. Work moves from SQL fundamentals to Spark/PySpark to Databricks Delta Lake, ending with a Medallion Architecture pipeline on a real 1.3M-row dataset.

## Weekly Breakdown

| Week | Topic | Key Deliverable |
|-----------------|---|---|
| [1](WEEK-1) | Data Cleaning (Pandas) | Cleaned e-commerce dataset, notebook |
| [2](WEEK-2) | SQL Fundamentals & Schema Design | Normalized DB, indexing, transactions |
| [3](WEEK-3-advanced-sql-queries) | Advanced SQL | Subqueries, CTEs, window functions on Superstore data |
| [4](WEEK-4-azure-adf-pipeline) | Azure Data Factory | Blob → ADF → Blob pipeline with Get Metadata + Copy |
| [5](WEEK-5-spark-assignment) | Spark Fundamentals | PySpark DataFrames, cleaning a malformed CSV |
| [6](WEEK-6-spark-dataprocessing) | Spark Data Processing | Full read→transform→filter→write pipeline, CSV vs Parquet |
| [7](WEEK-7-databricks-delta-lake-implementation) | Databricks Delta Lake | SCD1 MERGE / upsert pipeline on 9,994-row Superstore data |
| [8](WEEK-8-ecommerce-analytics-system) | End-to-End Analytics System | Data generation → cleaning → SQLite → CLI reporting tool |
| [Major Project](MajorProject-dataflow-inc-medallion) | Medallion Architecture | Bronze/Silver/Gold pipeline, SCD2, schema drift detection on Olist (1.3M rows) |

## Major Project: DataFlow Inc. Medallion Pipeline

End-to-end reliability platform on Databricks using Bronze → Silver → Gold layering over the Olist Brazilian E-Commerce dataset (9 tables, ~1.3M rows).

- **Bronze**: append-only raw ingestion with lineage columns (`_ingestion_timestamp`, `_source_file`)
- **Silver**: null handling, dedup, zip-code normalization, category translation joins
- **Gold**: category sales, revenue by state, seller performance, RFM segmentation
- **SCD Type 2**: dimension history tracking via Delta `MERGE INTO`
- **Schema drift detection**: compares current Bronze schema to the last snapshot
- **SQL analytics**: window functions, CTEs, CASE-based customer segmentation
- ADF orchestration was designed and documented but couldn't run end-to-end live, since Databricks Free Edition has no persistent cluster for ADF to target — noted as a known limitation rather than hidden.

## Tech Stack

Python · Pandas · PySpark · SQL (PostgreSQL, SQLite) · Azure Data Factory · Databricks · Delta Lake

## Repo Structure

```
cei-data-engineering-portfolio/
├── WEEK-1/
├── WEEK-2/
├── WEEK-3-advanced-sql-queries/
├── WEEK-4-azure-adf-pipeline/
├── WEEK-5-spark-assignment/
├── WEEK-6-spark-dataprocessing/
├── WEEK-7-databricks-delta-lake-implementation/
├── WEEK-8-ecommerce-analytics-system/
├── MajorProject-dataflow-inc-medallion/
└── README.md
```
Each folder has its own README with setup instructions, findings, and screenshots.

## Author

Kapil Singhal <br>
Data Engineering Intern @ Celebal Technologies