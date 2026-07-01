# Delta Lake MERGE Implementation — Assignment 7

![Databricks](https://img.shields.io/badge/Platform-Databricks%20Free%20Edition-red)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-MERGE-blue)
![PySpark](https://img.shields.io/badge/Language-PySpark-orange)

## Objective
Perform incremental data processing using Delta Lake on the Superstore dataset — demonstrating real-world upsert patterns with MERGE.

## Project Structure
```
delta-lake-assignment/
├── data/
│   ├── customer_master.csv         # Base dataset (90% of Superstore data, cleaned)
│   └── customer_incremental.csv    # Simulated new + updated records (10% + modifications)
├── notebooks/
│   └── delta_scd_assignment.ipynb  # Full PySpark implementation
├── screenshots/
│   ├── data_loading/               # Step 1 output — schema, row count
│   ├── data_cleaning/              # Step 4 output — null/duplicate handling
│   ├── scd1/                       # Step 6 output — MERGE operation
│   ├── validation/                 # Step 7 output — row count, duplicate check
│   └── final_output/               # Step 8 output — final Delta table
├── report/
│   └── assignment_summary.pdf      # Short written summary
└── README.md
```

## Dataset
- **Source:** [Superstore Dataset — Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- **Original rows:** 9,994
- **After cleaning:** ~8,771 rows
- **Key column:** `Row_ID` (used as merge key)

## Steps Performed
| Step | Description |
|------|-------------|
| 1 | Loaded Superstore CSV from Databricks Volume into a Spark DataFrame |
| 2 | Fixed column names (spaces/hyphens → underscores), cast numeric fields using `try_cast` |
| 3 | Saved as Delta table `customer_master` |
| 4 | Cleaned nulls (Sales, Quantity, Customer_ID) and removed duplicate rows |
| 5 | Created `customer_incremental`: 10% new rows + 5 simulated updated rows |
| 6 | Applied Delta Lake `MERGE INTO` on `Row_ID` — matched rows updated, new rows inserted |
| 7 | Validated: final row count = distinct Row_ID count, zero duplicate groups |
| 8 | Displayed final Delta table with all changes reflected |

## MERGE Logic
```python
delta_master.alias("t")
  .merge(df_incr.alias("s"), "t.Row_ID = s.Row_ID")
  .whenMatchedUpdate(set={"Sales": "s.Sales", "Quantity": "s.Quantity", ...})
  .whenNotMatchedInsertAll()
  .execute()
```

## Validation Results
| Check | Result |
|-------|--------|
| Final row count | 8,771 |
| Distinct Row_ID count | 8,771 |
| Duplicate Row_ID groups | 0 |

## Environment
- Databricks Free Edition (Serverless Compute)
- PySpark + Delta Lake (built-in)
- Unity Catalog Volume for file storage

## 👨‍💻 Author

Kapil Singhal  
Data Engineering Intern @ Celebal Technologies