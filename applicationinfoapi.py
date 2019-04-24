import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import os

sts = boto3.client('sts')


#CROSSACCOUNT DYNAMO ACCESS TO SHARED ACCOUNT
stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']

dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
resource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
table = resource.Table('ECS_Inventory_NonProduction')


#RETURN BODY FOR API
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

def getitem(appname, table, env_list):
    message = []
    for env in env_list:
        info = {}
        info['applicationName'] = appname
        info['environment'] = env
        try:
            dynamo_response = dynamo_client.get_item(TableName=table,
                                                 Key={'ApplicationName': {'S': appname}, 'Environment': {'S': env}},
                                                 AttributesToGet=['TechnicalTeam', 'URL', 'Version', 'Time'])
            info['techTeam'] = dynamo_response['Item']['TechnicalTeam']['S']
            info['version'] = dynamo_response['Item']['Version']['S']
            info['url'] = dynamo_response['Item']['URL']['S']
            info['time'] = dynamo_response['Item']['Time']['S']
            message.append(info)
        except Exception as e:
            pass

    return message 


def lambda_handler(event, context):
    body = json.loads(event['body'])

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


    table = "ECS_Inventory_NonProduction"
    env_list = ["DEV", "QA", "STAGE"]
    nonprod_message = getitem(appname, table, env_list)

    table = "ECS_Inventory_Production"
    env_list = ["PROD1", "PROD2"]
    prod_message = getitem(appname, table, env_list)

    table = "ECS_Inventory_TrainingDA"
    env_list = ["TRAINING", "DA"]
    trainingda_message = getitem(appname, table, env_list)

    message = nonprod_message + prod_message + trainingda_message
    print json.dumps(message, indent=4, sort_keys=True)

    status_code = 200
    return_message = return_body(status_code, message)
    return return_message

