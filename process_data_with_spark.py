"""

aws emr add-steps --cluster-id j-23EEAM3NN5CQN --steps Type=Spark,Name="Kinesis-SQL",ActionOnFailure=CONTINUE,Args=[--jars,s3://sparkkinesis/spark-sql-kinesis_2.11-1.2.1_spark-2.4-SNAPSHOT.jar,s3://sparkkinesis/kinesis_example.py,kinesis-sql,pyspark-kinesis,https://kinesis.us-east-1.amazonaws.com,us-east-1]

"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructField, StructType, StringType, IntegerType
import boto3
import json

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: kinesis_example.py <app-name> <stream-name> <endpoint-url> <region-name>")
        sys.exit(-1)
    applicationName, streamName, endpointUrl, regionName = sys.argv[1:]
    print('Criando o spark')
    spark = SparkSession \
        .builder \
        .appName(applicationName) \
        .getOrCreate()
    print('spark finalizado')
    print(spark)
    kinesis = spark \
            .readStream \
            .format("kinesis") \
            .option("streamName", streamName) \
            .option("endpointUrl", endpointUrl)\
            .option("region", regionName) \
            .option("startingPosition", "earliest")\
            .load()\

    schema = StructType([
                StructField("message_type", StringType()),
                StructField("count", IntegerType())])
    print(schema.__str__())
    print(schema)
    print("teste de stream")

    def convertCtoF(temp):
        return (temp * 1.8) + 32
    
    def convertFtoC(temp):
        return ((temp - 32) * 5) / 9

    def calculate_heat_index(data):
        heat_index_list = []
        for i in range(len(data)):
            if((data[i]["TEM_MAX"] != None and data[i]["TEM_MIN"] != None) or (data[i]["UMD_MAX"] != None and data[i]["UMD_MAX"] != None )):
                temp_media = 1.0

                try:
                    temp_media = (convertCtoF(float(data[i]["TEM_MAX"])) + convertCtoF(float(data[i]["TEM_MIN"]))) / 2
                except:
                    print('temperatura except ' + data[i]["TEM_MIN"])
                    continue
                umd_media = 1.0
                try:
                    umd_media = ((float(data[i]["UMD_MAX"]) + float(data[i]["UMD_MIN"])) / 2) / 100
                except:
                    print('media da umidade ' + str(umd_media))
                    continue
                heat_index = 1.1 * temp_media - 10.3 + 0.047 * umd_media
                if(heat_index < 80):
                    heat_index_list.append(heat_index)
                else:
                    heat_index = -42.379 + (2.04901523 * temp_media) + \
                        (10.14333127 * umd_media) - (6.83783 * 10**-3) * temp_media**2 \
                            - (5.481717 * 10 ** -2) * umd_media ** 2 + 1.22874 * (10 ** -3) \
                                * (temp_media ** 2) * umd_media + 8.5282 * (10**-4) * temp_media \
                                    * umd_media ** 2 - (1.99 * 10**-6) * temp_media**2 * umd_media ** 2
                    if(temp_media >= 80 and temp_media <= 112 and umd_media <= 0.13):
                        heat_index = heat_index - (3.25 - (0.25 * umd_media)) \
                            * ((17 - (abs(temp_media - 95))) / 17) ** 0.5
                    else:
                        if(temp_media >= 80 and temp_media <= 87 and umd_media > 0.85):
                            heat_index = heat_index + 0.02 * \
                                (umd_media - 85) * (87 - temp_media)
                            heat_index_list.append(heat_index)
                        else:
                            heat_index = heat_index
                            heat_index_list.append(heat_index)
            else:
                continue
        finalHI = 0.0
        finalHI = sum(heat_index_list)
        if(len(heat_index_list) > 0):
            finalHI = "{:.1f}".format(convertFtoC(finalHI / len(heat_index_list)))
            heat_index_list.append(data[0]["DC_NOME"])
            final_temp = "{:.1f}".format(convertFtoC(temp_media))
            return [data[0]["DC_NOME"], finalHI, final_temp]
        else:
            return 0

    def process(row):
        formatted_row = row["message_type"]
        clientSqs = boto3.client("sqs",region_name="us-east-1")
        if(formatted_row != None):
            data = json.loads(formatted_row)
            final_data = calculate_heat_index(data)
            URL = "https://sqs.us-east-1.amazonaws.com/687638469357/MyQueue"
            send = clientSqs.send_message(QueueUrl=URL,MessageBody=json.dumps(final_data))
        else:
            URL = "https://sqs.us-east-1.amazonaws.com/687638469357/MyQueue"
            send = clientSqs.send_message(QueueUrl=URL,MessageBody='bateu no none')
    kinesis\
        .selectExpr("CAST(data AS STRING)")\
        .select(from_json("data", schema).alias("data"))\
        .select("data.*")\
        .writeStream\
        .outputMode("append")\
        .foreach(process)\
        .trigger(processingTime="3600 seconds") \
        .start()\
        .awaitTermination()