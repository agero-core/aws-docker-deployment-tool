import boto3
import json
import time
import os

cf = boto3.client('cloudformation')
sns = boto3.client('sns')
waiter = cf.get_waiter('stack_create_complete')


def sendnotification(appname, nonprod_acc, message):
        env_name = appname.lower()
        sns_arn = "arn:aws:sns:us-east-1:" + nonprod_acc + ":ECSNotifications-" + env_name
        print sns_arn
        sns_message = message
        subject = "CloudFormation StackSet Completed"
        response = sns.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
        print response


def lambda_handler(event, context):
    # TODO implement
    print context
    print event
    
    nonprod_acc = os.environ['NONPROD_ACC']
    
    eventName = event['detail']['eventName']
    if eventName == 'CreateStackSet':
        stackSetName = event['detail']['requestParameters']['stackSetName']
        stackSetId = event['detail']['responseElements']['stackSetId']
        print stackSetId
        print "StackSet is being Created for " + stackSetName
    if eventName == 'DeleteStackSet':
        stackSetName = event['detail']['requestParameters']['stackSetName']
        stackSetId = event['detail']['responseElements']['stackSetId']
        print stackSetId        
        print "StackSet is being Deleted for " + stackSetName
        
    if eventName == 'CreateStackInstances':
        stackSetName = event['detail']['requestParameters']['stackSetName']
        operationId = event['detail']['responseElements']['operationId']
        response = cf.describe_stack_set_operation(StackSetName=stackSetName, OperationId=operationId)
        status = response['StackSetOperation']['Status']
        while status == 'RUNNING':
            time.sleep(10)
            response = cf.describe_stack_set_operation(StackSetName=stackSetName, OperationId=operationId)
            status = response['StackSetOperation']['Status']
        
        if status == 'SUCCEEDED':
            dev_endpoint = "https://" + stackSetName + ".dkr.dev.dot-nonprod.corppvt.cloud"
            qa_endpoint = "https://" + stackSetName + ".dkr.qa.dot-nonprod.corppvt.cloud"
            stage_endpoint = "https://" + stackSetName + ".dkr.stage.dot-nonprod.corppvt.cloud"
            prodblue_endpoint = "https://" + stackSetName + ".dkr.prod-blue.dot-nonprod.corppvt.cloud"
            prod_endpoint = "https://" + stackSetName + ".dkr.prod.dot-nonprod.corppvt.cloud"
            message = "StackSet Creation for Application " + stackSetName + " completed successfully \n Application Name: " + stackSetNamae + "\n ECR Name: " + stackSetName.lower() + "\n DEV Endpoint: " + dev_endpoint + "\n QA Endpoint: " + qa_endpoint + "\n STAGE Endpoint: " + stage_endpoint + "\n PROD_BLUE Endpoint: " + prodblue_endpoint + "\n PROD Endpoint: " + prod_endpoint
            print message
            sendnotification(stackSetName, nonprod_acc, message)
        elif status == 'FAILED':
            message = "StackSet Creation for Application " + stackSetName + " Failed"
            print message
        else:
            message = "StackSet Creation for Application " + stackSetName + " is been Stopped"
            print message

