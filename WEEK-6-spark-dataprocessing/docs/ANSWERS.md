# Week 6 – Spark Assignment: Answers

### Q1: Roles of Driver, Cluster Manager, Executor
- **Driver**: Runs the `main()` of the Spark application, creates the SparkSession/SparkContext, builds the DAG of transformations, and schedules tasks.
- **Cluster Manager**: Allocates resources (CPU, memory) across the cluster for the application. Examples: YARN, Mesos, Kubernetes, Spark Standalone.
- **Executor**: Runs on worker nodes, executes the tasks assigned by the Driver, stores data in memory/disk for caching, and reports results back to the Driver.

### Q2: Lazy Evaluation
Spark does not execute transformations (`filter`, `select`, `map`, etc.) immediately. It builds a logical execution plan (DAG) and only triggers computation when an **action** (`show()`, `collect()`, `write()`) is called. This allows Spark to optimize the entire chain of operations (combine/reorder steps, skip unnecessary work) before running anything, reducing redundant computation and I/O.

### Q3: Read CSV with header + inferSchema
```python
df = spark.read.csv("data/source.csv", header=True, inferSchema=True)
```

### Q4: CSV vs Parquet
- **CSV**: Row-based, plain text, no schema enforcement, reads the entire file even if only a few columns are needed.
- **Parquet**: Columnar, binary, compressed, stores schema with data. Since it's columnar, Spark can read only the required columns (column pruning) and apply predicate pushdown, making it much faster and storage-efficient for analytical workloads.

### Q5: Select product_id, price where category = 'Electronics'
```python
df.select("product_id", "price").filter(col("category") == "Electronics")
```

### Q6: Rename column + cast price to Double
```python
df.withColumnRenamed("old_name", "new_name") \
  .withColumn("price", col("price").cast("double"))
```

### Q7: Lineage Graph (DAG) and Fault Tolerance
Spark tracks every transformation applied to an RDD/DataFrame as a lineage graph (DAG). If a worker/executor fails and a partition of data is lost, Spark uses the lineage graph to recompute only the lost partition from the original source data, instead of recomputing the whole dataset or restarting the job. This removes the need for replicating data for fault tolerance.

### Q8: Filter status = 'Completed' AND amount > 1000
```python
df.filter((col("status") == "Completed") & (col("amount") > 1000))
```

### Q9: Predicate Pushdown in Parquet
Predicate pushdown means filter conditions (`WHERE` clauses) are pushed down to the data source/file format level instead of being applied after loading all data into memory. Since Parquet stores column statistics (min/max) per row-group, Spark can skip entire row-groups/blocks that can't match the filter, drastically reducing the amount of data read from disk and loaded into memory.

### Q10: Add final_price = base_price * 1.18
```python
df.withColumn("final_price", col("base_price") * 1.18)
```

### Q11: Transformations vs Actions
- **Transformations**: Lazy operations that return a new DataFrame/RDD without computing results immediately. Examples: `filter()`, `select()`, `withColumn()`, `groupBy()`, `map()`.
- **Actions**: Trigger actual execution of the DAG and return a result. Examples: `show()`, `collect()`, `count()`, `write()`.

### Q12: Load Parquet → filter null user_id → save as CSV
```python
df = spark.read.parquet("path/to/input")
clean_df = df.filter(col("user_id").isNotNull())
clean_df.write.option("header", True).csv("path/to/output")
```

### Q13: Client Mode vs Cluster Mode
- **Client Mode**: The Driver runs on the machine that submitted the application (e.g., local laptop/edge node), outside the cluster. Useful for interactive/debugging sessions, but the client machine must stay connected.
- **Cluster Mode**: The Driver itself runs inside the cluster (on one of the worker nodes), managed by the Cluster Manager. Used for production jobs since it doesn't depend on the submitting machine staying alive.

### Q14: Filter region = 'North' OR priority = 'High'
```python
df.filter((col("region") == "North") | (col("priority") == "High"))
```

### Q15: Why .show(5) instead of .collect() on huge datasets
`.collect()` pulls **all** rows from all executors back to the Driver's memory, which can easily crash the Driver on a multi-terabyte dataset (Driver has limited memory, unlike the distributed cluster). `.show(5)` only computes and returns a small sample (default 5/20 rows) without pulling the entire dataset, making it safe for quick inspection of large data.
