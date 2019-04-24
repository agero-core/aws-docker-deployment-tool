import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import os


ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
sns = boto3.client('sns')
ecr = boto3.client('ecr')
sts = boto3.client('sts')


#CROSSACCOUNT DYNAMO ACCESS TO SHARED ACCOUNT
stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']

dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
resource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
table = resource.Table('ECS_Inventory_Production')


#CROSS ACCOUNT ECS ACCESS TO NONPROD ACCOUNT
stsrole_prod = os.environ['STSROLE_PROD']
resp = sts.assume_role(RoleArn=stsrole_prod, RoleSessionName='crossAccountEcsTaskExecutionRole')

aws_access_key_id_prod=resp['Credentials']['AccessKeyId']
aws_secret_access_key_prod=resp['Credentials']['SecretAccessKey']
aws_session_token_prod=resp['Credentials']['SessionToken']

ecsclient_prod = boto3.client('ecs', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod)
elbclient_prod = boto3.client('elbv2', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod)
sns_prod = boto3.client('sns', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod)


###     GET PROD BLUE ENVIRONMENT NAME   ###
def getprodblueEnv(appname):
    albname = appname + '-prod'
    resp = elbclient_prod.describe_load_balancers(Names=[albname])
    alb_arn = resp['LoadBalancers'][0]['LoadBalancerArn']
    response = elbclient_prod.describe_listeners(LoadBalancerArn=alb_arn)
    listener_arn = response['Listeners'][0]['ListenerArn']
    res = elbclient_prod.describe_rules(ListenerArn=listener_arn)
    for rule in res['Rules']:
        rule_arn = rule['RuleArn']
        print rule_arn
        priority = rule['Priority']
        if priority == '2':
            hostheader_value = rule['Conditions'][0]['Values']
            print hostheader_value[0]
            rule_arn_blue = rule_arn
            targetgrp_arn_blue = rule['Actions'][0]['TargetGroupArn']
            print targetgrp_arn_blue

    if 'prod1' in targetgrp_arn_blue:
        env = "prod1"
    else:
        env = "prod2"

    return env


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
        count = 2
        

    try:        
        response = ecsclient_prod.update_service(
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

    environment = getprodblueEnv(appname)
    print "Prod Blue " + environment

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

