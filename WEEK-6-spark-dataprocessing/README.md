# Week 6 – Spark Assignment

Understanding Spark architecture and performing data processing with PySpark: transformations, filtering, schema handling, and file format optimization (CSV vs Parquet).

## Repo Structure
```
week6-spark-assignment/
├── data/
│   └── source.csv              # Sample input dataset
├── src/
│   ├── spark_pipeline.py       # Main pipeline: read -> transform -> filter -> write
│   └── null_handling_pipeline.py  # Parquet read, null filtering, CSV write (Q12)
├── docs/
│   └── ANSWERS.md              # Theory + code answers (Q1–Q15)
├── output/                     # Generated output (CSV/Parquet)
├── requirements.txt
└── README.md
```

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
cd week6-spark-assignment
python src/spark_pipeline.py
python src/null_handling_pipeline.py
```

## What it covers
- Spark architecture (Driver, Cluster Manager, Executor) & execution modes
- Lazy Evaluation and DAG/Lineage Graph
- Reading CSV/Parquet with schema handling
- Filtering, column selection, renaming, type casting
- Adding derived columns (tax calculation)
- Wide transformations, Shuffle, Predicate Pushdown concepts
- Null handling
- Full pipeline: read → transform → filter → write (CSV/Parquet)
- Best practices: using `.show()` instead of `.collect()` on large data

## Insights
- **Parquet vs CSV**: Parquet (columnar + predicate pushdown) is significantly faster and smaller on disk than CSV for analytical filtering/column-selection workloads used here.
- **Lazy evaluation**: No computation happens until an action (`show`, `write`) is called — Spark optimizes the full chain of transformations first.
- Full theory answers are in `docs/ANSWERS.md`.

## Author 
Kapil Singhal 