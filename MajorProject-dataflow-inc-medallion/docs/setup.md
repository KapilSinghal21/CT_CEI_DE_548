# Setup & run instructions (Databricks)

## 1. Create a Volume
Catalog → your catalog (`workspace`) → schema (`default`) → Create Volume → name it, e.g. `raw_data`.

## 2. Upload data
Upload all 9 Olist CSVs into the volume:
```
/Volumes/workspace/default/raw_data/
```

## 3. Create notebooks
Create 5 notebooks under a project folder, one per file in `notebooks/`. Attach each to **Serverless** compute.

## 4. Update paths
Each script has path variables at the top (`RAW_DIR`, `BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`, etc). Point them to your volume, e.g.:
```python
RAW_DIR = "/Volumes/workspace/default/raw_data"
BRONZE_DIR = "/Volumes/workspace/default/raw_data/bronze"
```

## 5. Run order
```
01_bronze_ingest.py
02_silver_clean.py
03_gold_aggregate.py
04_scd2_merge.py
05_schema_drift_check.py
```
Each depends on the previous layer's output — run strictly in this order.

## 6. SQL analytics
Create a SQL notebook, paste `sql/06_sql_analytics.sql`, run on Serverless SQL Warehouse. Tables are referenced directly via Delta path (`delta.\`/Volumes/...\``) — no `CREATE TABLE` needed since Unity Catalog Volumes don't support external table registration from `dbfs:` paths on free edition.

## Notes
- Bronze uses `multiLine` CSV option to correctly parse multi-line review text fields.
- SCD2 merge uses `dbutils.fs.ls()` for existence checks instead of `os.path.exists()`, since Volumes aren't visible to the local filesystem.
- Schema drift snapshots are stored as JSON files in `/Volumes/workspace/default/raw_data/schema_history/`.
