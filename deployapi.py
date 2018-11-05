import boto3
import json
import requests
import datetime

ecr_client = boto3.client('ecr')
dynamo_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    print event    

    try:
        record = event["Records"][0]
    except KeyError:
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': "KeyError while parsing event[Records][0]"}})
        print resp


    try:
        package = record["s3"]["object"]["key"]
        print package
        message = package + " Retrieved"
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
    except KeyError:
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': "KeyError while parsing record[s3][object][key]"}})

    try:
        message = "Creating Repository with package " + package  
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        ecr_repo = package.replace(".zip","")
        ecr_repo = ecr_repo.lower()
        print ecr_repo
        response = ecr_client.create_repository(repositoryName='string')
        print response

        message = "Pushing "  + ecr_repo + " to ECR"
        print "Pushing " + ecr_repo + " to ECR"
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}}) 
    except:
        message = "Error Creating/Pushing the Image to ECR"
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})


