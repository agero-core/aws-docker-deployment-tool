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

def get_albarn(appname, env):
    alb_name = appname + '-' + env
    response = alb.describe_load_balancers(Names=[alb_name])
    alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    return alb_arn



def lambda_handler(event, context):
    body = json.loads(event['body'])
    print body

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

    try:
        environment = body['environment']
    except KeyError:
        status_code = 400
        message = {"errorMessage": "environment needs to be mentioned"}
        return {
                'statusCode': str(status_code),
                'body': json.dumps(message),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
                }    

    try:
        repo_uri = body['repouri']
        if repo_uri == "":
            status_code = 400
            message = {"errorMessage": "repouri cannot be empty"}
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
        message = {"errorMessage": "repouri needs to be mentioned"}
        return {
                'statusCode': str(status_code),
                'body': json.dumps(message),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
                }    

    try:
        version = body['version']
        if version == "":
            status_code = 400
            message = {"errorMessage": "version cannot be empty"}
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
        message = {"errorMessage": "version needs to be mentioned"}
        return {
                'statusCode': str(status_code),
                'body': json.dumps(message),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
                }

    vpc = os.environ['VPC']
    subnet1 = os.environ['SUBNET1']
    subnet2 = os.environ['SUBNET2']
    sg = os.environ['SG']

    for i in environment:
        env = i.upper()
        try:
            resp = table.query(KeyConditionExpression=Key('ApplicationName').eq(appname) & Key('Environment').eq(env))
            if resp['Count'] == 0:
                status_code = 409
                message = {'errorMessage': appname + " does not exist. You must create the Stack first"}
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
        
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': env}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']           
        print techteam 

        env = env.lower()

        message = "Deploying version " + version + " to " + appname + "-" + env
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        print resp

        #alb_arn = get_albarn(appname, env)
        create_taskdefinitions(appname, repo_uri, env)
        #targetgp_arn = create_targetgroups(appname, env, vpc)
        #add_listeners(alb_arn, targetgp_arn, env)
        update_service(appname, env, subnet1, subnet2, sg, techteam)

        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName': {'S': appname}, 'Environment': {'S': env.upper()}, 'TechnicalTeam': {'S': techteam}, 'Version': {'S': version}, 'Time': {'S': str(time)}})
        print resp    

    message = {"message" : "Deployed version " + version + " to " + appname}
    return {
        "statusCode": "200",
        "body" : json.dumps(message),
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }
        
