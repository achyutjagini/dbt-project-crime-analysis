from kafka import KafkaConsumer
import logging
import time
from pymongo import MongoClient
import json


logger = logging.getLogger(__name__)
client = MongoClient('mongodb://localhost:27017')
#collection = client.numtest.numtest

db = client["mydatabase"]
Collection = db["data"]

with open('police-department-calls-for-service.json') as f:
	file_data = json.load(f)


if isinstance(file_data, list):
    Collection.insert_many(file_data)  
else:
    Collection.insert_one(file_data)


def run_consumer_server():
    consumer = KafkaConsumer(
        "crime-analysis",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        group_id="crime_consumer"
    )

    for message in consumer:
        #collection.insert_many(data)
        print(f"Message: {message.value.decode('utf-8')}")
        


if __name__ == "__main__":
    run_consumer_server()
