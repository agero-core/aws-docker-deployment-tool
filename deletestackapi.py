import boto3
import json
import datetime
import os

cf = boto3.client('cloudformation')
dynamo_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
ecs = boto3.client('ecs')
ecr = boto3.client('ecr')
sts = boto3.client('sts')
sns = boto3.client('sns')

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


###     RETURN BODY FOR API     ###
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
####     ####

###     DELETE ECR      ###
def delete_ecr(stackname):
    ecr_name = stackname.lower()
    resp = ecr.delete_repository(repositoryName=ecr_name, force=True)
####     ####


###     SEND SNS NOTIFICATION   ###
def sendnotification(stackname, nonprod_acc):
    env_list = ["dev", "qa", "stage"]
    for env in env_list:
        env_name = stackname + "-" + env
        sns_arn = "arn:aws:sns:us-east-1:" + nonprod_acc + ":ECSNotifications-" + env_name

        sns_message = "Deleting the Stack and all environments for " + stackname
        subject = "Deleting the Stack for the Application " + stackname
        response = sns.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
        print response


###     Main Handler    ###
def lambda_handler(event, context):

    print event
    body = json.loads(event['body'])

    nonprod_acc = os.environ['NONPROD_ACC']
    prod_acc = os.environ['PROD_ACC']
    region = os.environ['REGION']

    try:
        stackname = body['stack']
        if stackname == "":
            status_code = 400
            message = {"errorMessage": "Parameter Validation Error: stackname cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "Parameter Validation Error: stackname needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message


    try:
        delete_ecr(stackname)
    except Exception as e:
        print e
        pass 

    try:
        response = cf.delete_stack_instances(StackSetName=stackname, Accounts = [nonprod_acc, prod_acc], Regions=[region], RetainStacks=False)
        print response
        try:
            resp = nonprod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'DEV'})
        except Exception as e:
            print e
            pass
        try:
            resp = nonprod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'QA'})
        except Exception as e:
            print e
            pass
        try:
            resp = nonprod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'STAGE'})
        except Exception as e:
            print e
            pass
        try:
            resp = prod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'PROD1'})
        except Exception as e:
            print e
            pass
        try:
            resp = prod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'PROD2'})
        except Exception as e:
            print e
            pass
        try:
            resp = trainda_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'TRAINING'})
        except Exception as e:
            print e
            pass
        try:
            resp = trainda_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'DA'})
        except Exception as e:
            print e
            pass

        sendnotification(stackname, nonprod_acc)

        status_code = 200
        message = {'message': 'StackInstances Deletion Initiated', 'Warning': 'Please be aware to Remove StackSet been created in CloudFormation'}
        return_message = return_body(status_code, message)
        return return_message
    except Exception as e:
        print e
        status_code = 409
        message = {'message': 'Stack does not Exists'}
        return_message = return_body(status_code, message)
        return return_message

    """
    try:
        response = cf.delete_stack_set(StackSetName=stackname)
        print response
    except Exception as e:
        print e
        status_code = 409
        message = {'message': 'Stack does not Exists'}
        return_message = return_body(status_code, message)
        return return_message
    """
