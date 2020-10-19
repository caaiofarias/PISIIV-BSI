from __future__ import print_function
import requests

DEVICE_ID = "4206eb00-1169-11eb-af98-19366df12767"
DEVICE_TOKEN = "RMsGEBCTcClQdjLhhc9p"

THINGSBOARD_HOST="demo.thingsboard.io"

def send_data_to_tb(data):
    try:
        url = 'http://' + THINGSBOARD_HOST + '/api/v1/' + DEVICE_TOKEN + '/telemetry'
        requests.post(url, json=data)
    except ConnectionError:
        print('Failed to send data.')

def lambda_handler(event, context):
    for record in event['Records']:
       print ("test")
       payload=json.loads(record["body"])
       if(len(payload) > 0):
           data = {"temperatura":payload[2], "hindex":payload[1], "station":payload[0]}
           send_data_to_tb(data)
       print(str(payload))
