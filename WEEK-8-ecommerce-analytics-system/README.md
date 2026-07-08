# E-Commerce Order Analytics System

An end-to-end data analytics system built with Python and SQL (SQLite) that generates messy
e-commerce data, cleans it, loads it into a relational database, runs analytical SQL queries,
and provides a CLI reporting tool.

## Architecture

```
ecommerce-analytics-system/
├── data/
│   ├── raw/              # Generated messy CSVs
│   └── cleaned/          # Cleaned CSVs after processing
├── scripts/
│   ├── generate_data.py  # Step 1: creates raw CSVs with intentional issues
│   ├── clean_data.py     # Step 2: cleans data, validates integrity, writes report
│   ├── load_db.py        # Step 3: loads cleaned CSVs into SQLite (ecommerce.db)
│   ├── report_cli.py     # Step 8: CLI reporting tool
│   └── test_edge_cases.py# Step 9: edge case test functions
├── sql/
│   ├── schema.sql          # Table definitions + constraints
│   ├── aggregations.sql    # Queries 1-6 (basic + intermediate)
│   ├── window_functions.sql# Queries 7-14 (window functions, CTEs)
│   └── cohort_analysis.sql # Queries 15-16 (cohort retention, market basket)
├── output/
│   ├── data_quality_report.txt
│   └── sample_reports/
└── ecommerce.db          # SQLite database
```

## How to Run

```bash
cd ecommerce-analytics-system

# 1. Generate raw messy data
python3 scripts/generate_data.py

# 2. Clean the data (writes data/cleaned/*.csv and output/data_quality_report.txt)
python3 scripts/clean_data.py

# 3. Load cleaned data into SQLite
python3 scripts/load_db.py

# 4. Run SQL analysis queries directly (using python's sqlite3)
sqlite3 ecommerce.db < sql/aggregations.sql
sqlite3 ecommerce.db < sql/window_functions.sql
sqlite3 ecommerce.db < sql/cohort_analysis.sql

# 5. Generate a CLI report
python3 scripts/report_cli.py --type monthly --start 2025-01-01 --end 2025-01-31
# or run interactively:
python3 scripts/report_cli.py

# 6. Run edge case tests
python3 scripts/test_edge_cases.py
```

## Data Issues Intentionally Introduced

| Issue | Location | Rate |
|---|---|---|
| Missing customer_id | orders.csv | ~5% |
| Negative quantity (returns) | order_items.csv | ~3% |
| Wrong date format (DD-MM-YYYY) | orders.csv | ~10% |
| Extra spaces / mixed case names | products.csv | ~25-50% |
| Invalid emails (no @ / no domain) | customers.csv | ~2% |

## Data Cleaning Approach

- `clean_orders()` — normalizes all date formats to `YYYY-MM-DD HH:MM:SS`, converts missing/blank
  customer_id to NULL, flags future-dated and invalid-status rows.
- `clean_products()` — trims whitespace and applies title case to product names.
- `validate_emails()` — regex-validates emails, returns list of customer_ids with bad emails.
- `check_referential_integrity()` — finds order_items referencing non-existent orders; these are
  excluded from the cleaned dataset.
- `clean_order_items()` — flags negative quantities (kept, treated as returns), flags zero
  quantities, and clips out-of-range discount_percent values to 0-100.

All issues found are written to `output/data_quality_report.txt`.

## SQL Analysis Summary

- **Basic (1-3):** category revenue, top customers, monthly order counts
- **Intermediate (4-6):** non-delivered customers, over-returned products, category return rates
- **Advanced (7-16):** running totals, DENSE_RANK, LAG gaps with "At Risk" flagging, multi-level
  CTEs, NTILE quartile segmentation, YoY growth, first/last category shift, cumulative revenue
  distribution, cohort retention analysis, and market-basket (frequently bought together) analysis.

## CLI Reporting Tool

`report_cli.py` accepts `--type {daily,weekly,monthly}`, `--start`, `--end` (or runs interactively
if no args are given). It reports total orders, revenue, unique customers, top 3 products, and
% change vs. the equivalent previous period. No external libraries beyond `sqlite3` are used.

## Edge Case Handling

Verified in `test_edge_cases.py`:
1. order_items with non-existent order_id → detected and excluded during cleaning
2. discount_percent > 100 → flagged and clipped to valid range
3. quantity = 0 → kept but flagged; excluded from revenue via `quantity > 0` filters in SQL
4. order_date in the future → detectable via `order_date > datetime('now')`, can be flagged/excluded
5. Empty result sets (e.g., no orders in a date range) → queries return 0 rows without errors
