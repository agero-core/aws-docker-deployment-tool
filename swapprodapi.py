import boto3
import json
import datetime
import os

#alb = boto3.client('elbv2')
#dynamo_client = boto3.client('dynamodb')
sts = boto3.client('sts')

### CROSSACCOUNT DYNAMO ACCESS TO SHARED ACCOUNT ###
stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']

dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
resource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
nonprod_table = resource.Table('ECS_Inventory_NonProduction')
prod_table = resource.Table('ECS_Inventory_Production')
trainda_table = resource.Table('ECS_Inventory_Training_DA')
#### ###


#CROSS ACCOUNT ALB ACCESS TO NONPROD ACCOUNT
stsrole_prod = os.environ['STSROLE_PROD']
response = sts.assume_role(RoleArn=stsrole_prod, RoleSessionName='crossAccountEcsTaskExecutionRole')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']

elbclient_prod = boto3.client('elbv2', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
sns_prod = boto3.client('sns', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
### ###


### RETURN BODY FOR API ###
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
### ###


###     SEND SNS NOTIFICATION   ###
def sendnotification(appname, prod1, prod2, prod_acc, version):

    if prod1 == 'green':
        env_name = appname + "-prod2"
    else:
        env_name = appname + "-prod1"
    
    sns_arn = "arn:aws:sns:us-east-1:" + prod_acc + ":ECSNotifications-" + env_name
    print sns_arn
    sns_message = "Updated Green Environment: " + env_name + "\n" + "Running Version: " + version 
    subject = "Swap on Application " + appname + " has been perfromed"
    response = sns_prod.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
    print response

####    ####


#   MODIFY LISTENER RULES FOR SWAP  #
def modifyrules(rule_arn_blue, targetgrp_arn_blue, rule_arn_green, targetgrp_arn_green):
    response_green = elbclient_prod.modify_rule(RuleArn=rule_arn_green, Actions=[{'Type': 'forward', 'TargetGroupArn': targetgrp_arn_blue}])
    print response_green
    response_blue = elbclient_prod.modify_rule(RuleArn=rule_arn_blue, Actions=[{'Type': 'forward', 'TargetGroupArn': targetgrp_arn_green}])
    print response_blue

#   RETRIEVE TASK DEFINITIONS FOR SWAPPING  #
def gettaskdefinition(appname):
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
        if priority == '1':
            hostheader_value = rule['Conditions'][0]['Values']
            print hostheader_value[0]
            rule_arn_green = rule_arn
            targetgrp_arn_green = rule['Actions'][0]['TargetGroupArn']
            print targetgrp_arn_green
            print

        if priority == '2':
            hostheader_value = rule['Conditions'][0]['Values']
            print hostheader_value[0]
            rule_arn_blue = rule_arn
            targetgrp_arn_blue = rule['Actions'][0]['TargetGroupArn']
            print targetgrp_arn_blue
            print

    modifyrules(rule_arn_blue, targetgrp_arn_blue, rule_arn_green, targetgrp_arn_green)


def updatelisteners(swap):
    listener_arn = str(swap['type1'][0])
    targetgrp_arn = str(swap['type2'][2])
    response = alb.modify_listener(ListenerArn = listener_arn, DefaultActions = [{'Type': 'forward', 'TargetGroupArn': targetgrp_arn}])

    listener_arn = str(swap['type2'][0])
    targetgrp_arn = str(swap['type1'][2])
    response = alb.modify_listener(ListenerArn = listener_arn, DefaultActions = [{'Type': 'forward', 'TargetGroupArn': targetgrp_arn}])


def recordswap(appname):

    dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD1'}}, AttributesToGet=['TechnicalTeam', 'Time', 'URL', 'Version'])
    print dynamo_response
    url = dynamo_response['Item']['URL']['S']
    techteam = dynamo_response['Item']['TechnicalTeam']['S']
    if 'prod-blue' in url:
        time_blue = dynamo_response['Item']['Time']['S']
        url_blue = url
        version = dynamo_response['Item']['Version']['S']
        prod1 = 'blue'
    else:
        time_green = dynamo_response['Item']['Time']['S']
        url_green = url
        #version_green = dynamo_response['Item']['Version']['S']
        prod1 = 'green'
        
    dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD2'}}, AttributesToGet=['TechnicalTeam', 'Time', 'URL', 'Version'])
    url = dynamo_response['Item']['URL']['S']
    techteam = dynamo_response['Item']['TechnicalTeam']['S']
    if 'prod-blue' in url:
        time_blue = dynamo_response['Item']['Time']['S']
        url_blue = url
        version = dynamo_response['Item']['Version']['S']
        prod2 = 'blue'
    else:
        time_green = dynamo_response['Item']['Time']['S']
        url_green = url
        #version_green = dynamo_response['Item']['Version']['S']
        prod2 = 'green'
    
    time = datetime.datetime.now()
    if prod1 == 'green':
        resp = dynamo_client.update_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD1'}}, AttributeUpdates={'URL':{'Value':{'S': url_blue}}, 'Time':{'Value':{'S': str(time)}}})
        print resp

        resp = dynamo_client.update_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD2'}}, AttributeUpdates={'URL':{'Value':{'S': url_green}}, 'Time':{'Value':{'S': str(time)}}})
        print resp

    else:
        resp = dynamo_client.update_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD2'}}, AttributeUpdates={'URL':{'Value':{'S': url_blue}}, 'Time':{'Value':{'S': str(time)}}})
        print resp

        resp = dynamo_client.update_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD1'}}, AttributeUpdates={'URL':{'Value':{'S': url_green}}, 'Time':{'Value':{'S': str(time)}}})
        print resp        

    return prod1, prod2, version


def lambda_handler(event, context):
    print event
    body = json.loads(event['body'])   
    prod_acc = os.environ['PROD_ACC']
 
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

    alb_name = appname + '-prod'
    swap = {}

    try:
        env = "PROD1"
        resp = table.query(KeyConditionExpression=Key('ApplicationName').eq(appname) & Key('Environment').eq(env))
        if resp['Count'] == 0:
            status_code = 409
            message = {"errorMessage": appname + " does not exist. You must create the Stack first"}
            return_message = return_body(status_code, message)
            return return_message
    except Exception as e:
        message = e

    message = "Starting Prod Blue/Green Swap for " + appname
    #time = datetime.datetime.now()
    #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'swapprod'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
    #print resp

    gettaskdefinition(appname)
    prod1, prod2, version = recordswap(appname)
    sendnotification(appname, prod1, prod2, prod_acc, version)

    message = "Prod Blue/Green Swap Completed Successfully for " + appname
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'swapprod'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        #print resp
    status_code = 200
    return_message = {"message": message}
    return_message = return_body(status_code, return_message)
    return return_message

