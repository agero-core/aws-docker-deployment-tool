import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import datetime
import os

ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
sns = boto3.client('sns')
ecr = boto3.client('ecr')
sts = boto3.client('sts')

stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']


dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
resource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
table = resource.Table('ECS_Inventory_NonProduction')


#    RETURN BODY FOR API     #
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

###     SEND SNS NOTIFICATION   ###
def sendnotification(appname, env, nonprod_acc, version):
        env_name = appname + "-" + env
        sns_arn = "arn:aws:sns:us-east-1:" + nonprod_acc + ":ECSNotifications-" + env_name
        print sns_arn
        sns_message = "New Version " + version + " is getting deployed to environment " + env_name
        subject = "Deploying Version " + version + " to Environment " + env_name
        response = sns.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
        print response

###     VERIFY REPO URI     ###
def verifyrepouri(appname, tag):
    response = ecr.batch_get_image(repositoryName = appname.lower(), imageIds = [{'imageTag':tag}])
    print json.dumps(response, indent=4, sort_keys=True)

    if not response['failures']:
        print "Image Present"
        result = 0
    else:
        print "Image does not exists"
        print response['failures'][0]
        result = 1
    
    return result


#   CREATING ECS TASK DEFINITION
def create_taskdefinitions(apiname, repo_uri, env):

    try:
        container = {
            'name': apiname + '-' + env,
            'environment': [
                {
                    'name': 'ASPNETCORE_ENVIRONMENT',
                    'value': env
                }
            ],
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
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp

    except Exception as e:
        error_message = e
        status_code = 400
        message = {"errorMessage": str(error_message)}
        return_message = return_body(status_code, message)
        return return_message        
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp


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
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp

    except Exception as e:
        message = e
        print message
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp

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
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp

    except Exception as e:
        message = e
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp


# CREATING ECS SERVICE
def update_service(apiname, env, techteam):
    try:
        ecs_resp = ecs_client.update_service(
            cluster=apiname,
            service=apiname + '-' + env,
            taskDefinition=apiname + '-' + env,
            desiredCount=1,
            healthCheckGracePeriodSeconds=30
        )
        print ecs_resp
        message = "Updating Service " + apiname + '-' + env + ' for new taskDefinition '
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        #print resp

    except Exception as e:
        message = e
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp

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
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "applicationName needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        environment = body['environment']
    except KeyError:
        status_code = 400
        message = {"errorMessage": "environment needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        tag = body['imageTag']
        if tag == "":
            status_code = 400
            message = {"errorMessage": "imageTag cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "imageTag needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    version = tag

    devqa_vpc = os.environ['DEVQA_VPC']
    stage_vpc = os.environ['STAGE_VPC']
    training_vpc = os.environ['TRAINING_VPC']
    da_vpc = os.environ['DA_VPC']
    devqa_subnet = os.environ['DEVQA_SUBNET']
    stage_subnet = os.environ['STAGE_SUBNET']
    training_subnet = os.environ['TRAINING_SUBNET']
    da_subnet = os.environ['DA_SUBNET']
    devqa_sg = os.environ['DEVQA_SG']
    stage_sg = os.environ['STAGE_SG']
    training_sg = os.environ['TRAINING_SG']
    da_sg = os.environ['DA_SG']
    nonprod_acc = os.environ['NONPROD_ACC']
    repo_uri = nonprod_acc + ".dkr.ecr.us-east-1.amazonaws.com/" + appname.lower() + ":" + tag


    for i in environment:
        env = i.upper()
        try:
            resp = table.query(KeyConditionExpression=Key('ApplicationName').eq(appname) & Key('Environment').eq(env))
            print resp
            if resp['Count'] == 0:
                status_code = 409
                message = {'errorMessage': appname + " does not exist. You must create the Stack first"}
                return_message = return_body(status_code, message)
                return return_message
        
        except Exception as e:
            print e
            status_code = 409
            message = {'errorMessage': appname + " does not exist. You must create the Stack first"}
            return_message = return_body(status_code, message)
            return return_message
       
 
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': env}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']           
        print techteam 

        env = env.lower()

        message = "Deploying version " + version + " to " + appname + "-" + env
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        #print resp

        result = verifyrepouri(appname, tag)
        if result == 1:
            status_code = 404
            message = {"errorMessage": "Invalid imageTag"}
            return_message = return_body(status_code, message)
            return return_message
            
        create_taskdefinitions(appname, repo_uri, env)
        update_service(appname, env, techteam)

        time = datetime.datetime.now()
        resp = dynamo_client.update_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': env.upper()}}, AttributeUpdates={'Version':{'Value':{'S': version}}, 'Time':{'Value':{'S': str(time)}}})
        print resp    

        sendnotification(appname, env, nonprod_acc, version)

    message = {"message" : "Deployed version " + version + " to " + appname}
    return {
        "statusCode": "200",
        "body" : json.dumps(message),
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }
        
