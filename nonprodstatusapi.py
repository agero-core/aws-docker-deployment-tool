import boto3
from boto3.dynamodb.conditions import Key, Attr
import json


ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
sns = boto3.client('sns')
ecr = boto3.client('ecr')
sts = boto3.client('sts')


###    RETURN BODY FOR API     ###
def return_body(status_code, message):
    body = {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }
    return body


###     Update Task Count   ###
def serviceupdate(appname, environment, action):
    cluster = appname
    service = appname + '-' + environment
    if action.lower() == "stop":
        count = 0
    if action.lower() == "start":
        count = 1
        

    try:        
        response = ecs_client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=count
        )
        print response
        msg = "success"
    except Exception as e:
        print e
        msg = "error"
        
    return msg
    

def lambda_handler(event, context):
    body = json.loads(event['body'])
    print body

    try:
        appname = body['applicationName']
        if appname == "":
            status_code = 400
            message = {"errorMessage": "applicationName cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "applicationName needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        environment = body['environment']
        if environment == "":
            status_code = 400
            message = {"errorMessage": "environment cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "environment needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        action = body['action']
        if action == "":
            status_code = 400
            message = {"errorMessage": "action cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "action needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    msg = serviceupdate(appname, environment, action)
    if msg == "success":
        status_code = 200
        if action.lower() == "start":
            message = {"message": "Environment " + appname + "-" + environment + " for Application " + appname + " is been Started"}
        if action.lower() == "stop":
            message = {"message": "Environment " + appname + "-" + environment + " for Application " + appname + " is been Stopped"}

    if msg == "error":
        status_code = 404
        message = {"errorMessage": "The Cluster " + appname + "-" + environment + " for Application " + appname + " does not exists"}

        
    return_message = return_body(status_code, message)
    return return_message
