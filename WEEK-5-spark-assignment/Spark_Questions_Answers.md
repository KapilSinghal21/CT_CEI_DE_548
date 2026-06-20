# Week 5 - Spark Questions (Answers)

Dataset used for testing: Sample - Superstore.csv

---

### Q1: What are the key limitations of traditional MapReduce that make Spark a preferred choice for modern big data processing?

The main problem with MapReduce is that it writes data to disk after every map and reduce step. So if you have a job with multiple stages, it keeps reading and writing to disk again and again, which is slow.

Spark fixes this by keeping data in memory between operations instead of going back to disk every time. It also gives you a much nicer API (DataFrames/SQL) instead of writing raw map and reduce functions, and it builds an execution plan first and optimizes it before actually running anything (lazy evaluation). That's basically why Spark ends up being way faster, especially for jobs that need to go over the same data multiple times.

---

### Q2: Explain how Spark uses In-Memory Computing to speed up iterative machine learning algorithms compared to disk-based systems.

ML algorithms like gradient descent or k-means run the same data through many iterations. In a disk-based system, every iteration means reading from disk, processing, writing back, then reading again for the next round — so the disk I/O cost happens every single time.

Spark loads the data into memory once and can cache it there (`.cache()` / `.persist()`), so after the first read, every other iteration just reuses what's already in RAM. You only pay the disk cost once instead of N times for N iterations, which is the real reason Spark's MLlib is so much faster than running the same thing on Hadoop MapReduce.

---

### Q3: Write a code snippet to remove all duplicate rows from a DataFrame based on a specific set of columns: user_id and transaction_date.

```python
df_deduped = df.dropDuplicates(["user_id", "transaction_date"])
df_deduped.show()
```

`dropDuplicates()` lets you pass specific columns, so it only checks those two columns to decide what counts as a duplicate, not the whole row. I tested this same idea on the Superstore data using `["Customer ID", "Order Date"]` and it worked fine, row count went down as expected.

---

### Q4: Given a DataFrame df_sales, write a query to filter for rows where the region is 'West' and then group by product_category to find the average sale_amount.

```python
from pyspark.sql.functions import avg, col

result = df_sales.filter(col("region") == "West") \
                  .groupBy("product_category") \
                  .agg(avg("sale_amount").alias("avg_sale_amount"))

result.show()
```

Just filter first, then groupBy + agg. Ran the same logic on Superstore (Region = West, grouped by Category, averaging Sales) and got real numbers back — Technology came out highest around 420, Furniture around 357, Office Supplies around 116.

---

### Q5: What is the difference between .na.drop() and .na.fill()? Provide a code example of filling null values in a status column with the string 'Unknown'.

`.na.drop()` removes rows that have nulls — so your row count goes down.
`.na.fill()` replaces the null with something you choose — row count stays the same.

So drop loses data, fill keeps the row but patches the missing value.

```python
df_filled = df.na.fill({"status": "Unknown"})
```

---

### Q6: Write a query to find the total count of records for each city in a DataFrame, but only for cities where the count is greater than 100.

```python
from pyspark.sql.functions import count, col

result = df.groupBy("city") \
            .agg(count("*").alias("record_count")) \
            .filter(col("record_count") > 100)

result.show()
```

This is basically the same idea as SQL's HAVING — you can't filter on the aggregated count before you've actually aggregated, so the filter has to come after `.agg()`, not before. Tested with City on Superstore data, cities like New York City and LA showed up since they had way over 100 records, smaller cities got filtered out.

---

### Q7: How does the immutability of Spark DataFrames affect how you perform "data cleaning" steps like dropping columns or renaming them?

DataFrames in Spark can't be changed in place. So when you do something like drop a column or rename it, you're not actually modifying the original df — you're getting a brand new DataFrame back, and the old one is still sitting there unchanged.

```python
df_clean = df.drop("temp_column").withColumnRenamed("old_name", "new_name")
# df itself is untouched, df_clean is the new version
```

Practically this just means you always have to assign the result somewhere (either a new variable or overwrite the same name), otherwise your cleaning step basically does nothing. It's also kind of nice for debugging since the original df is still around if you need to go back and check something.

---

### Q8: Write a Spark command to filter a dataset for rows where the age is between 18 and 30 (inclusive) and the subscription is 'Premium'.

```python
from pyspark.sql.functions import col

result = df.filter(
    (col("age").between(18, 30)) & (col("subscription") == "Premium")
)
```

`.between()` already includes both endpoints, so no need to write separate >= and <= conditions. Tried a similar filter on Superstore data (Quantity between 1-5, Ship Mode = Second Class) and it worked the same way.

---

### Q9: When cleaning a dataset, why is it often better to handle null values before performing mathematical aggregations like sum() or avg()?

