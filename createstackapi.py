import boto3
import json
import os
import time
import datetime

cf = boto3.client('cloudformation')
dynamo_client = boto3.client('dynamodb')

def lambda_handler(event,context):
    print event
    message = "Successfully Created Stack"
    applicationname = event["applicationname"]
    if applicationname == "":
        message = "ApplicationName needs to be specified"
        return {
            'message' : message
        }

    description = event["description"]
    email = event["email"]
    if email == "":
        message = "Email needs to be specified"
        return {
            'message' : message
        }

    ageroservice = event['ageroservice']
    if ageroservice == "":
        message = "AgeroService needs to be specified"
        return {
            'message' : message
        }

    tier = event['tier']
    if tier == "":
        message = "Tier needs to be specified"
        return {
            'message' : message
        }

    compliancetype = event['compliancetype']
    if compliancetype == "":
        message = "ComplianceType needs to be specified"
        return {
            'message' : message
        }

    businessteam = event['businessteam']
    if businessteam == "":
        message = "BusinessTeam needs to be specified"
        return {
            'message' : message
        }

    classificationlabel = event['classificationlabel']
    if classificationlabel == "":
        message = "ClassificationLabel needs to be specified"
        return {
            'message' : message
        }
    
    team = event['technicalteam']
    if team == "":
        message = "TechnicalTeam needs to be specified"
        return {
            'message' : message
        }

    NonProd = event["NonProd"]
    Prod = event["Prod"]
    Training = event["Train"]

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

    if 'yes' in Prod.lower():
        ProdEnvironment = "PROD"
        prod_env = "YES"
    else:
        ProdEnvironment = "None"
        prod_env = "NO"

    if 'yes' in Training.lower():
        TrainEnvironment = "TRAINING"
        train_env = "YES"
    else:
        TrainEnvironment = "None"
        train_env = "NO"

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
    albsubnet1 = os.environ['ALB_SUBNET1']
    albsubnet2 = os.environ['ALB_SUBNET2']
    albsg = os.environ['ALB_SG']
    sg1 = os.environ['SG']
    ecr_name = applicationname.lower()
    
    
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
            'ParameterKey': 'ECRName',
            'ParameterValue': ecr_name,
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
            'ParameterKey': 'ALBSG',
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


    print response


    status_time = datetime.datetime.now()
    if dev_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'DEV'}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if qa_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'QA'}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if stage_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_NonProduction", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'STAGE'}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if prod_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'PROD'}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})
    if train_env == "YES":
        resp = dynamo_client.put_item(TableName="ECS_Inventory_Production", Item={'ApplicationName':{'S': applicationname}, 'Environment':{'S': 'TRAINING'}, 'TechnicalTeam': {'S': team}, 'Time':{'S': str(status_time)}})


    return {
    'message' : message,
    'application' : applicationname,
    'ECRName' : ecr_name,
    'TechnicalTeam' : team,
    'Email' : email,
    'EnvironmentType' : [{'DEV': dev_env}, {'QA': qa_env}, {'STAGE': stage_env}, {'PROD': prod_env}, {'TRAINING': train_env}]
    }
    


