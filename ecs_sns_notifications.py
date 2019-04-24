import boto3
import json
import os

sns = boto3.client('sns')

def sendnotifications(env_name, taskdef, nonprod_acc):
    sns_arn = "arn:aws:sns:us-east-1:" + nonprod_acc + ":" + env_name
    sns_message = "New Version Deployed to environment " + env_name + " with new Task Definition version " + taskdef
    subject = "Deployed Latest Version to Environment " + env_name
    response = sns.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
    print response
    
def lambda_handler(event, context):
    print event
    
    detail_type = event['detail-type']
    group = event['detail']['group']
    last_status = event['detail']['lastStatus']
    nonprod_acc = os.environ['NONPROD_ACC']
    
    if last_status == "RUNNING":
        try:
            update = event['detail']['stopCode']
        except:
            taskdefarn = event['detail']['taskDefinitionArn']
            taskdef = taskdefarn.partition('/')[2]
            print taskdef
            env_name = taskdef.partition(':')[0]
            print env_name
            sendnotifications(env_name, taskdef, nonprod_acc)
