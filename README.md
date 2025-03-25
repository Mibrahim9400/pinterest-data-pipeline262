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
./bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
```

**Start Kafka:**
<p align="justify">
Apache Kafka is a distributed event streaming platform used for building real-time data pipelines and streaming applications.</p>

```
./bin/kafka-server-start.sh config/server.properties
```

**Run Script:** 
```
python main.py
```

### 2. **Batch Processing Initialization**
- Once the data is published to Kafka topics, it marks the beginning of the batch processing workflow.

### 3. **Data Cleaning in Databricks**
- The ingested data from Kafka is consumed and cleaned in **Databricks**, ensuring data consistency and quality.
- Databricks offers scalable and efficient processing of large datasets, making it a key component of the pipeline.

### 4. **Workflow Monitoring with Apache Airflow**
- After cleaning, the data is uploaded to **Apache Airflow**.
- Airflow is used to orchestrate and monitor workflows, ensuring that all batch processes are executed correctly and on schedule.

## Benefits of the Workflow
- **Scalability**: Kafka and Databricks handle high-volume data ingestion and processing.
- **Automation**: Apache Airflow ensures automated and reliable monitoring of workflows.
- **Clean Data**: Databricks ensures the data processed downstream is consistent and ready for use.


This pipeline forms the backbone of the batch processing system, enabling efficient data ingestion, cleaning, and workflow monitoring.
