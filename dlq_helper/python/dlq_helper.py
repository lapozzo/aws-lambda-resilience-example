import logging
import boto3
import os

sqs = boto3.client('sqs')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_RETRIES = 2
if os.environ['MAX_RETRIES']:
   MAX_RETRIES = int(os.environ['MAX_RETRIES'])

if os.environ['RETRY_QUEUE_URL']:
   queue_url = os.environ['RETRY_QUEUE_URL']

def is_recoverable(record, context):
    msg_attrs = record['messageAttributes']
    retries=1
    if 'retries' in msg_attrs:
        retries = int(msg_attrs['retries']['stringValue'])

    logging.info('Current attempt:'+str(retries))

    if retries < MAX_RETRIES:
        return True
    return False

def send_to_retry_queue(record):
    msg_attrs = record['messageAttributes']
    retries = 1
    if 'retries' in msg_attrs:
        retries = int(msg_attrs['retries']['stringValue'])+1
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'retries': {
                'DataType': 'Number',
                'StringValue': str(retries)
            }
        },
        MessageBody=record['body']
    )