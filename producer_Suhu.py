from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

gudang_ids = ['G1', 'G2', 'G3']

while True:
    for gudang_id in gudang_ids:
        data = {"gudang_id": gudang_id, "suhu": random.randint(75, 90)}
        producer.send('sensor-suhu-gudang', value=data)
        print(f"Sent suhu: {data}")
    time.sleep(1)
