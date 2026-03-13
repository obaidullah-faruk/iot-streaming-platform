import json
import logging
import os
import sys
import time
from datetime import datetime
from app.db import engine
from sqlalchemy.exc import OperationalError
from confluent_kafka import Consumer, KafkaError, KafkaException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from dateutil import parser
from app.db import SessionLocal
from database.models.schema import Device, Telemetry, Alert
from app.processor import detect_anomalies


logger = logging.getLogger(__name__)

def wait_for_db():
    
    max_retries = 30
    retry_delay = 2
    
    logger.info("Checking database connection...")
    for i in range(max_retries):
        try:
            with engine.connect() as _:
                logger.info("Successfully connected to the database.")
                return
        except OperationalError:
            logger.warning(f"Database not ready. Retrying in {retry_delay}s... ({i+1}/{max_retries})")
            time.sleep(retry_delay)
    
    logger.error("Failed to connect to the database. Exiting.")
    sys.exit(1)

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure DB is up before connecting to Kafka
    wait_for_db()

    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
    GROUP_ID = os.getenv('KAFKA_GROUP_ID')

    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

    consumer = Consumer(conf)
    
    try:
        # Check if topic exists/wait for it
        topics = consumer.list_topics().topics
        while KAFKA_TOPIC not in topics:
            logger.warning(f"Topic {KAFKA_TOPIC} not found. Waiting...")
            time.sleep(2)
            topics = consumer.list_topics().topics

        consumer.subscribe([KAFKA_TOPIC])
        logger.info(f"Subscribed to topic: {KAFKA_TOPIC}")

        db: Session = SessionLocal()

        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                try:
                    # Parse data map
                    data = json.loads(msg.value().decode('utf-8'))
                    device_id = data['device_id']
                    timestamp_dt = parser.parse(data['timestamp'])
                    
                    # 1. Update/Upsert Device log
                    insert_stmt = insert(Device).values(
                        device_id=device_id,
                        first_seen=timestamp_dt,
                        last_seen=timestamp_dt
                    )
                    
                    # On conflict, update last_seen
                    do_update_stmt = insert_stmt.on_conflict_do_update(
                        index_elements=['device_id'],
                        set_=dict(last_seen=timestamp_dt)
                    )
                    db.execute(do_update_stmt)
                    
                    # 2. Insert Telemetry
                    telemetry_entry = Telemetry(
                        device_id=device_id,
                        temperature=data.get('temperature'),
                        humidity=data.get('humidity'),
                        vibration=data.get('vibration'),
                        timestamp=timestamp_dt
                    )
                    db.add(telemetry_entry)
                    
                    # 3. Process Anomalies
                    alerts = detect_anomalies(data)
                    for alert in alerts:
                        alert_entry = Alert(
                            device_id=alert['device_id'],
                            rule_name=alert['rule_name'],
                            description=alert['description'],
                            timestamp=parser.parse(alert['timestamp'])
                        )
                        db.add(alert_entry)
                        logger.warning(f"ALERT REGISTERED: {alert['rule_name']} for {device_id}")

                    db.commit()

                    # 4. Commit to Kafka after DB success
                    consumer.commit(asynchronous=False)
                    logger.info(f"Processed offset: {msg.offset()} for {device_id}")

                except json.JSONDecodeError as e:
                    logger.error(f"Malformed message skipped: {msg.value()} - Error: {e}")
                    consumer.commit(asynchronous=False)
                except Exception as e:
                    logger.exception(f"Error processing message, rolling back DB transaction: {e}")
                    db.rollback()

    except KeyboardInterrupt:
        logger.info("Worker stopped automatically.")
    finally:
        consumer.close()
        logger.info("Consumer closed.")

if __name__ == '__main__':
    main()
