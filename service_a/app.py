import logging
import boto3
import requests
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table = boto3.resource('dynamodb').Table('CircuitBreakerStatus')

def lambda_handler(event, context):
    logger.info("Processing event: "+str(event))
    body = unpack_body(event)
    logger.info("Processing body: "+str(body))
    try:
        logger.info("Calling Service B")
        service_b_response = call_service_b(body)
    except Exception:
        logger.info("Error calling Service B!")
        service_b_response = 'Service B with error!'
        raise
    finally:
        logger.info('Service B response:'+str(service_b_response))

def call_service_b(body):
    circuit_status = get_circuit_status()
    if circuit_status == 'OPEN':
        return 'Service B not called, Circuit is Open, this is the fallback response!'
    else:
        if 'simulate_error_code' in body:
            status_code = body['simulate_error_code']
            logger.warning('simulating error calling service b, status code '+str(status_code))
            raise requests.HTTPError('http://serviceb.domain.com', status_code)
        else:
            logger.info('Service B called with success!')
            return 'Service B called with success!'

def get_circuit_status():
    response = table.get_item(
        Key={
            'ServiceName': 'ServiceB'
        }
    )
    if 'Item' in response:
        return response['Item']['CircuitStatus']
    return 'CLOSED'

# helper function that unpack the body when the message comes from retry queue
def unpack_body(event):
    if 'Records' in event:
        return json.loads(event['Records'][0]['body'])
    return event
