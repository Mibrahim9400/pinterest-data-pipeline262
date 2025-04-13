import requests
import time
import random
import json

from threading import Thread
from sqlalchemy import text
from input_output import load_db_credentials
from db_conn import AWSDBConnector
from API import start_flask

# Load database credentials and create the DB engine
creds = load_db_credentials()               # Load credentials                       
new_connector = AWSDBConnector(creds)       # Create DB connector object
engine = new_connector.create_db_connector()   

# Start the Flask API on a background thread
flask_thread = Thread(target=start_flask, daemon=True)
flask_thread.start()

def random_row_from_table(connection: str, table_name: str, random_row: str) -> None:
    """
    Fetch a single random row from a given table.

    :param connection: The SQLAlchemy connection object
    :param table_name: The name of the table to query
    :param random_row: The random row index to fetch
    :return: A dictionary representing the fetched row
    """
    query = text(f"SELECT * FROM {table_name} LIMIT {random_row}, 1")
    result = connection.execute(query)
    for row in result:
        return dict(row._mapping)
    return None

def send_post_request(payload, url="http://127.0.0.1:5000/send-data"):
    """
    Send a POST request to the Flask API.

    :param payload: The payload to send in the request
    """
    try:
        # response = requests.post(url, )
        response = requests.post(
            url, 
            data=json.dumps(payload, default=str), 
            headers={"Content-Type": "application/json"}
        )
        print(response.json())
    except Exception as e:
        print(f"Error sending POST request: {e}")

def run_infinite_post_data_loop():
    """
    Continuously fetch random rows from the database and send them as POST requests.
    """
    while True:
        try:
            time.sleep(random.uniform(0, 2))
            random_row = random.randint(0, 11000)

            # Use the engine to connect to the DB and fetch data
            with engine.connect() as connection:
                # pin_result = random_row_from_table(connection, "pinterest_data", random_row)

                # if pin_result:           
                #     send_post_request({
                #         "topic_name": "mo_user.pin",  
                #         "data": pin_result    
                #     })

                # geo_result = random_row_from_table(connection, "geolocation_data", random_row)

                # if geo_result:           
                #     send_post_request({
                #         "topic_name": "mo_user.geo",  
                #         "data": geo_result    
                #     })

                user_result = random_row_from_table(connection, "user_data", random_row)

                if user_result:           
                    send_post_request({
                        "topic_name": "mo_user.user",  
                        "data": user_result    
                    })

                # Logging the results
                # print(f"Pin result: {pin_result}")
                # print(f"Geo result: {geo_result}")
                print(f"User result: {user_result}")

        except Exception as e:
            print(f"Error occurred: {e}")
            break  # Exit the loop if an error occurs

if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')
