import boto3
import json
import os
import time
import datetime

cf = boto3.client('cloudformation')
dynamo_client = boto3.client('dynamodb')
sts = boto3.client('sts')

stsrolearn = os.environ['STSROLEARN']
response = sts.assume_role(RoleArn=stsrolearn, RoleSessionName='CrossAccountECSDynamoTableAccess')

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']


dynamo_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)


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


def lambda_handler(event,context):
    print event
    body = json.loads(event['body'])
    print body
    message = "Stack Creation Initiated"
    hostedzonename = os.environ['HOSTEDZONE_NAME']
    prod_hostedzonename = os.environ['PROD_HOSTEDZONE_NAME']
    version = "0.0.0.0"

    try:
        applicationname = body["applicationName"]
        if applicationname == "":
            status_code = 400
            message = {"errorMessage": "applicationName cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter applicationName is not present"}
        return_message = return_body(status_code, message)
        return return_message


    try:
        description = body["description"]
    except Exception as e:
        pass


    try:
        email = body["email"]
        if email == "":
            status_code = 400
            message = {"errorMessage": "email cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter email is not present"}
        return_message = return_body(status_code, message)
        return return_message


    try:
        ageroservice = body['tags']['ageroService']
        if ageroservice == "":
            status_code = 400
            message = {"errorMessage": "ageroService cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message

        if "OneRoad" not in ageroservice or "VIMS" not in ageroservice or "Blink Roadside" not in ageroservice or "D360" not in ageroservice or "MileUp" not in ageroservice or "NCC" not in ageroservice or "IT Internal" not in ageroservice or "Security" not in ageroservice or "Reporting" not in ageroservice or "Finance" not in ageroservice or "Business Application" not in ageroservice:            
            status_code = 400
            message = {"errorMessage": "Check the list of accepted values for ageroService"}
            return_message = return_body(status_code, message)
            return return_message        

    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter ageroService is not present"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        tier = body['tags']['tier']
        if tier == "":
            status_code = 400
            message = {"errorMessage": "tier cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message

        if "WEB" not in tier or "API" not in tier or "DATA" not in tier:
            status_code = 400
            message = {"errorMessage": "Check the list of accepted values for tier"}
            return_message = return_body(status_code, message)
            return return_message

    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter tier is not present"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        compliancetype = body['tags']['complianceType']
        if compliancetype == "":
            status_code =400
            message = {"errorMessage": "complianceType cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message

        if "NA" not in compliancetype or "PII" not in compliancetype or "PCI" not in compliancetype:
            status_code =400
            message = {"errorMessage": "Check the list of accepted values for complianceType"}
            return_message = return_body(status_code, message)
            return return_message

    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter complianceType is not present"}
        return_message = return_body(status_code, message)
        return return_message
    
    try:
        businessteam = body['tags']['businessTeam']
        if businessteam == "":
            status_code = 400
            message = {"errorMEssage": "businessTeam cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter businessTeam is not present"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        classificationlabel = body['tags']['classificationLabel']
        if classificationlabel == "":
            status_code = 400
            message = {"errorMessage": "classificationLabel cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message

        if "Level 1/Public" not in classificationlabel or "Level 2/Confidential" not in classificationlabel or "Level 3/Restricted" not in classificationlabel:
            status_code = 400
            message = {"errorMessage": "Check the listed values for classificationLabel"}
            return_message = return_body(status_code, message)
            return return_message

    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter classificationLabel is not present"}
        return_message = return_body(status_code, message)
        return return_message
    
    try:
        team = body['tags']['technicalTeam']
        if team == "":
            status_code = 400
            message = {"errorMessage": "technicalTeam cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message

        if "CoreEngineeingTeam" in team or "CoreApiServices" in team or "CorePlatformTeam" in team or "Architecture" in team or "CoreAutomationTeam" in team:
            status_code = 400
            message = {"errorMessage": "Check the listed values for technicalTeam"}
            return_message = return_body(status_code, message)
            return return_message

    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter technicalTeam is not present"}
        return_message = return_body(status_code, message)
        return return_message


    try:
        NonProd = str(body['environments']['nonProd'])
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter nonProd is not present"}
        return_message = return_body(status_code, message)
        return return_message


    try:
        Training = body['environments']['training']
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter training is not present"}
        return_message = return_body(status_code, message)
        return return_message

    try:
        DA = body['environments']['da']
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter da is not present"}
        return_message = return_body(status_code, message)
        return return_message


    if 'qa' in NonProd.lower():
        QAEnvironment = "QA"
        qa_env = "YES"
        qa_endpoint = applicationname + ".dkr.qa." + hostedzonename
    else:
        QAEnvironment = "None"
        qa_env = "NO"
        qa_endpoint = "N/A"

    if 'dev' in NonProd.lower():
        DevEnvironment = "DEV"
        dev_env = "YES"
        dev_endpoint = applicationname + ".dkr.dev." + hostedzonename
    else:
        DevEnvironment = "None"
        dev_env = "NO"
        dev_endpoint = "N/A"

    ProdEnvironment = "PROD"
    prod_env = "YES"
    prod_endpoint = applicationname + ".dkr.prod." + prod_hostedzonename

    if Training == True:
        TrainEnvironment = "TRAINING"
        train_env = "YES"
        train_endpoint = applicationname + ".dkr.training." + hostedzonename
    else:
        TrainEnvironment = "None"
        train_env = "NO"
        train_endpoint = "N/A"

    if DA == True:
        DAEnvironment = "DA"
        da_env = "YES"
        da_endpoint = applicationname + ".dkr.da." + hostedzonename
    else:
        DAEnvironment = "None"
        da_env = "NO"
        da_endpoint = "N/A"

    if NonProd == "" or 'stage' in NonProd.lower():
        StageEnvironment = "STAGE"
        stage_env = "YES"
        stage_endpoint = applicationname + ".dkr.stage." + hostedzonename
    else:
        StageEnvironment = "None"
        stage_env = "NO"
        stage_endpoint = "N/A"

    application = "New Application"

    print application
    print "Creating Stack for " + applicationname + " under team " + team + " with following Parameters"
    print "Description: " + description
    print "Following Environments created:"
    print DevEnvironment, QAEnvironment, StageEnvironment, ProdEnvironment, TrainEnvironment

    nonprod_acc = os.environ['NONPROD_ACC']
    prod_acc = os.environ['PROD_ACC']
    template_url = os.environ['CF_TEMPLATE']
    devqa_vpc = os.environ['DEVQA_VPC']
    stage_vpc = os.environ['STAGE_VPC']
    training_vpc = os.environ['TRAINING_VPC']
    da_vpc = os.environ['DA_VPC']
    prod_vpc = os.environ['PROD_VPC']
    devqa_subnet = os.environ['DEVQA_SUBNET']
    stage_subnet = os.environ['STAGE_SUBNET']
    training_subnet = os.environ['TRAINING_SUBNET']
    da_subnet = os.environ['DA_SUBNET']
    prod_subnet = os.environ['PROD_SUBNET']
    devqa_albsubnet = os.environ['DEVQA_ALBSUBNET']
    stage_albsubnet = os.environ['STAGE_ALBSUBNET']
    training_albsubnet = os.environ['TRAINING_ALBSUBNET']
    da_albsubnet = os.environ['DA_ALBSUBNET']
    prod_albsubnet = os.environ['PROD_ALBSUBNET']
    devqa_sg = os.environ['DEVQA_SG']
    stage_sg = os.environ['STAGE_SG']
    training_sg = os.environ['TRAINING_SG']
    da_sg = os.environ['DA_SG']
    prod_sg = os.environ['PROD_SG']
    devqa_albsg = os.environ['DEVQA_ALBSG']
    stage_albsg = os.environ['STAGE_ALBSG']
    training_albsg = os.environ['TRAINING_ALBSG']
    da_albsg = os.environ['DA_ALBSG']
    prod_albsg = os.environ['PROD_ALBSG']

    ecr_name = applicationname.lower()
    repo_uri = os.environ['REPO_URI']

    admin_rolearn = os.environ['ADMIN_ROLEARN']
    execution_rolename = os.environ['EXECUTION_ROLENAME']
    
    try: 
        response = cf.create_stack_set(
        StackSetName= applicationname,
        TemplateURL=template_url,
        Parameters=[
            {
                'ParameterKey': 'ApplicationName',
                'ParameterValue': applicationname,
            },
            {
                'ParameterKey': 'AppDescription',
                'ParameterValue': description,
            },
            {
                'ParameterKey': 'Application',
                'ParameterValue': application,
            },
            {
                'ParameterKey': 'EmailAddress',
                'ParameterValue': email,
            },
            {
                'ParameterKey': 'DevEnvironment',
                'ParameterValue': DevEnvironment,
            },
            {
                'ParameterKey': 'QAEnvironment',
                'ParameterValue': QAEnvironment,
            },
            {
                'ParameterKey': 'StageEnvironment',
                'ParameterValue': StageEnvironment,
            },
            {
                'ParameterKey': 'ProdEnvironment',
                'ParameterValue': ProdEnvironment,
            },
            {
                'ParameterKey': 'TrainEnvironment',
                'ParameterValue': TrainEnvironment,
            },
            {
                'ParameterKey': 'DAEnvironment',
                'ParameterValue': DAEnvironment,
            },
            {   'ParameterKey': 'DomainName',
                'ParameterValue': hostedzonename
            },
            {   'ParameterKey': 'ProdDomainName',
                'ParameterValue': prod_hostedzonename
            },            
            {
                'ParameterKey': 'DEVQAVPC',
                'ParameterValue': devqa_vpc,
            },
            {
                'ParameterKey': 'STAGEVPC',
                'ParameterValue': stage_vpc,
            },
            {
                'ParameterKey': 'TRAININGVPC',
                'ParameterValue': training_vpc,
            },
            {
                'ParameterKey': 'DAVPC',
                'ParameterValue': da_vpc,
            },
            {
                'ParameterKey': 'PRODVPC',
                'ParameterValue': prod_vpc,
            },
            {
                'ParameterKey': 'DEVQASUBNET',
                'ParameterValue': devqa_subnet,
            },
            {
                'ParameterKey': 'STAGESUBNET',
                'ParameterValue': stage_subnet,
            },
            {
                'ParameterKey': 'TRAININGSUBNET',
                'ParameterValue': training_subnet,
            },
            {
                'ParameterKey': 'DASUBNET',
                'ParameterValue': da_subnet,
            },
            {
                'ParameterKey': 'PRODSUBNET',
                'ParameterValue': prod_subnet,
            },
            {
                'ParameterKey': 'ECRName',
                'ParameterValue': ecr_name,
            },
            {
                'ParameterKey': 'RepoURI',
                'ParameterValue': repo_uri,
            },
            {
                'ParameterKey': 'DEVQAALBSUBNET',
                'ParameterValue': devqa_albsubnet,
            },
            {
                'ParameterKey': 'STAGEALBSUBNET',
                'ParameterValue': stage_albsubnet,
            },
            {
                'ParameterKey': 'TRAININGALBSUBNET',
                'ParameterValue': training_albsubnet
            },
            {
                'ParameterKey': 'DAALBSUBNET',
                'ParameterValue': da_albsubnet
            },
            {
                'ParameterKey': 'PRODALBSUBNET',
                'ParameterValue': prod_albsubnet
            },
            {
                'ParameterKey': 'DEVQASG',
                'ParameterValue': devqa_sg,
            },
            {
                'ParameterKey': 'STAGESG',
                'ParameterValue': stage_sg,
            },
            {
                'ParameterKey': 'TRAININGSG',
                'ParameterValue': training_sg,
            },
            {
                'ParameterKey': 'DASG',
                'ParameterValue': da_sg,
            },
            {
                'ParameterKey': 'PRODSG',
                'ParameterValue': prod_sg,
            },
            {
                'ParameterKey': 'DEVQAALBSG',
                'ParameterValue': devqa_albsg,
            },
            {
                'ParameterKey': 'STAGEALBSG',
                'ParameterValue': stage_albsg,
            },
            {
                'ParameterKey': 'TRAININGALBSG',
                'ParameterValue': training_albsg,
            },
            {
                'ParameterKey': 'DAALBSG',
                'ParameterValue': da_albsg,
            },
            {
                'ParameterKey': 'PRODALBSG',
                'ParameterValue': prod_albsg,
            },
            {
                'ParameterKey': 'AgeroService',
                'ParameterValue': ageroservice
            },
            {
                'ParameterKey': 'Tier',
                'ParameterValue': tier
            },
            {
                'ParameterKey': 'ComplianceType',
                'ParameterValue': compliancetype
            },
            {
                'ParameterKey': 'TechnicalTeam',
                'ParameterValue': team
            },
            {
                'ParameterKey': 'BusinessTeam',
                'ParameterValue': businessteam
            },
            {
                'ParameterKey': 'ClassificationLabel',
                'ParameterValue': classificationlabel
            },
            {
                'ParameterKey': 'NonProdAccountId',
                'ParameterValue': nonprod_acc
            },
            {
                'ParameterKey': 'ProdAccountId',
                'ParameterValue': prod_acc
            }            
        ],
        Tags = [
            {
                'Key': 'Application',
                'Value': applicationname
            },
            {
                'Key': 'Email',
                'Value': email
            },
            {
                'Key': 'Version',
                'Value': version
            },
            {
                'Key': 'AgeroService',
                'Value': ageroservice
            },
            {
                'Key': 'Tier',
                'Value': tier
            },
            {
                'Key': 'ComplianceType',
                'Value': compliancetype
            },
            {
                'Key': 'TechnicalTeam',
                'Value': team
            },
            {
                'Key': 'BusinessTeam',
                'Value': businessteam
            },
            {
                'Key': 'ClassificationLabel',
                'Value': classificationlabel
            }
        ],
        AdministrationRoleARN=admin_rolearn,
        ExecutionRoleName=execution_rolename
    )

        print response

    except Exception as e:
        status_code = 400
        message = { "errorMEssage": "StackSet already exists" }
        print e
        return_message = return_body(status_code, message)
        return return_message

    try:
        resp = cf.create_stack_instances(
        StackSetName = applicationname,
        Accounts = [nonprod_acc, prod_acc],
        Regions = ["us-east-1"]
        )
        print resp

    except Exception as e:
        status_code = 400
        message = { "errorMEssage": "StackSet Instances Creation Error" }
        print e
        return_message = return_body(status_code, message)
        return return_message


    status_time = datetime.datetime.now()

    message = "Stack Creation Started for " + applicationname
    #resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'createstack'}, 'Time': {'S': str(status_time)}, 'Message': {'S': message}})
    #print resp

    if dev_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'DEV'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str(dev_endpoint)}, 'Time':{'S': str(status_time)}})
    if qa_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'QA'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str(qa_endpoint)}, 'Time':{'S': str(status_time)}})
    if stage_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'STAGE'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str(stage_endpoint)}, 'Time':{'S': str(status_time)}})
    if prod_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'PROD-BLUE'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str('')}, 'Time':{'S': str(status_time)}})
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'PROD-GREEN'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str(prod_endpoint)}, 'Time':{'S': str(status_time)}})
    if train_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Training", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'TRAINING'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str(train_endpoint)}, 'Time':{'S': str(status_time)}})
    if da_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_DA", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'DA'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'URL': {'S': str(da_endpoint)}, 'Time':{'S': str(status_time)}})


    status_code = 200
    return_message = {
    'message' : message,
    'application' : applicationname,
    'ecrName' : ecr_name,
    'technicalTeam' : team,
    'email' : email,
    'environmentType' : [{'DEV': dev_env, 'Endpoint': dev_endpoint}, {'QA': qa_env, 'Endpoint': qa_endpoint}, {'STAGE': stage_env, 'Endpoint': stage_endpoint}, {'PROD': prod_env, 'Endpoint': prod_endpoint}, {'TRAINING': train_env, 'Endpoint': train_endpoint}, {'DA': da_env, 'Endpoint': da_endpoint}]
    }
    
    return_message = return_body(status_code, return_message)
    return return_message




