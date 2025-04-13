from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.providers.databricks.hooks.databricks import DatabricksHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

# Define Databricks connection ID (configured in Airflow UI)
DATABRICKS_CONN_ID = 'databricks_default'

# Define Databricks Job ID 
DATABRICKS_JOB_ID = '  '  #input JOB ID

# Define default arguments for Airflow DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

# Function to fetch cleaned data from Databricks
def fetch_cleaned_data():
    """Fetch cleaned data from Databricks and save locally."""
    hook = DatabricksHook(databricks_conn_id=DATABRICKS_CONN_ID)
    
    # Query Databricks table containing cleaned data
    sql = "SELECT * FROM cleaned_data_table"
    df = hook.get_pandas_df(sql)
    
    # Save to CSV locally or upload to another destination
    df.to_csv("/path/to/airflow_upload/cleaned_data.csv", index=False)

# Define the Airflow DAG
with DAG(
    'databricks_airflow_pipeline',
    start_date=datetime(2025, 4, 3),
    schedule_interval='@daily',
    catchup=False,
    default_args=default_args,
) as dag:

    # Task: Run the existing Databricks job (using Job ID)
    opr_run_existing_job = DatabricksRunNowOperator(
        task_id='run_databricks_job',
        databricks_conn_id=DATABRICKS_CONN_ID,
        job_id=DATABRICKS_JOB_ID,
    )

    # Task: Fetch Cleaned Data from Databricks
    fetch_data = PythonOperator(
        task_id='fetch_cleaned_data',
        python_callable=fetch_cleaned_data,
    )

    # Define task dependencies: Run Databricks job first, then fetch data
    opr_run_existing_job >> fetch_data
