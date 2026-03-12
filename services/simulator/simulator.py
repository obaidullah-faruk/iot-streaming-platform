import os
import time
import json
import random
import logging
from datetime import datetime
from confluent_kafka import Producer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'iot.telemetry')
DEVICE_ID = os.getenv('DEVICE_ID', f'device_{random.randint(100, 999)}')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def generate_telemetry():
    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2),
        "vibration": round(random.uniform(0.0, 5.5), 2)
    }

def main():
    logger.info(f"Starting IoT Simulator for device: {DEVICE_ID}")
    logger.info(f"Connecting to Kafka: {KAFKA_BOOTSTRAP_SERVERS}")

    # Producer configuration
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': f'simulator-{DEVICE_ID}'
    }

    producer = Producer(conf)

    try:
        while True:
            # Generate data
            data = generate_telemetry()
            logger.info(f"Generated data: {data}")

            # Produce to Kafka
            producer.produce(
                KAFKA_TOPIC, 
                key=DEVICE_ID, 
                value=json.dumps(data).encode('utf-8'),
                callback=delivery_report
            )

            # Wait for any outstanding messages to be delivered and delivery report callbacks to be triggered.
            producer.poll(0)

            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping simulator...")
    finally:
        # Wait for any outstanding messages to be delivered and delivery report callbacks to be triggered.
        producer.flush()

if __name__ == "__main__":
    main()
