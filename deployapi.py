import boto3
import datetime
import json
import os

ecr_client = boto3.client('ecr')
ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
dynamo_client = boto3.client('dynamodb')

# CREATING ECS TASK DEFINITION
def create_taskdefinitions(apiname, repo_uri, prod_type):

    try:
        container = {
            'name': apiname + '-' + prod_type,
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
            family = apiname,
            taskRoleArn = 'ecsTaskExecutionRole',
            executionRoleArn = 'ecsTaskExecutionRole',
            networkMode = 'awsvpc',
            containerDefinitions=[container],
            requiresCompatibilities=['FARGATE'],
            cpu= "256",
            memory= "512"
        )
        print resp
        message = "Created Task Definiton " + apiname + '-' + prod_type
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


# CREATING APPLICATION LOAD BALANCER
def create_albs(apiname, alb_subnet1, alb_subnet2, alb_sg):

    try:
        alb_resp = alb.create_load_balancer(
            Name = apiname,
            Subnets = [
                alb_subnet1,
                alb_subnet2
            ],
            SecurityGroups=[
                alb_sg
            ],
            Scheme='internal',
            Tags=[
                {
                    'Key': 'Name',
                    'Value': apiname
                }
            ],
            Type='application',
            IpAddressType='ipv4'
        )

        print alb_resp
        alb_arn = alb_resp['LoadBalancers'][0]['LoadBalancerArn']
        message = "Created ALB " + apiname + " with ARN: " + alb_arn
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

    return alb_arn



# CREATE TARGET GROUPS
def create_targetgroups(apiname, prod_type, vpc):

    try:
        response = alb.create_target_group(
            Name=apiname + '-' + prod_type,
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
        message = "Created Target Gtoup " + apiname+ "-" + prod_type + " with ARN: " + targetgp_arn
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
def add_listeners(alb_arn, targetgp_arn, prod_type):
    try:
        if 'green' in prod_type:
            port = 80
        else:
            port = 8080
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
def create_service(apiname, targetgp_arn, prod_type, subnet1, subnet2, sg):
    try:
        ecs_resp = ecs_client.create_service(
            cluster='default',
            serviceName=apiname + '-' + prod_type,
            taskDefinition=apiname,
            loadBalancers = [
                {
                    'targetGroupArn': targetgp_arn,
                    'containerName': apiname + '-' + prod_type,
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
        message = "Adding Service " + apiname + '-' + prod_type
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        print resp

    except Exception as e:
        message = e
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp


def lambda_handler(event, context):
    print event

    try:
        record = event["Records"][0]
    except KeyError:
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        print resp


    try:
        package = record["s3"]["object"]["key"]
        print package
        message = package + " Retrieved"
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
    except KeyError:
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})


    apiname = package.replace(".zip","")
    apiname = apiname.replace("_", "-")
    apiname = apiname.lower()
    repo_uri = os.environ['REPO_URI']
    vpc = os.environ['VPC']
    subnet1 = os.environ['SUBNET1']
    subnet2 = os.environ['SUBNET2']
    sg = os.environ['SG']
    alb_subnet1 = os.environ['ALB_SUBNET1']
    alb_subnet2 = os.environ['ALB_SUBNET2']
    alb_sg = os.environ['ALB_SG']

    #CREATE ALB
    alb_arn = create_albs(apiname, alb_subnet1, alb_subnet2, alb_sg)

    #BLUE DEPLOYMENT
    message = "Deploying " + apiname + " to BLUE"
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
    print resp
    prod_type = 'prod-blue'
    create_taskdefinitions(apiname, repo_uri, prod_type)
    targetgp_arn = create_targetgroups(apiname, prod_type, vpc)
    add_listeners(alb_arn, targetgp_arn, prod_type)
    create_service(apiname, targetgp_arn, prod_type, subnet1, subnet2, sg)

    #GREEN DEPLOYMENT
    prod_type = 'prod-green'
    message = "Deploying " + apiname + " to GREEN"
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
    print resp
    create_taskdefinitions(apiname, repo_uri, prod_type)
    targetgp_arn = create_targetgroups(apiname, prod_type, vpc)
    add_listeners(alb_arn, targetgp_arn, prod_type)
    create_service(apiname, targetgp_arn, prod_type, subnet1, subnet2, sg)



# CREATING ECS REPOSITORY
# response = ecr_client.create_repository(repositoryName=apiname)
# print response
# repo_uri = response['repository']['repositoryUri']