Spark just skips nulls automatically when you call sum() or avg(), it doesn't throw an error or anything. But that can quietly mess things up:

- If a lot of rows have null in that column, your average is only based on the rows that aren't null, which might not represent the real picture if the nulls aren't random.
- count(*) counts every row, but avg(price) only counts non-null rows for price. If you're not careful, your numbers won't line up and it'll look confusing.
- If a null sneaks into a calculation like price * quantity, the whole result becomes null too, and that gets silently dropped from later aggregations.

So basically you want to decide upfront what a null actually means (zero? unknown? should the row even be there?) and deal with it deliberately, instead of letting Spark's default null-skipping behavior decide for you without you noticing.

---

### Q10: Write the code to revise a column named raw_timestamp by casting it to a TimestampType and renaming it to event_time.

```python
from pyspark.sql.types import TimestampType

df_revised = df.withColumn("raw_timestamp", col("raw_timestamp").cast(TimestampType())) \
               .withColumnRenamed("raw_timestamp", "event_time")
```

One thing worth knowing — `cast()` only works cleanly if the string is already in a format Spark recognizes by default. If the dates are in some weird/inconsistent format, you'd want `to_timestamp(col, format)` instead and give it the actual pattern.

---

### Q11: Explain the "Shuffle" process that occurs during a grouping operation. Why is it considered a wide transformation?

Spark splits your data into partitions, and those partitions can be sitting on different machines. When you do something like groupBy(), Spark needs all the rows with the same key (like the same city) to end up together so it can actually compute the aggregate correctly.

The problem is rows with the same key are probably scattered across different partitions right now. So Spark has to physically move data around — across the network, sometimes through disk — to get matching rows into the same partition. That whole data-moving process is the "shuffle."

It's called a wide transformation because the output partitions depend on data coming from a bunch of different input partitions, not just the one partition it started in (that's what a narrow transformation like filter or select would look like — no movement needed). Shuffles are expensive because of all that network/disk traffic, so they're usually the slowest part of a Spark job.

---

### Q12: Write a code snippet that identifies and removes rows where the email column contains null values OR the username is an empty string.

```python
from pyspark.sql.functions import col

df_clean = df.filter(
    ~(col("email").isNull() | (col("username") == ""))
)
```

The `~` flips the whole OR condition, so you're left with only rows where email isn't null AND username isn't empty. Checked something similar on the Superstore data using Customer Name and it came back clean — no bad rows there.

---

### Q13: How do you use the .agg() function to calculate multiple statistics at once, such as the min, max, and mean of the price column?

```python
from pyspark.sql.functions import min, max, avg

result = df.agg(
    min("price").alias("min_price"),
    max("price").alias("max_price"),
    avg("price").alias("mean_price")
)
```

You can just pass multiple aggregation expressions into one `.agg()` call, separated by commas — Spark computes all of them together in a single pass instead of running three separate queries. Tested this on the Sales column from Superstore and got min/max/mean all in one go.

---

### Q14: In the context of cleaning a dataset, what is the risk of using inferSchema=true when your source data contains messy or inconsistent date formats?

The big risk is that Spark just guesses the column types by sampling the data, and if the dates aren't consistent, that guess can go wrong in a couple of ways:

- If the format is mixed (some rows like 1/5/2024, others like 05-01-2024), Spark often can't confidently call it a date type at all, so it just falls back to treating the whole column as plain text. You don't get any warning, it just silently happens.
- Even if it does pick a date type, it assumes one format for the entire column. Any row that doesn't match that format can come out as null, or even worse, get parsed into a date that looks valid but is actually wrong (day and month flipped, for example) — which is way harder to catch because it doesn't look like an error.

I actually ran into this exact issue while working on this assignment — the Superstore data has Order Date and Ship Date columns mixing two formats, and when I tried `inferSchema=True` plus a normal date parse, some rows just failed or parsed wrong. Had to explicitly try both formats and fall back between them instead of trusting the auto-inferred schema.

---

### Q15: Write a final processing pipeline that: filters out duplicates, fills null prices with 0, groups by store_id to calculate total revenue.

```python
from pyspark.sql.functions import sum as _sum, col

pipeline_result = df.dropDuplicates() \
                     .na.fill({"price": 0}) \
                     .groupBy("store_id") \
                     .agg(_sum("price").alias("total_revenue")) \
                     .orderBy(col("total_revenue").desc())

pipeline_result.show()
```

This just runs the three steps in order — dedup first, then fill the nulls so they don't accidentally get skipped during the sum, then group and add up the revenue per store. Ran a version of this on the Superstore data (grouping by State, summing Sales instead of store_id/price) and it worked end to end without issues.
