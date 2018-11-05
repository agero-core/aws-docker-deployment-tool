import boto3
import json
import datetime

dynamo = boto3.client('dynamodb')
s3 = boto3.resource('s3')

def lambda_handler(event, context):

    message = "Performing Health Check for DevOps Resources"
    time = datetime.datetime.now()
    resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

    try:
        response = dynamo.list_tables()['TableNames']
        message = "Checking the DynamoDB to see if the Table Exists"
        time = datetime.datetime.now()
        resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
    except:
        message = "Error in Fetching and Comparing Tables from DynamoDB"
        time = datetime.datetime.now()
        resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

    table1 = "ECS_Inventory_NonProd"
    table2 = "ECS_Inventory_Prod"
    bucket = "agero-ecs-test-bucket"
    status = {}
    status_table1 = {}
    status_table2 = {}
    status_bucket = {}
    overall_success = "true"
    current_time = datetime.datetime.now()

    message = "Checking status for ECS_Inventory_NonProd"
    time = datetime.datetime.now()
    resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
   
 
    if table1 in response:
        status_table1["verificationType"] = table1 + " Status Check"
        status_table1["isSuccessful"] = "true"
        status_table1["verificationDescription"] = "Table Exists"
        status_table1["errorDetails"] = "null"

    else:
        status_table1["verificationType"] = table1 + " Status Check"
        status_table1["isSuccessful"] = "false"
        status_table1["verificationDescription"] = "Table Not Found"
        status_table1["errorDetails"] = "Table Does Not Exist in DyanmoDB Inventory"
        overall_success = "false"

    message = "Checking status for ECS_Inventory_Prod"
    time = datetime.datetime.now()
    resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})


    if table2 in response:
        status_table2["verificationType"] = table2 + " Status Check"
        status_table2["isSuccessful"] = "true"
        status_table2["verificationDescription"] = "Table Exists"
        status_table2["errorDetails"] = "null"

    else:
        status_table2["verificationType"] = table2 + " Status Check"
        status_table2["isSuccessful"] = "false"
        status_table2["verificationDescription"] = "Table Not Found"
        status_table2["errorDetails"] = "Table Does Not Exist in DyanmoDB Inventory"
        overall_success = "false"

    message = "Checking status for S3 " + bucket
    time = datetime.datetime.now()
    resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

        
    if s3.Bucket(bucket) in s3.buckets.all():
        status_bucket["verificationType"] = bucket + " Status Check"
        status_bucket["isSuccessful"] = "true"
        status_bucket["verificationDescription"] = "Bucket Exists"
        status_bucket["errorDetails"] = "null"

    else:
        status_bucket["verificationType"] = bucket + " Status Check"
        status_bucket["isSuccessful"] = "false"
        status_bucket["verificationDescription"] = "Bucket Not Found"
        status_bucket["errorDetails"] = "This S3 Bucket does not Exist"
        overall_success = "false"
        
    status["verificaions"] = [status_table1, status_table2, status_bucket]
    status["overallSuccess"] = overall_success
    status["name"] = "DevOps Resources Health Check"
    status["buildVersion"] = "1.0.0.0"
    status["time"] = str(current_time)

    message = "Sending the HealthCheck Status to API request"
    time = datetime.datetime.now()
    resp = dynamo.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'devopshealthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

    print json.dumps(status, indent=4, sort_keys=True)
    return json.dumps(status, indent=4, sort_keys=True)


    
    
    
