# Pinterest Data Pipeline

<p align="justify">
This project focuses on designing a scalable and efficient data processing system within the AWS cloud infrastructure, drawing inspiration from the data management capabilities of leading social platforms. The goal is to create a system capable of handling large-scale data workflows, encompassing ingestion, storage, processing, and analysis. However, in this case, the data is stored locally in MySQL. </p>
<p align="justify">
</p>

---

1. [Overview](#overview)
   - [File Structure](#file-structure)
   - [Project Libraries](#project-libraries)
2. [Milestone 2](#milestone-2)
3. [Milestones 3-7](#milestones-3-7)

## Overview
<p align="justify">
Milestone 1 focuses on setting up GitHub for version control, enabling the tracking and saving of all code changes throughout the project. By creating a GitHub repository and connecting it to the local environment, it ensures that the code remains well-organized, backed up, and easily accessible for collaboration. GitHub will serve as the primary platform to manage version history, handle branching for feature development, and facilitate smooth coordination.</p>

### File Structure
Project Related Files: 
1. `API.py`
2. `input_ouput.py`
3. `db_conn.py`
4. `main.py`
- The file structure includes Python scripts for all task requirements used throughout this project.

### Project Libraries
The following modules need to be installed:
- `Kafka-python`
- `PySpark`
- `Thread`
- `sqlalchemy`
- `requests`
- `yaml`

## Milestone 2 
## 1. Setup Infrastructure
- Download the ZIP package containing `user_posting_emulation.py`.
- The script connects to an RDS database with three tables:
  - `pinterest_data`: Contains data about posts being uploaded to Pinterest.
  - `geolocation_data`: Contains geolocation details for each post in `pinterest_data`.
  - `user_data`: Contains information about users who uploaded the posts.

## 2. Secure Credentials
- Extract database credentials (`HOST`, `USER`, `PASSWORD`) and save them in a `db_creds.yaml` file.
- Add `db_creds.yaml` to your `.gitignore` file to avoid exposing sensitive information in version control.

## 3. Explore Data
- Run the `user_posting_emulation.py` script.
- Print the following variables to inspect data structure:
  - `pin_result`: A sample entry from the `pinterest_data` table.
  - `geo_result`: A sample entry from the `geolocation_data` table.
  - `user_result`: A sample entry from the `user_data` table.

This milestone establishes the groundwork for managing Pinterest-like data in this project.


## Milestones 3-7

This section describes the process of setting up a Kafka-based pipeline to enable batch processing of data. The pipeline integrates multiple tools to efficiently manage, clean, and monitor the data workflow.

### 1. **Create Kafka Topics**
- Kafka topics are created using the `kafka-python` library. These topics serve as message queues for data ingestion into the pipeline.
- The API will be built to send data to these Kafka topics, allowing for seamless data streaming. Refer to the code for a clearer visual understanding

**Start Zookeeper:**
<p align="justify">
Apache ZooKeeper is used for coordinating and managing distributed systems, providing features like configuration management, leader election, and distributed locking.</p>

```
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
```

**Start Kafka:**
<p align="justify">
Apache Kafka is a distributed event streaming platform used for building real-time data pipelines and streaming applications.</p>

```
bin/kafka-server-start.sh config/server.properties
```

- Created a `folder-sink.properties` file to configure **Kafka Connect** and set up the **FileStreamSink Connector**. This setup enables consuming messages from a Kafka topic and storing them locally as JSON files using the `kafka/config` properties with the following configuration.

```
name=local-json-file-sink
connector.class=FileStreamSink
tasks.max=1
topics=kafka_test #(Changed to my topics)
file=/home/<my user>/connectors/sink/kafka_test.json #(Changed to my specified path)
# Use simple string for keys
key.converter=org.apache.kafka.connect.storage.StringConverter
# Use JSON for values (no schema)
value.converter=org.apache.kafka.connect.json.JsonConverter
value.converter.schemas.enable=false
```

**Run Kafka Connect:**
```
bin/connect-standalone.sh -daemon config/connect-standalone.properties config/folder-sink.properties
```

**Run Script:** 
```
python main.py
```

**Check Kafka topics:** 
```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic --from-beginning
```

Or

**Retrieve the current offsets for Kafka topics:**
```
bin/kafka-get-offsets.sh --bootstrap-server localhost:9092 --topic demo-get-offsets
```

### 2. **Batch Processing Initialization**
- Once the data is published to Kafka topics, it marks the beginning of the batch processing workflow.

### 3. **Data Cleaning in Databricks**
- The ingested data from Kafka is consumed and cleaned in **Databricks**, ensuring data consistency and quality.
- Databricks offers scalable and efficient processing of large datasets, making it a key component of the pipeline.

## Task 1 - Cleaning Dataframes containing Pinterest posts

1. **Handle Missing Data**: Replace empty entries and entries with no relevant data in each column with `None`.  
2. **Ensure Numeric Consistency**:  
   - Convert `follower_count` values to numbers and ensure the column data type is `int`.  
   - Verify that all columns containing numeric data have an appropriate numeric data type.  
3. **Clean `save_location` Data**: Extract only the save location path from the `save_location` column.  
4. **Rename the Index Column**: Change the column name `index` to `ind`.  
5. **Reorder Columns**: Structure the DataFrame in the following order:  
   - `ind`  
   - `unique_id`  
   - `title`  
   - `description`  
   - `follower_count`  
   - `poster_name`  
   - `tag_list`  
   - `is_image_or_video`  
   - `image_src`  
   - `save_location`  
   - `category`

```python
# Required Dictionairies
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import split

# Path to the JSON file in Databricks
file_path = "/FileStore/tables/df_pin/kafka_test-1.json"
file_type = "json"

# Read in JSON from the local DBFS location
df_pin = spark.read.format(file_type).load(file_path)

# Display DataFrame
# display(df_pin)

#Data Cleaning: Dropping Duplicates
df_pin = df_pin.dropDuplicates()
Drop_dup = df_pin.count() 
print(f'{Drop_dup} rows')

# Replace  empty entries and entries with no relevant data with None
df_pin = df_pin.replace({
    'User Info Error': None,
    'No description available Story format': None,
    'Image src error.': None,
    'N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e': None,
    'No Title Data Available': None
}, subset=['follower_count', 'description', 'image_src', 'tag_list', 'title'])


# Converts K = 1000 and M = 1000000 into digits
df_pin = df_pin.withColumn(
    "follower_count",
    when(col("follower_count").contains("k"), 
         regexp_replace(col("follower_count"), "k", "").cast("double") * 1000)
    .when(col("follower_count").contains("M"), 
         regexp_replace(col("follower_count"), "M", "").cast("double") * 1000000)
    .otherwise(col("follower_count").cast("integer"))
    .cast(IntegerType())
)

# Columns containing numeric data has a numeric data type
numeric_columns = ["downloaded", "index"]
for col_name in numeric_columns:
    df_pin = df_pin.withColumn(col_name, col(col_name).cast(IntegerType()))

# Clean the data in the save_location column to include only the save location path
df_pin = df_pin.withColumn("save_location", split("save_location", "Local save in ").getItem(1))

# index column to ind. 
df_pin = df_pin.withColumnRenamed("index", "ind")


# Reorder the DataFrame columns 
df_pin = df_pin.select(
    "ind", "unique_id", "title", "description", "follower_count", 
    "poster_name", "tag_list", "is_image_or_video", "image_src", 
    "save_location", "category"
)

clean_pin = df_pin
display(clean_pin)
```

## Task 2 - Cleaning Dataframes containing geolocation information

1. **Create a new column** `coordinates` that stores an array combining the `latitude` and `longitude` values.  
2. **Remove** the `latitude` and `longitude` columns from the DataFrame.  
3. **Convert** the `timestamp` column from a string format to a timestamp data type.  
4. **Reorder** the DataFrame columns in the following order:  
   - `ind`  
   - `country`  
   - `coordinates`  
   - `timestamp`

``` python
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType

# Path to the JSON file in Databricks
file_path = "/FileStore/tables/df_geo/geo_mo.json"
file_type = "json"

# Read in JSON from the local DBFS location
df_geo = spark.read.format(file_type).load(file_path)
# display(df_geo)

# drop dulpicate rows
df_geo = df_geo.dropDuplicates()
Drop_dup = df_geo.count() 
print(f'{Drop_dup} rows')

# Create the coordinates column
df_geo = df_geo.withColumn("coordinates", F.array("latitude", "longitude"))

# Drop the latitude and longitude columns
df_geo = df_geo.drop("latitude", "longitude")

#Convert the timestamp column to TimestampType
df_geo = df_geo.withColumn("timestamp", F.col("timestamp").cast(TimestampType())) 

# Reorder columns
df_geo = df_geo.select("ind", "country", "coordinates", "timestamp")
clean_geo = df_geo
display(clean_geo)
```

## Task 3 - Cleaning Dataframes containing users information

1. **Create a new column** `user_name` by concatenating the values from `first_name` and `last_name` columns.  
2. **Remove** the `first_name` and `last_name` columns from the DataFrame.  
3. **Convert** the `date_joined` column from a string format to a timestamp data type.  
4. **Reorder** the DataFrame columns in the following order:  
   - `ind`  
   - `user_name`  
   - `age`  
   - `date_joined`
 
```python
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType

# Path to the JSON file in Databricks
file_path = "/FileStore/tables/df_user/user_mo.json"
file_type = "json"

# Read in JSON from the local DBFS location
df_user = spark.read.format(file_type).load(file_path)
display(df_user)

# drop dulpicate rows
df_user = df_user.dropDuplicates()
Drop_dup = df_user.count() 
print(f'{Drop_dup} rows')

# Create a new column user_name that concatenates the information found in the first_name and last_name columns
df_user = df_user.withColumn("user_name", concat("first_name", lit(" "), "last_name"))

# Drop the first_name and last_name columns
df_user = df_user.drop("first_name", "last_name")

# Convert the date_joined column from a string to a timestamp data type
df_user = df_user.withColumn("date_joined", F.col("date_joined").cast(TimestampType()))

# Reorder columns
df_user = df_user.select("ind", "user_name", "age", "date_joined")
clean_user = df_user
display(clean_user)
```

## Task 4 - Find the most popular Category in each country
1. Find the most popular Pinterest category people post to based on their country.
2. Your query should return a DataFrame that contains the following columns:
   - country
   - category
   - category_count, a new column containing the desired query output
``` python
from pyspark.sql.window import Window

# Joining geo and pin cleaned data 
joined_df = clean_geo.join(clean_pin, "ind")
# display(joined_df)

# Group by country and category, count occurrences, and find the most popular category
window = Window.partitionBy("country").orderBy(F.desc("category_count"))

final_df = joined_df.groupBy("country", "category") \
                    .agg(F.count("*").alias("category_count")) \
                    .withColumn("rank", F.rank().over(window)) \
                    .filter(F.col("rank") == 1) \
                    .drop("rank")

# Display the final result
final_df.show()
```

## Task 5 - Find the most popular Category in each year

1. Count the number of posts in each category for every year between 2018 and 2022.
2. Return a DataFrame with the following columns:
   - **post_year**: The year extracted from the `timestamp` column.
   - **category**: The category of the post.
   - **category_count**: The number of posts in each category per year.

``` python
df_result = (df_pin.join(df_geo, 'ind', 'inner')
             .withColumn("timestamp", F.col("timestamp").cast("timestamp"))
             .filter((F.year("timestamp") >= 2018) & (F.year("timestamp") <= 2022))
             .withColumn("post_year", F.year("timestamp"))
             .groupBy("post_year", "category")
             .agg(F.count("*").alias("category_count"))
             .orderBy("post_year", "category"))


# Display the final result
display(df_result)
```

## Task 6 - Find the user with most followers in each country

**Step 1**: For each country find the user with the most followers.
- Your query should return a DataFrame that contains the following columns:
   - country
   - poster_name
   - follower_count

``` python
window_spec = Window.partitionBy("country")

# Filter users with the maximum follower count per country
country_followers = (
    joined_df.withColumn("max_follower_count", max("follower_count").over(window_spec))
    .filter(col("follower_count") == col("max_follower_count"))
    .select("country", "poster_name", "follower_count")
    .dropDuplicates()
    .orderBy(col("follower_count").desc())
)

display(country_followers)
```

**Step 2**: Based on the above query, find the country with the user with most followers.
- Your query should return a DataFrame that contains the following columns:
   - country
   - follower_count
 
```python
country_followers.createOrReplaceTempView("country_followers")

# Run the Spark SQL query
most_followers = spark.sql("""
    SELECT country, MAX(follower_count) AS follower_count
    FROM country_followers
    GROUP BY country
    ORDER BY follower_count DESC
    LIMIT 1
""")

# Display the result
display(most_followers)
```

## Task 7 - Popular Ctaegoty for different age groups
**Create Age Groups**:  
   - Categorize users based on their age into the following groups:  
     - 18-24  
     - 25-35  
     - 36-50  
     - 50+

**Return a DataFrame** with the following columns:  
   - `age_group`: The age group of the users.  
   - `category`: The category in which the posts were made.  
   - `category_count`: The count of posts in each category for the corresponding age group.

``` python
age_group = spark.sql("""
WITH AGERANGE AS (
    SELECT 
        u.age, 
        p.category,
        CASE 
            WHEN u.age BETWEEN 18 AND 24 THEN '18-24'
            WHEN u.age BETWEEN 25 AND 35 THEN '25-35'
            WHEN u.age BETWEEN 36 AND 50 THEN '36-50'
            ELSE '+50'
        END AS age_group
    FROM global_temp.clean_user u
    INNER JOIN global_temp.clean_pin p 
        ON u.ind = p.ind
),

Categories AS (
    SELECT 
        age_group, 
        category, 
        COUNT(*) AS category_count,
        RANK() OVER (PARTITION BY age_group ORDER BY COUNT(*) DESC)
    FROM AGERANGE
    GROUP BY age_group, category
)

SELECT age_group, category, category_count 
FROM Categories 
""")

display(age_group)
```

## Task 8 - Find the median follower count for different age groups
- What is the median follower count for users in the following age groups:
   - 18-24  
   - 25-35  
   - 36-50  
   - 50+
 
**Return a DataFrame** with the following columns:  
   - `age_group`: A new column based on the original age column  
   - `median_follower_count,`: A new column containing the desired query output 
``` python
median_followers = spark.sql("""
WITH AgeGroups AS (
    SELECT
        u.age,
        p.follower_count,
        CASE
            WHEN u.age BETWEEN 18 AND 24 THEN '18-24'
            WHEN u.age BETWEEN 25 AND 35 THEN '25-35'
            WHEN u.age BETWEEN 36 AND 50 THEN '36-50'
            ELSE '+50'
        END AS age_group
    FROM global_temp.clean_user u
    JOIN global_temp.clean_pin p
    ON u.ind = p.ind
)

SELECT
    age_group, percentile(follower_count, 0.5) AS median_followers_count
FROM AgeGroups
GROUP BY age_group
ORDER BY median_followers_count DESC
""")

display(median_followers)
```

## Task 9 - How many users have joined each year
- *Find how many users have joined between 2015 and 2020.
- **Return a DataFrame** with the following columns:  
   - `post_year`, A new column that contains only the year from the timestamp column 
   - `number_users_joined,`: A new column containing the desired query output

``` python
user_joined = spark.sql("""
SELECT
    YEAR(date_joined) AS post_year,
    COUNT(*) AS number_users_joined
FROM global_temp.clean_user
WHERE YEAR(date_joined) BETWEEN 2015 AND 2020
GROUP BY post_year
ORDER BY post_year
""")

display(user_joined)
```

## Task 10 - Find the median follower count
- Find how many users have joined between 2015 and 2020.
- **Return a DataFrame** with the following columns:  
   - `post_year`, A new column that contains only the year from the timestamp column 
   - `median_follower_count,`: A new column containing the desired query output

``` python
user_joined = spark.sql("""
SELECT
    YEAR(date_joined) AS post_year,
    COUNT(*) AS number_users_joined
FROM global_temp.clean_user
WHERE YEAR(date_joined) BETWEEN 2015 AND 2020
GROUP BY post_year
ORDER BY post_year
""")

display(user_joined)
```

## Task 11 - Find the most popular Category in each year
- Find how many users have joined between 2015 and 2020.
- **Return a DataFrame** with the following columns:
   - `age_group`, a new column based on the original age column
   - `post_year`, A new column that contains only the year from the timestamp column
   - `median_follower_count,`: A new column containing the desired query output

``` python
median_follower_age = spark.sql("""
WITH AGEGROUPS AS (
    SELECT CASE
        WHEN age BETWEEN 18 AND 24 THEN '18-24'
        WHEN age BETWEEN 25 AND 35 THEN '25-35'
        WHEN age BETWEEN 36 AND 50 THEN '36-50'
        ELSE '+50' 
    END AS age_group,
    YEAR(CAST(u.date_joined AS DATE)) AS post_year,
    p.follower_count
    FROM global_temp.clean_user u
    JOIN global_temp.clean_pin p 
    ON u.ind = p.ind
    WHERE YEAR(CAST(u.date_joined AS DATE)) BETWEEN 2015 AND 2020
)
SELECT age_group, post_year, percentile_approx(follower_count, 0.5, 100) AS median_follower_count
FROM AGEGROUPS
GROUP BY age_group, post_year
ORDER BY age_group, post_year
""")

display(median_follower_age)
```

### 4. **Workflow Monitoring with Apache Airflow**
- After cleaning, the data is uploaded to **Apache Airflow**.
- Airflow is used to orchestrate and monitor workflows, ensuring that all batch processes are executed correctly and on schedule.

## Benefits of the Workflow
- **Scalability**: Kafka and Databricks handle high-volume data ingestion and processing.
- **Automation**: Apache Airflow ensures automated and reliable monitoring of workflows.
- **Clean Data**: Databricks ensures the data processed downstream is consistent and ready for use.


This pipeline forms the backbone of the batch processing system, enabling efficient data ingestion, cleaning, and workflow monitoring.
