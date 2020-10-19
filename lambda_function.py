import requests
from datetime import date
import simplejson
import json
import boto3
import time

stream_name = 'stream-heat-index'

kinesis_client = boto3.client('kinesis', region_name='us-east-1')

values = {
    "RECIFE": [],
    "PETROLINA": [],
    "ARCO VERDE": [],
    "GARANHUNS": [],
    "SURUBIM": [],
    "CABROBÓ": [],
    "CARUARU": [],
    "IBIMIRIM": [],
    "SERRA TALHADA": [],
    "FLORESTA": [],
    "PALMARES": [],
    "OURICURI":  [],
    "SALGUEIRO": [],
}


def get_values_from_api(values):
    count = 0

    try:
        # testData 2020-05-02
        today = str(date.today())
        r = requests.get(
            f'https://apitempo.inmet.gov.br/estacao/dados/{today}')
        if(r.status_code == 200):
            data = []
            try:
                data = r.json()
            except simplejson.errors.JSONDecodeError:
                raise Exception('could not encode empty data') from None
            iterator = filter(lambda x: x["UF"] == "PE", data)

            for element in iterator:
                count += 1
                if element["DC_NOME"] in values.keys():
                    values[element["DC_NOME"]].append(element)
            return values
        elif(r.status_code != 200):
            r.raise_for_status()
    except requests.exceptions.RequestException as identifier:
        print(identifier)


def put_data_to_stream(formattedData):
    for i in formattedData.keys():
        send_pkg = []
        for j in range(len(formattedData[i])):
            if(formattedData[i][j]["UMD_MAX"]):
                send_pkg.append(formattedData[i][j])
            else: 
                continue
        print(json.dumps(send_pkg))
        response = kinesis_client.put_records(
            Records=[{
                'Data': json.dumps({"message_type":send_pkg, "count":len(formattedData[i])}),
                'PartitionKey': 'aa-bb'
                }],
                StreamName=stream_name
                )
        # print(response)


def lambda_handler(event, context):
    filteredDataFromInmet = get_values_from_api(values)
    if(filteredDataFromInmet):
        put_data_to_stream(filteredDataFromInmet)
    return {
        'statusCode': 200,
        'body': json.dumps(len(filteredDataFromInmet))
    }

get_values_from_api(values)
put_data_to_stream(values)