import boto3
import json
import datetime
import os

ecs_client = boto3.client('ecs')
alb = boto3.client('elbv2')
sts = boto3.client('sts')

#CROSSACCOUNT DYNAMO ACCESS TO SHARED ACCOUNT
stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']


dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
resource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
table = resource.Table('ECS_Inventory_Production')

#CROSS ACCOUNT ECS ACCESS TO NONPROD ACCOUNT
stsrole_prod = os.environ['STSROLE_PROD']
resp = sts.assume_role(RoleArn=stsrole_prod, RoleSessionName='crossAccountEcsTaskExecutionRole')

aws_access_key_id_prod=resp['Credentials']['AccessKeyId']
aws_secret_access_key_prod=resp['Credentials']['SecretAccessKey']
aws_session_token_prod=resp['Credentials']['SessionToken']

ecsclient_prod = boto3.client('ecs', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod,region_name='us-west-2')
elbclient_prod = boto3.client('elbv2', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod,region_name='us-west-2')
sns_prod = boto3.client('sns', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod,region_name='us-west-2')
#CROSS ACCOUNT ALB ACCESS TO NONPROD ACCOUNT
#alb_stsrole_prod = os.environ['ALB_STSROLE_PROD']
#resp = sts.assume_role(RoleArn=alb_stsrole_prod, RoleSessionName='crossAccountEcsTaskExecutionRole')

#aws_access_key_id_prod=resp['Credentials']['AccessKeyId']
#aws_secret_access_key_prod=resp['Credentials']['SecretAccessKey']
#aws_session_token_prod=resp['Credentials']['SessionToken']

#elbclient_prod = boto3.client('elbv2', aws_access_key_id=aws_access_key_id_prod,aws_secret_access_key=aws_secret_access_key_prod,aws_session_token=aws_session_token_prod)


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
    response = ecsclient_prod.describe_task_definition(taskDefinition=taskdef)
    image_uri = response['taskDefinition']['containerDefinitions'][0]['image']
    print image_uri
    return image_uri


#   GET PROD ENVIRONMENT NAME   #
def getprodblueEnv(appname):
    albname = appname + '-prod'
    resp = elbclient_prod.describe_load_balancers(Names=[albname])
    alb_arn = resp['LoadBalancers'][0]['LoadBalancerArn']
    response = elbclient_prod.describe_listeners(LoadBalancerArn=alb_arn)
    listener_arn = response['Listeners'][0]['ListenerArn']
    res = elbclient_prod.describe_rules(ListenerArn=listener_arn)
    for rule in res['Rules']:
        rule_arn = rule['RuleArn']
        print rule_arn
        priority = rule['Priority']
        if priority == '2':
            hostheader_value = rule['Conditions'][0]['Values']
            print hostheader_value[0]
            rule_arn_blue = rule_arn
            targetgrp_arn_blue = rule['Actions'][0]['TargetGroupArn']
            print targetgrp_arn_blue

    if 'prod1' in targetgrp_arn_blue:
        env = "prod1"
    else:
        env = "prod2"

    return env


###     SEND SNS NOTIFICATION   ###
def sendnotification(appname, env, prod_acc, version):

        env_name = appname + "-" + env
        sns_arn = "arn:aws:sns:us-west-2:" + prod_acc + ":ECSNotifications-" + env_name

        sns_message = "New Version " + version + " is getting deployed to Blue Environment " + env_name + " in West Region"
        subject = "Deploying Version " + version + " to Environment " + env_name + " in West Region"
        response = sns_prod.publish(TopicArn=sns_arn, Message=sns_message, Subject=subject)
        print response


# CREATING ECS TASK DEFINITION
def create_taskdefinitions(apiname, repo_uri, env):

    try:
        container = {
            'name': apiname + '-' + env,
            'environment': [
                {
                    'name': 'ASPNETCORE_ENVIRONMENT',
                    'value': 'prod'
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

        resp = ecsclient_prod.register_task_definition(
            family = apiname + '-' + env,
            taskRoleArn = stsrole_prod,
            executionRoleArn = stsrole_prod,
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
        message = e
        print message
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp


# CREATING ECS SERVICE
def update_service(apiname, env, techteam):
    try:
        ecs_resp = ecsclient_prod.update_service(
            cluster=apiname,
            service=apiname + '-' + env,
            taskDefinition=apiname + '-' + env,
            desiredCount=2,
            forceNewDeployment=True,
            healthCheckGracePeriodSeconds=30
        )
        print ecs_resp
        #message = "Updating Service " + apiname + '-' + env + ' for new taskDefinition '
        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
        #print resp

    except Exception as e:
        message = e
        print message

        #time = datetime.datetime.now()
        #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'ecs_deployapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
        #print resp


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
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD1'}}, AttributesToGet=['TechnicalTeam', 'Version', 'URL'])
        url = dynamo_response['Item']['URL']['S']
        if "prod-blue" not in url:
            task_env = 'prod1'
            print task_env
            techteam = dynamo_response['Item']['TechnicalTeam']['S']
            version = dynamo_response['Item']['Version']['S']


        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': 'PROD2'}}, AttributesToGet=['TechnicalTeam', 'Version', 'URL'])
        url = dynamo_response['Item']['URL']['S']
        if "prod-blue" not in url:
            task_env = 'prod2'
            print tak_env
            techteam = dynamo_response['Item']['TechnicalTeam']['S']
            version = dynamo_response['Item']['Version']['S']

    except Exception as e:
        print e
        status_code = 409
        message = {'errorMessage': appname + " does not exist. You must create the Stack first"}
        return_message = return_body(status_code, message)
        return return_message


    prod_vpc = os.environ['PROD_WEST_VPC']
    prod_subnet = os.environ['PROD_WEST_SUBNET']
    prod_sg = os.environ['PROD_WEST_SG']
    prod_acc = os.environ['PROD_ACC']
   
    repo_uri = getstageenv_image(appname, task_env)
    env = getprodblueEnv(appname)
    create_taskdefinitions(appname, repo_uri, env)
    update_service(appname, env, techteam)
    sendnotification(appname, env, prod_acc, version)

    time = datetime.datetime.now()
    resp = dynamo_client.update_item(TableName="ECS_Inventory_Production_West", Key={'ApplicationName': {'S': appname}, 'Environment': {'S': env.upper()}}, AttributeUpdates={'Version':{'Value':{'S': version}}, 'Time':{'Value':{'S': str(time)}}})
    print resp

    status_code = 200
    message = {'message': "Deployed version " + version + " to " + appname + " in ProdBlue West Environment"}
    return_message = return_body(status_code, message)
    return return_message

    
