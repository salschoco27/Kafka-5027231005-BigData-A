# gudang_monitoring/app/producer_suhu.py
import time
import json
import random
import os
from kafka import KafkaProducer
from kafka.errors import KafkaError

KAFKA_TOPIC = "sensor-suhu-gudang"
KAFKA_BROKERS = os.environ.get("KAFKA_BROKERS", "kafka:9092")

GUDANG_IDS = ["G1", "G2", "G3", "G4"] # Added G4 for more variety

def get_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                client_id="suhu-producer"
            )
            print("Suhu Producer connected to Kafka successfully!")
            return producer
        except KafkaError as e:
            print(f"Suhu Producer: Error connecting to Kafka: {e}, retrying in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    producer = get_producer()
    if not producer:
        print("Failed to create Suhu Producer. Exiting.")
        exit(1)
        
    try:
        while True:
            gudang_id = random.choice(GUDANG_IDS)
            # Generate some values that sometimes exceed the threshold
            suhu = random.randint(70, 90) 
            
            message = {
                "gudang_id": gudang_id,
                "suhu": suhu
            }
            
            print(f"Sending Suhu: {message}")
            producer.send(KAFKA_TOPIC, value=message)
            producer.flush() # Ensure messages are sent
            time.sleep(1) # Send data every second
            
    except KeyboardInterrupt:
        print("Suhu Producer interrupted. Closing...")
    except Exception as e:
        print(f"Suhu Producer encountered an error: {e}")
    finally:
        if producer:
            producer.close()
            print("Suhu Producer closed.")
