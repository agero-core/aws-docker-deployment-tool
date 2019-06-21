import boto3
import json
import os

sns = boto3.client('sns')

def sendnotification(appname, nonprod_acc, tag):
        env_name = appname
        sns_arn = "arn:aws:sns:us-east-1:" + nonprod_acc + ":ECSNotifications-" + env_name
        print sns_arn
        sns_message = "Image Version " + tag + " has been pushed to " + env_name
        subject = "New Image Pushed to " + env_name
        response = sns.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
        print response

def lambda_handler(event, context):
    print event
    
    eventname = event['detail']['eventName']
    ecrname = event['detail']['requestParameters']['repositoryName']
    nonprod_acc = os.environ['NONPROD_ACC']
    print eventname
    if eventname == "PutImage":
        print ecrname
        tag = event['detail']['requestParameters']['imageTag']
        sendnotification(ecrname, nonprod_acc, tag)
        
