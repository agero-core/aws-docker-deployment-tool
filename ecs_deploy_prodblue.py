import boto3
import json
import datetime
import os

ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
dynamo_client = boto3.client('dynamodb')
resource = boto3.resource('dynamodb')
table = resource.Table('ECS_Inventory_Production')


def getstageenv_image(appname):
    taskdef = appname + '-stage'
    response = ecs_client.describe_task_definition(taskDefinition=taskdef)
    image_uri = response['taskDefinition']['containerDefinitions'][0]['image']
    print image_uri
    return image_uri

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
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp

    except Exception as e:
        message = e
        print message
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp


# CREATING ECS SERVICE
def update_service(apiname, env, subnet1, subnet2, sg, techteam):
    try:
        ecs_resp = ecs_client.update_service(
            cluster=techteam,
            service=apiname + '-' + env,
            taskDefinition=apiname + '-' + env,
            desiredCount=1,
            healthCheckGracePeriodSeconds=30
        )
        print ecs_resp
        message = "Updating Service " + apiname + '-' + env + ' for new taskDefinition '
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        print resp

    except Exception as e:
        message = e
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp



def lambda_handler(event, context):
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

    dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'STAGE'}}, AttributesToGet=['TechnicalTeam', 'Version'])
    techteam = dynamo_response['Item']['TechnicalTeam']['S']
    version = dynamo_response['Item']['Version']['S']

    vpc = os.environ['VPC']
    subnet1 = os.environ['SUBNET1']
    subnet2 = os.environ['SUBNET2']
    sg = os.environ['SG']
    
    repo_uri = getstageenv_image(appname)
    env = 'prod-blue'
    create_taskdefinitions(appname, repo_uri, env)
    update_service(appname, env, subnet1, subnet2, sg, techteam)

    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName': {'S': appname}, 'Environment': {'S': env.upper()}, 'TechnicalTeam': {'S': techteam}, 'Version': {'S': version}, 'Time': {'S': str(time)}})
    print resp

    status_code = 200
    message = {'message': "Deployed version " + version + " to " + appname + " in ProdBlue Environment"}
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }

    
        
