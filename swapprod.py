import boto3
import json
import datetime

alb = boto3.client('elbv2')
dynamo_client = boto3.client('dynamodb')

def updatelisteners(swap):
    listener_arn = str(swap['type1'][0])
    targetgrp_arn = str(swap['type2'][2])
    response = alb.modify_listener(ListenerArn = listener_arn, DefaultActions = [{'Type': 'forward', 'TargetGroupArn': targetgrp_arn}])

    listener_arn = str(swap['type2'][0])
    targetgrp_arn = str(swap['type1'][2])
    response = alb.modify_listener(ListenerArn = listener_arn, DefaultActions = [{'Type': 'forward', 'TargetGroupArn': targetgrp_arn}])


def recordswap(appname):

    dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD-BLUE'}}, AttributesToGet=['TechnicalTeam', 'Time', 'Version'])
    techteam = dynamo_response['Item']['TechnicalTeam']['S']
    time_blue = dynamo_response['Item']['Time']['S']
    version_blue = dynamo_response['Item']['Version']['S']

    dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD-GREEN'}}, AttributesToGet=['TechnicalTeam', 'Time', 'Version'])
    techteam = dynamo_response['Item']['TechnicalTeam']['S']
    time_green = dynamo_response['Item']['Time']['S']
    version_green = dynamo_response['Item']['Version']['S']

    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD-GREEN'}, 'TechnicalTeam': {'S': techteam}, 'Version': {'S': version_blue}, 'Time': {'S': str(time)}})
    print resp

    resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD-BLUE'}, 'TechnicalTeam': {'S': techteam}, 'Version': {'S': version_green}, 'Time': {'S': str(time)}})
    print resp



def lambda_handler(event, context):
    print event
    body = json.loads(event['body'])   
 
    try:
        appname = body['applicationName']
        if appname == "":
            status_code = 400
            message = {"errorMessage": "applicationName cannot be empty"}
            return {
                'statusCode': str(status_code),
                'body': json.dumps(message),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
                }
    except KeyError:
        status_code = 400
        message = {"errorMessage": "applicationName needs to be mentioned"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    alb_name = appname + '-prod'
    swap = {}

    try:
        env = "PROD"
        resp = table.query(KeyConditionExpression=Key('ApplicationName').eq(appname) & Key('Environment').eq(env))
        if resp['Count'] == 0:
            status_code = 409
            message = {"errorMessage": appname + " does not exist. You must create the Stack first"}
            return {
                'statusCode': str(status_code),
                'body': json.dumps(message),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
                }
    except Exception as e:
        message = e


    message = "Starting Prod Blue/Green Swap for " + appname
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'swapprod'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
    print resp

    try:
        resp = alb.describe_load_balancers(Names=[alb_name])
        print resp
        alb_arn = resp['LoadBalancers'][0]['LoadBalancerArn']
        response = alb.describe_listeners(LoadBalancerArn=alb_arn)

        x = 0
        for listener in response['Listeners']:
                listeners = []
                x = x + 1
                listener_arn = listener['ListenerArn']
                port = listener['Port']
                for actions in listener['DefaultActions']:
                    if actions['Type'] == 'forward':
                        targetgrp_arn = actions['TargetGroupArn']
                        print listener_arn, port, targetgrp_arn
                    listeners.append(listener_arn)
                    listeners.append(port)
                    listeners.append(targetgrp_arn)
                print listeners
                if x == 1:
                    swap['type1'] = listeners
                if x == 2:
                    swap['type2'] = listeners
        print swap

        updatelisteners(swap)

        recordswap(appname)

        message = "Prod Blue/Green Swap Completed Successfully for " + appname
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'swapprod'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        print resp


    except Exception as e:
        print e

    status_code = 200
    return_message = {"message": message}
    return {
            'statusCode': str(status_code),
            'body': json.dumps(return_message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

