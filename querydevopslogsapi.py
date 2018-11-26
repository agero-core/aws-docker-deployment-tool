import boto3
import json
import datetime
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    print event

    res_name = event['resourcename']
    starttime = event['starttime']
    endtime = event['endtime']

    dynamo_client = boto3.client('dynamodb')

    table_name = "DevOpsLogsTable"
    dynamo_client = boto3.resource('dynamodb')
    table = dynamo_client.Table(table_name)

    resp = table.query(KeyConditionExpression=Key("ResourceName").eq(res_name) & Key("Time").between(starttime, endtime))
    print resp
    return resp




