import boto3
import json
import os
import time
import datetime

cf = boto3.client('cloudformation')
dynamo_client = boto3.client('dynamodb')



def lambda_handler(event,context):
    print event
    body = json.loads(event['body'])
    print body
    message = "Stack Creation Initiated"

    try:
        applicationname = body["applicationName"]
        if applicationname == "":
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
    except Exception as e:
        status_code = 400
        message = {"errorMessage": "Parameter applicationName is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    try:
        description = body["description"]
    except Exception as e:
        pass

    version = "0.0.0.0"

    try:
        email = body["email"]
        if email == "":
            status_code = 400
            message = {"errorMessage": "email cannot be empty"}
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
        message = {"errorMessage": "Parameter email is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    try:
        ageroservice = body['tags']['ageroService']
        if ageroservice == "":
            status_code = 400
            message = {"errorMessage": "ageroService cannot be empty"}
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
        message = {"errorMessage": "Parameter ageroService is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }       

    try:
        tier = body['tags']['tier']
        if tier == "":
            status_code = 400
            message = {"errorMessage": "tier cannot be empty"}
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
        message = {"errorMessage": "Parameter ageroService is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    try:
        compliancetype = body['tags']['complianceType']
        if compliancetype == "":
            status_code =400
            message = {"errorMessage": "complianceType cannot be empty"}
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
        message = {"errorMessage": "Parameter complianceType is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }
    try:
        businessteam = body['tags']['businessTeam']
        if businessteam == "":
            status_code = 400
            message = {"errorMEssage": "businessTeam cannot be empty"}
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
        message = {"errorMessage": "Parameter businessTeam is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    try:
        classificationlabel = body['tags']['classificationLabel']
        if classificationlabel == "":
            message = {"errorMessage": "classificationLabel cannot be empty"}
    except KeyError:
        status_code = 400
        message = {"errorMessage": "Parameter classificationLabel is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }
    
    try:
        team = body['tags']['technicalTeam']
        if team == "":
            status_code = 400
            message = {"errorMessage": "technicalTeam cannot be empty"}
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
        message = {"errorMessage": "Parameter technicalTeam is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }


    try:
        NonProd = str(body['environments']['nonProd'])
    except KeyError:
        status_code = 400
        message = {"errorMessage": "Parameter nonProd is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    try:
        Training = body['environments']['training']
    except KeyError:
        status_code = 400
        message = {"errorMessage": "Parameter training is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    try:
        DA = body['environments']['da']
    except KeyError:
        status_code = 400
        message = {"errorMessage": "Parameter da is not present"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    if 'qa' in NonProd.lower():
        QAEnvironment = "QA"
        qa_env = "YES"
    else:
        QAEnvironment = "None"
        qa_env = "NO"

    if 'stage' in NonProd.lower():
        StageEnvironment = "STAGE"
        stage_env = "YES"
    else:
        StageEnvironment = "None"
        stage_env = "NO"

    ProdEnvironment = "PROD"
    prod_env = "YES"

    if Training == True:
        TrainEnvironment = "TRAINING"
        train_env = "YES"
    else:
        TrainEnvironment = "None"
        train_env = "NO"

    if DA == True:
        DAEnvironment = "DA"
        da_env = "YES"
    else:
        DAEnvironment = "None"
        da_env = "NO"

    if NonProd == "" or 'dev' in NonProd.lower():
        DevEnvironment = "DEV"
        dev_env = "YES"
    else:
        DevEnvironment = "None"
        dev_env = "NO"

    application = "New Application"

    print application
    print "Creating Stack for " + applicationname + " under team " + team + " with following Parameters"
    print "Description: " + description
    print "Following Environments created:"
    print DevEnvironment, QAEnvironment, StageEnvironment, ProdEnvironment, TrainEnvironment

    template_url = os.environ['CF_TEMPLATE']
    vpc = os.environ['VPC']
    subnet1 = os.environ['SUBNET1']
    subnet2 = os.environ['SUBNET2']
    albsubnet1 = os.environ['ALB_SUBNET1']
    albsubnet2 = os.environ['ALB_SUBNET2']
    albsg = os.environ['ALB_SG']
    sg1 = os.environ['SG']
    ecr_name = applicationname.lower()
    repo_uri = os.environ['REPO_URI']
    
    try: 
        response = cf.create_stack(
        StackName= applicationname,
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
            {
                'ParameterKey': 'VPC',
                'ParameterValue': vpc,
            },
            {
                'ParameterKey': 'SUBNET1',
                'ParameterValue': subnet1,
            },
            {
                'ParameterKey': 'SUBNET2',
                'ParameterValue': subnet2,
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
                'ParameterKey': 'ALBSubnetAZ1',
                'ParameterValue': albsubnet1,
            },
            {
                'ParameterKey': 'ALBSubnetAZ2',
                'ParameterValue': albsubnet2,
            },
            {
                'ParameterKey': 'ALBSG1',
                'ParameterValue': albsg,
            },
            {
                'ParameterKey': 'SG1',
                'ParameterValue': sg1,
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
            }
        ],
        ResourceTypes = ["AWS::ECS::*", "AWS::ECR::*", "AWS::Lambda::*", "AWS::ElasticLoadBalancingV2::LoadBalancer"],
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
        ]
    )

    except Exception as e:
        status_code = 400
        message = { "errorMEssage": "Stack already exists" }
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    print response


    status_time = datetime.datetime.now()

    message = "Stack Creation Started for " + applicationname
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'createstack'}, 'Time': {'S': str(status_time)}, 'Message': {'S': message}})
    print resp

    if dev_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'DEV'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if qa_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'QA'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if stage_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'STAGE'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if prod_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'PROD-BLUE'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'PROD-GREEN'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if train_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Training", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'TRAINING'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if da_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_DA", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'DA'}, 'Version':{'S': version}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})


    status_code = 200
    return_message = {
    'message' : message,
    'application' : applicationname,
    'ecrName' : ecr_name,
    'technicalTeam' : team,
    'email' : email,
    'environmentType' : [{'DEV': dev_env}, {'QA': qa_env}, {'STAGE': stage_env}, {'PROD': prod_env}, {'TRAINING': train_env}, {'DA': da_env}]
    }
    
    return {
        'statusCode': str(status_code),
        'body': json.dumps(return_message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }



