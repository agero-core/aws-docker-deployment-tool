import boto3
import json
import os

sns = boto3.client('sns')
sts = boto3.client('sts')

#CROSS ACCOUNT ECS ACCESS TO NONPROD ACCOUNT
stsrole_prod = os.environ['STSROLE_PROD']
resp = sts.assume_role(RoleArn=stsrole_prod, RoleSessionName='crossAccountEcsTaskExecutionRole')

aws_access_key_id_prod=resp['Credentials']['AccessKeyId']
aws_secret_access_key_prod=resp['Credentials']['SecretAccessKey']
aws_session_token_prod=resp['Credentials']['SessionToken']

sns_prod = boto3.client('sns', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod)


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

def create_subscription(sns, topic_arn, protocol, endpoint):
    response = sns.subscribe(TopicArn=topic_arn, Protocol=protocol, Endpoint=endpoint)
    print response


def lambda_handler(event, context):
    print event
    nonprod_acc = os.environ['NONPROD_ACC']
    prod_acc = os.environ['PROD_ACC']
    body = json.loads(event['body'])
    try:
        applicationName = body['applicationName']
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter applicationName is not present"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        protocol = body['protocol']
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter applicationName is not present"}
        return_message = return_body(status_code, message)
        return return_message

    protocol_list = ["http", "https", "email", "email-json", "sms", "sqs", "application", "lambda"]
    if protocol not in protocol_list:
        status_code = 400
        message = {"errorMessage": "Invalid Protocol"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        endpoint = body['endpoint']
        if endpoint == "":
            status_code = 400
            message = {"errorMessage": "Parameter endpoint cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message

    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter endpoint is not present"}
        return_message = return_body(status_code, message)
        return return_message


    try:
        environments = body['environments']
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter environments is not present"}
        return_message = return_body(status_code, message)
        return return_message

    if not environments:
        status_code = 400
        message = {"errorMessage": "Parameter environments cannot be empty"}
        return_message = return_body(status_code, message)
        return return_message
        
    x = ""
    for env in environments:
        env_name = applicationName + '-' + env.lower()
        if 'dev' in env.lower() or 'qa' in env.lower() or 'stage' in env.lower() or 'training' in env.lower() or 'da' in env.lower():
            topic_arn = "arn:aws:sns:us-east-1:" + nonprod_acc + ":ECSNotifications-" + env_name
            create_subscription(sns, topic_arn, protocol, endpoint)
            x = "success"

        elif 'prod' in env.lower():
            env_name = applicationName + "-prod1"
            topic_arn = "arn:aws:sns:us-east-1:" + prod_acc + ":ECSNotifications-" + env_name
            print topic_arn
            create_subscription(sns_prod, topic_arn, protocol, endpoint)
            env_name = applicationName + "-prod2"
            print topic_arn
            topic_arn = "arn:aws:sns:us-east-1:" + prod_acc + ":ECSNotifications-" + env_name
            print topic_arn
            create_subscription(sns_prod, topic_arn, protocol, endpoint)
            x = "success"

        else:
            status_code = 400
            message = {"errorMessage": "Parameter environments cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message


    if x == "success":
        status_code = 200
        message = {"message": "The Subscription has been added"}
        return_message = return_body(status_code, message)
        return return_message


