import boto3
import json
import datetime
import os

ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
sts = boto3.client('sts')
sns = boto3.client('sns')

#CROSSACCOUNT DYNAMO ACCESS TO SHARED ACCOUNT
stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']

dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
resource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
table = resource.Table('ECS_Inventory_TrainingDA')


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


def getstageenv_image(appname, task_env):
    taskdef = appname + '-' + task_env
    response = ecs_client.describe_task_definition(taskDefinition=taskdef)
    image_uri = response['taskDefinition']['containerDefinitions'][0]['image']
    print image_uri
    return image_uri


###     SEND SNS NOTIFICATION   ###
def sendnotification(appname, env, prod_acc, version):

        env_name = appname + "-" + env
        sns_arn = "arn:aws:sns:us-east-1:" + prod_acc + ":ECSNotifications-" + env_name

        sns_message = "New Version " + version + " is getting deployed to Blue Environment " + env_name
        subject = "Deploying Version " + version + " to Environment " + env_name
        response = sns.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
        print response


# CREATING ECS TASK DEFINITION
def create_taskdefinitions(apiname, repo_uri, env):

    try:
        container = {
            'name': apiname + '-' + env,
            'image': repo_uri,
            'portMappings': [
                {
                    "containerPort": 80,
                    "hostPort": 80,
                    "protocol": "tcp"
                }
            ],
            'essential': True
        }

        resp = ecs_client.register_task_definition(
            family = apiname + '-' + env,
            taskRoleArn = 'ecsTaskExecutionRole',
            executionRoleArn = 'ecsTaskExecutionRole',
            networkMode = 'awsvpc',
            containerDefinitions=[container],
            requiresCompatibilities=['FARGATE'],
            cpu= "256",
            memory= "512"
        )
        print resp

        message = "Created Task Definiton " + apiname + '-' + env
        print message

    except Exception as e:
        message = e
        print message


# CREATING ECS SERVICE
def update_service(apiname, env, techteam):
    try:
        ecs_resp = ecs_client.update_service(
            cluster=apiname,
            service=apiname + '-' + env,
            taskDefinition=apiname + '-' + env,
            desiredCount=2,
            forceNewDeployment=True,
            healthCheckGracePeriodSeconds=30
        )
        print ecs_resp

    except Exception as e:
        message = e
        print message

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

    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'STAGE'}}, AttributesToGet=['TechnicalTeam', 'Version'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        version = dynamo_response['Item']['Version']['S']
        task_env = 'stage'
    except Exception as e:
        try:
            dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'QA'}}, AttributesToGet=['TechnicalTeam', 'Version'])
            techteam = dynamo_response['Item']['TechnicalTeam']['S']
            version = dynamo_response['Item']['Version']['S']
            task_env = 'qa'
        except Exception as e:
            try:
                dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'DEV'}}, AttributesToGet=['TechnicalTeam', 'Version'])
                techteam = dynamo_response['Item']['TechnicalTeam']['S']
                version = dynamo_response['Item']['Version']['S']
                task_env = 'dev'
            except Exception as e:
                print e
                status_code = 409
                message = {'errorMessage': appname + " does not exist. You must create the Stack first"}
                return_message = return_body(status_code, message)
                return return_message


    devqa_vpc = os.environ['DEVQA_VPC']
    devqa_subnet = os.environ['DEVQA_SUBNET']
    devqa_sg = os.environ['DEVQA_SG']
    nonprod_acc = os.environ['NONPROD_ACC']

    repo_uri = getstageenv_image(appname, task_env)
    env = ["training", "da"]
    for eachenv in env:
        create_taskdefinitions(appname, repo_uri, eachenv)
        update_service(appname, eachenv, techteam)
        sendnotification(appname, eachenv, nonprod_acc, version)

        time = datetime.datetime.now()
        resp = dynamo_client.update_item(TableName="ECS_Inventory_TrainingDA", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': eachenv.upper()}}, AttributeUpdates={'Version':{'Value':{'S': version}}, 'Time':{'Value':{'S': str(time)}}})
    print resp

    status_code = 200
    message = {'message': "Deployed version " + version + " to " + appname + " in Training and DA Environment"}
    return_message = return_body(status_code, message)
    return return_message

