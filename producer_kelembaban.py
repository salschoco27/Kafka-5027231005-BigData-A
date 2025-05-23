# gudang_monitoring/app/producer_kelembaban.py
import time
import json
import random
import os
from kafka import KafkaProducer
from kafka.errors import KafkaError

KAFKA_TOPIC = "sensor-kelembaban-gudang"
KAFKA_BROKERS = os.environ.get("KAFKA_BROKERS", "kafka:9092")

GUDANG_IDS = ["G1", "G2", "G3", "G4"]

def get_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                client_id="kelembaban-producer"
            )
            print("Kelembaban Producer connected to Kafka successfully!")
            return producer
        except KafkaError as e:
            print(f"Kelembaban Producer: Error connecting to Kafka: {e}, retrying in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    producer = get_producer()
    if not producer:
        print("Failed to create Kelembaban Producer. Exiting.")
        exit(1)

    try:
        while True:
            gudang_id = random.choice(GUDANG_IDS)
            # Generate some values that sometimes exceed the threshold
            kelembaban = random.randint(60, 80)

            message = {
                "gudang_id": gudang_id,
                "kelembaban": kelembaban
            }
            
            print(f"Sending Kelembaban: {message}")
            producer.send(KAFKA_TOPIC, value=message)
            producer.flush()
            time.sleep(1) # Send data every second
            
    except KeyboardInterrupt:
        print("Kelembaban Producer interrupted. Closing...")
    except Exception as e:
        print(f"Kelembaban Producer encountered an error: {e}")
    finally:
        if producer:
            producer.close()
            print("Kelembaban Producer closed.")
