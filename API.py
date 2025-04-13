from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json
import yaml
from input_output import load_db_credentials

app = Flask(__name__)

# MySQL Configuration using credentials from db_creds.yaml
config = load_db_credentials()
MYSQL_CONFIG = {
    'host': config['HOST'],
    'user': config['USER'],
    'password': config['PASSWORD'],
    'database': config['DATABASE'],
    'port': config['PORT']
}

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
VALID_TOPICS = ['mo_user.pin', 'mo_user.geo', 'mo_user.user']

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route("/", methods=["GET"])
def root():
    print("Welcome to the Kafka API")
    return {
        "StatusCode": 200
    }

## See posting_emilation part
@app.route('/send-data', methods=['POST'])
def send_data():
    try:
        # Parse request data
        data = request.json
        topic_name = data.get('topic_name')
        event_data = data.get("data")

        # Validate if the topic is in the allowed list
        if topic_name not in VALID_TOPICS:
            return jsonify(data={'error': 'Invalid topic_name'}, status=400)

        # Validate if event_data exists and is a valid dictionary
        if not event_data:
            return jsonify(data={'error': 'Event data is missing or invalid'}, status=400)

        # Send the data to Kafka
        response = producer.send(topic_name, value=event_data)
        return jsonify(data={'message': f'Data sent to Kafka topic {response}'}, status=200)

    except Exception as e:
        return jsonify(data={'error': f"An error occurred: {str(e)}"}, status=500)
def start_flask():
    app.run(debug=False)

if __name__ == '__main__':
    app.run(debug=False)