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

display(df_pin)
```

## Task 2 - Cleaning Dataframes containing geolocation information
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
display(df_geo)
```

## Task 3 - Cleaning Dataframes containing users information

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
df_user = df_user.withColumn("user_name", F.array("first_name", "last_name"))

# Drop the first_name and last_name columns
df_user = df_user.drop("first_name", "last_name")

# Convert the date_joined column from a string to a timestamp data type
df_user = df_user.withColumn("date_joined", F.col("date_joined").cast(TimestampType()))

# Reorder columns
df_user = df_user.select("ind", "user_name", "age", "date_joined")
display(df_user)
```

### 4. **Workflow Monitoring with Apache Airflow**
- After cleaning, the data is uploaded to **Apache Airflow**.
- Airflow is used to orchestrate and monitor workflows, ensuring that all batch processes are executed correctly and on schedule.

## Benefits of the Workflow
- **Scalability**: Kafka and Databricks handle high-volume data ingestion and processing.
- **Automation**: Apache Airflow ensures automated and reliable monitoring of workflows.
- **Clean Data**: Databricks ensures the data processed downstream is consistent and ready for use.


This pipeline forms the backbone of the batch processing system, enabling efficient data ingestion, cleaning, and workflow monitoring.
