import logging
import os
import time
import datetime
import boto3
from dlq_helper import is_recoverable, send_to_retry_queue

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# in minutes
CIRCUIT_BREAKER_TTL = 2

table = boto3.resource('dynamodb').Table('CircuitBreakerStatus')

def lambda_handler(event, context):
    logger.warning('Handling error events '+str(event)+ ' context '+str(context))
    if event and event['Records']:
        for record in event['Records']:
            logger.warning('Handling error record '+str(record))
            if is_recoverable(record, context):
                logger.info('It is recoverable, sending to retry queue!')
                send_to_retry_queue(record)
            else:
                logger.info('It is not recoverable, open the circuit breaker and report the incident!')
                open_circuit()

def open_circuit():
    ttl = datetime.datetime.today() + datetime.timedelta(minutes=CIRCUIT_BREAKER_TTL)
    expiryDateTime = int(time.mktime(ttl.timetuple())) 
    table.put_item(
        Item = { 
          'ServiceName': 'ServiceB', 
          'ExpireTimeStamp': expiryDateTime,
          'CircuitStatus': 'OPEN'
          })

