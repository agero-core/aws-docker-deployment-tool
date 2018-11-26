import boto3
import json
import datetime
import os

ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
dynamo_client = boto3.client('dynamodb')
resource = boto3.resource('dynamodb')
table = resource.Table('ECS_Inventory_NonProduction')


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


# CREATE TARGET GROUPS
def create_targetgroups(apiname, env, vpc):

    try:
        response = alb.create_target_group(
            Name=apiname + '-' + env,
            Protocol='HTTP',
            Port=80,
            VpcId=vpc,
            HealthCheckProtocol='HTTP',
            HealthCheckPort='80',
            HealthCheckPath='/health',
            HealthCheckIntervalSeconds=30,
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=3,
            Matcher={
                'HttpCode': '200'
            },
            TargetType='ip'
        )

        print response
        targetgp_arn = response['TargetGroups'][0]['TargetGroupArn']
        message = "Created Target Gtoup " + apiname + "-" + env + " with ARN: " + targetgp_arn
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

    return targetgp_arn

# ADD LISTENERS
def add_listeners(alb_arn, targetgp_arn, env):
    try:
        port = 80
        listener_response = alb.create_listener(
            LoadBalancerArn = alb_arn,
            Protocol = 'HTTP',
            Port = port,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': targetgp_arn,
                }
            ]
        )
        print listener_response
        message = "Listener Added"
        print message
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp

    except Exception as e:
        message = e
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp


# CREATING ECS SERVICE
def create_service(apiname, targetgp_arn, env, subnet1, subnet2, sg, techteam):
    try:
        ecs_resp = ecs_client.create_service(
            cluster=techteam,
            serviceName=apiname + '-' + env,
            taskDefinition=apiname + '-' + env,
            loadBalancers = [
                {
                    'targetGroupArn': targetgp_arn,
                    'containerName': apiname + '-' + env,
                    'containerPort': 80

                }
            ],
            desiredCount=1,
            launchType='FARGATE',
            schedulingStrategy='REPLICA',
            deploymentConfiguration={
                'maximumPercent': 100,
                'minimumHealthyPercent': 50
            },
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        subnet1,
                        subnet2
                    ],
                    'securityGroups': [
                        sg
                    ],
                    'assignPublicIp': 'DISABLED'
                }
            }
        )
        print ecs_resp
        message = "Adding Service " + apiname + '-' + env
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        print resp

    except Exception as e:
        message = e
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp

def get_albarn(appname, env):
    alb_name = appname + '-' + env
    response = alb.describe_load_balancers(Names=[alb_name])
    alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    return alb_arn



def lambda_handler(event, context):
    appname = event['application']
    environment = event['environment']
    repo_uri = event['repouri']

    vpc = os.environ['VPC']
    subnet1 = os.environ['SUBNET1']
    subnet2 = os.environ['SUBNET2']
    sg = os.environ['SG']

    environment = environment.split(',')
    for i in environment:
        env = i.upper()
        try:
            resp = table.query(KeyConditionExpression=Key('ApplicationName').eq(appname) & Key('Environment').eq(env))
            if resp['Count'] == 0:
                message = appname + " does not exist. You must create the Stack first"
                return {
                    "Status" : message
                }
        except Exception as e: 
            message = e
        
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': env}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']           
        print techteam 

        env = env.lower()

        message = "Deploying to " + appname + "-" + env
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        print resp

        alb_arn = get_albarn(appname, env)
        create_taskdefinitions(appname, repo_uri, env)
        targetgp_arn = create_targetgroups(appname, env, vpc)
        add_listeners(alb_arn, targetgp_arn, env)
        create_service(appname, targetgp_arn, env, subnet1, subnet2, sg, techteam)

    return {
        "Status" : "Deployed " + appname + "-" + env 
    }
        

    
