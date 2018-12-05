import boto3
import json
import datetime

cf = boto3.client('cloudformation')
dynamo_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
ecs = boto3.client('ecs')

def stackexists(stackname):
    try:
        response = cf.describe_stacks(StackName=stackname)
    except Exception as e:
            status_code = 400
            message = {'errorMessage': "Stack does not exist"}
            return {
                'statusCode': str(status_code),
                'body': json.dumps(message),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
                }

def lambda_handler(event, context):

    print event
    body = json.loads(event['body'])

    try:
        stackname = body['stack']
        if stackname == "":
            status_code = 400
            message = {"errorMessage": "Parameter Validation Error: stackname cannot be empty"}
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
        message = {"errorMessage": "Parameter Validation Error: stackname needs to be mentioned"}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }

    message = "Deleting " + stackname
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
    print resp


    message = "All Environments Deleted"
    nonprod_table = dynamodb.Table("ECS_Inventory_NonProduction")
    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'DEV'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam

        name = stackname+'-'+'dev'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = nonprod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'DEV'})
        print response
        
    except Exception as e:
        message = str(e)
        pass 

    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'QA'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam

        name = stackname+'-'+'qa'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = nonprod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'QA'})
        print response

    except Exception as e:
        message = str(e)
        pass

    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_NonProduction", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'STAGE'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam

        name = stackname+'-'+'stage'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = nonprod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'STAGE'})
        print response

    except Exception as e:
        message = str(e)
        pass
        
    
    prod_table = dynamodb.Table("ECS_Inventory_Production")
    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'PROD-BLUE'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam

        name = stackname+'-'+'prod-blue'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = prod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'PROD-BLUE'})
        print response

    except Exception as e:
        message = str(e)
        pass


    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'PROD-GREEN'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam

        name = stackname+'-'+'prod-green'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = prod_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'PROD-GREEN'})
        print response


    except Exception as e:
        message = str(e)
        pass


    trainda_table = dynamodb.Table("ECS_Inventory_Training_DA")
    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Production", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'TRAINING'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam        

        name = stackname+'-'+'training'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = trainda_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'TRAINING'})
        print response

    except Exception as e:
        message = str(e)
        pass


    try:
        dynamo_response = dynamo_client.get_item(TableName="ECS_Inventory_Training_DA", Key={'ApplicationName': {'S': stackname}, 'Environment': {'S': 'DA'}}, AttributesToGet=['TechnicalTeam'])
        techteam = dynamo_response['Item']['TechnicalTeam']['S']
        print techteam

        name = stackname+'-'+'da'
        ecs_resp = ecs.delete_service(cluster=techteam, service=name, force=True)
        resp = ecs.list_task_definitions(familyPrefix=name,status='ACTIVE')
        taskdef_arn = resp['taskDefinitionArns']
        print taskdef_arn
        for each_taskdef_arn in taskdef_arn:
            print each_taskdef_arn
            task_resp = ecs.deregister_task_definition(taskDefinition=each_taskdef_arn)

        response = trainda_table.delete_item(Key={'ApplicationName': stackname, 'Environment': 'DA'})
        print response

    except Exception as e:
        message = str(e)
        pass


    try:
        response = cf.delete_stack(StackName=stackname)
        print response
    except Exception as e:
        status_code = 409
        message = {'message': 'Stack does not Exists'}
        return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }        

    message = "Deleted Stack " + stackname
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName': {'S': 'ecs_deployapi'}, 'Time': {'S': str(time)}, 'Message': {'S': message}})
    print resp

    status_code = 200
    message = {"message": "Stack " + stackname + " has been deleted"}
    
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
            }
        }


