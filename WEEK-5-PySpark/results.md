# Query Results & Insights - Week 5 Spark Assignment

## 1. Raw Data Sample (Schema-enforced read)
```
+------+--------------+----------+----------+--------------+-----------+---------------+---------+-------------+---------------+----------+-----------+------+---------------+---------------+------------+--------------------+--------+--------+--------+--------+
|Row_ID|      Order_ID|Order_Date| Ship_Date|     Ship_Mode|Customer_ID|  Customer_Name|  Segment|      Country|           City|     State|Postal_Code|Region|     Product_ID|       Category|Sub_Category|        Product_Name|   Sales|Quantity|Discount|  Profit|
+------+--------------+----------+----------+--------------+-----------+---------------+---------+-------------+---------------+----------+-----------+------+---------------+---------------+------------+--------------------+--------+--------+--------+--------+
|     1|CA-2016-152156|11-08-2016|11-11-2016|  Second Class|   CG-12520|    Claire Gute| Consumer|United States|      Henderson|  Kentucky|      42420| South|FUR-BO-10001798|      Furniture|   Bookcases|Bush Somerset Col...|  261.96|       2|     0.0| 41.9136|
|     2|CA-2016-152156|11-08-2016|11-11-2016|  Second Class|   CG-12520|    Claire Gute| Consumer|United States|      Henderson|  Kentucky|      42420| South|FUR-CH-10000454|      Furniture|      Chairs|Hon Deluxe Fabric...|  731.94|       3|     0.0| 219.582|
|     3|CA-2016-138688|06-12-2016| 6/16/2016|  Second Class|   DV-13045|Darrin Van Huff|Corporate|United States|    Los Angeles|California|      90036|  West|OFF-LA-10000240|Office Supplies|      Labels|Self-Adhesive Add...|   14.62|       2|     0.0|  6.8714|
+------+--------------+----------+----------+--------------+-----------+---------------+---------+-------------+---------------+----------+-----------+------+---------------+---------------+------------+--------------------+--------+--------+--------+--------+
```
Note: `Order_Date` mixes formats (`11-08-2016` vs `6/16/2016`) — confirms why `inferSchema=true` would be risky here (see theory_answers.md, point 7).

## 2. Filtered & Selected (Region = West, Sales > 100)
```
+--------------+----------+------+---------------+--------+--------+--------+
|      Order_ID|Order_Date|Region|       Category|   Sales|  Profit|Quantity|
+--------------+----------+------+---------------+--------+--------+--------+
|CA-2014-115812|06-09-2014|  West|     Technology| 907.152| 90.7152|       6|
|CA-2014-115812|06-09-2014|  West|Office Supplies|   114.9|   34.47|       5|
|CA-2014-115812|06-09-2014|  West|      Furniture|1706.184| 85.3092|       9|
+--------------+----------+------+---------------+--------+--------+--------+
```

## 3. Modified DataFrame (renamed column + cast + new column)
```
+--------------+----------+------+---------------+--------+--------+--------+-------------+
|      order_id|Order_Date|Region|       Category|   Sales|  Profit|Quantity|Profit_Margin|
+--------------+----------+------+---------------+--------+--------+--------+-------------+
|CA-2014-115812|06-09-2014|  West|     Technology| 907.152| 90.7152|       6|          0.1|
|CA-2014-115812|06-09-2014|  West|Office Supplies|   114.9|   34.47|       5|          0.3|
+--------------+----------+------+---------------+--------+--------+--------+-------------+
```

## 4. GroupBy Aggregation (Wide Transformation - triggers Shuffle)
```
+-------+---------------+------------------+-------------------+
| Region|       Category|       Total_Sales|         Avg_Profit|
+-------+---------------+------------------+-------------------+
|  South|Office Supplies|123979.92499999993|  19.69422462311557|
|   West|Office Supplies|213125.18300000002|  26.99628392198215|
|Central|     Technology| 170401.5319999999|  80.22247952380951|
|   West|     Technology|251895.92799999993|  73.90965275459094|
|   East|     Technology|264872.08300000033|  88.67281794392511|
+-------+---------------+------------------+-------------------+
```
This aggregation required a **Shuffle** — Spark redistributed rows by `(Region, Category)` key across partitions before computing sums/averages.

## 5. CSV vs Parquet — File Size Comparison
Same cleaned dataset written in both formats:

| Format  | Size  |
|---------|-------|
| CSV     | 2.3 MB |
| Parquet | 444 KB |

Parquet is **~5x smaller** due to columnar storage and built-in compression.

## 6. Predicate Pushdown Proof (Physical Plan, reading Parquet)
```
== Physical Plan ==
*(1) Filter (isnotnull(Region#365) AND (Region#365 = West))
+- *(1) ColumnarToRow
   +- FileScan parquet [...]
      PushedFilters: [IsNotNull(Region), EqualTo(Region,West)]
```
`PushedFilters` confirms the filter was pushed down to the Parquet file scan itself — Spark skips irrelevant row groups at read time instead of loading the full dataset into memory first. This optimization is **not available with CSV**, since CSV has no column-level metadata/statistics for Spark to use.

## Key Insights
- **Lazy Evaluation**: No computation ran until `.show()`/`.write()` triggered an action; Spark optimized filter + select + groupBy together as one DAG.
- **Shuffle cost**: `groupBy("Region","Category")` was the most expensive operation since it required moving data across partitions.
- **Parquet > CSV**: ~5x smaller file size and supports predicate pushdown; CSV requires a full row-by-row scan with no skip-ahead capability.
- **Immutability**: every transformation (`withColumn`, `filter`, `na.fill`) returned a new DataFrame; the original `df` was never altered.
- **Best practice followed**: used `.show()` throughout instead of `.collect()`, which avoids pulling the full dataset into Driver memory.
