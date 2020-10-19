# PISIIV-BSI
Get data from INMET API to calculate the Heat Index from Pernambuco, using a serverless application with all features on aws cloud. Project to PISIIV course on BSI at UFRPE.

  # Project Info

## Technology 

All aws technologies used in this project was built in python.
The data Visualization in real-time it is available in ThingsBoard Platform

* python 3.8
* Lambda Function
* Kinesis Data Stream
* API Gateway
* Elastic MapReduce
* Spark stream 
* Simple Queue Service

<img height="700" src="https://github.com/caaiofarias/PISIIV-BSI/blob/main/logo.png">

## Getting started
  To run the project:
  This project was made to fire an event each day, using the [easy-cron](https://www.easycron.com). 
  To configure the project follow te steps below:
* Create Kinesis Stream
>    $ aws kinesis create-stream --stream-name stream-heat-index --shard-count 1
* To create lambda functions:
>    $ aws lambda create-function --function-name <choosen-name> --runtime "python3.8" --role "arn:aws:iam::625297745038:role/<role>" 
      --handler "lambda_function.handler" 
      --timeout 10
      --memory-size 128 
      --zip-file "fileb://function.zip"
* Create a zip file with external dependencies (pip):
>    $ pip3 install --target ./package <NAME OF PACKAGE> \
>    $ cd package/ \
>    $ sudo zip -r9 ${OLDPWD}/function.zip . \
>    $ cd .. \
>    $ sudo zip -g function.zip lambda_function.py \
* Update function on lambda:
>    $  aws lambda update-function-code --function-name <FUNCTION NAME> --zip-file fileb://function.zip
* Deploying rest api with api gateway:
>    $ aws apigateway create-deployment --region <Your Region> --rest-api-id <YOUR API GATEWAY ID> --stage-name <prod || beta || alpha>
  - to deploy tou need first to create an api gateway on console aws
 
* Create SQS Queue:
>    $ aws sqs create-queue --queue-name <<queue-name>> --attributes VisibilityTimeout=900
* Create EMR Cluster with spark installed, 3 nodes (one core, two workers), using QuBole jar to connect kinesis on Spark Structured Stream, a bootstrap action \
  to install boto3 library on all nodes, and passing on args the AppName, S3-Path-to-process-data-on-spark, kinesis stream name:
>    $ aws emr create-cluster --applications Name=Spark Name=Zeppelin --ec2-attributes \
       '{"KeyName":"kinesisPair","InstanceProfile":"EMR_EC2_DefaultRole","SubnetId":"subnet-c5ae1a9a","EmrManagedSlaveSecurityGroup":"sg-018c9d950307c7ae5","EmrManagedMasterSecurityGroup":"sg-05b16b8a6a349ab38"}' \
        --release-label emr-5.31.0 \
        --log-uri 's3n://aws-logs-687638469357-us-east-1/elasticmapreduce/' \ 
        --instance-groups '[{"InstanceCount":1,"EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"SizeInGB":32,"VolumeType":"gp2"},"VolumesPerInstance":2}]},"InstanceGroupType":"MASTER","InstanceType":"m5.xlarge","Name":"Master Instance Group"},\
        {"InstanceCount":2,"EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"SizeInGB":32,"VolumeType":"gp2"},"VolumesPerInstance":2}]},"InstanceGroupType":"CORE","InstanceType":"m5.xlarge","Name":"Core Instance Group"}]' \
        --bootstrap-actions '[{"Path":"s3pathtoscriptinstall-boto3.sh","Args":["instance.isMaster=true","echo","Running","on","master","node"],"Name":"Ação personalizada"}]' \
        --ebs-root-volume-size 10 \
        --service-role EMR_DefaultRole \
        --enable-debugging \
        --name 'Meu cluster' \
        --scale-down-behavior TERMINATE_AT_TASK_COMPLETION \
        --region us-east-1
* Add Step on EMR Cluster:
>   $ aws emr add-steps --cluster-id <ID-CREATED-CLUSTER> \
    --steps Type=Spark,Name="Kinesis-SQL",ActionOnFailure=CONTINUE,\
    Args=[--jars,PATHTOQUBOLEJAR,\ 
    PATH-TO-S3-SCRIPT-PROCESS-DATA,\
    kinesis-stream-name,\
    kinesis-stream-name,\
   kineis-url,\
   region]
* SSH on Core node:
>   $ aws emr ssh --cluster-id ID DO CLUSTER --key-pair-file ~/<file.pem>

## Links

  - Link to show data visualized on thingsBoard: (https://demo.thingsboard.io/dashboards/8834ba40-1168-11eb-af98-19366df12767)
  
## Versioning

1.0.0.0


## Authors

* **Caio Farias Cavalcanti**: @caaiofarias (https://github.com/caaiofarias)


Please follow github and join us!
Thanks to visiting me and good coding!
