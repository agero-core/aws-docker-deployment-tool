import boto3
import requests
import datetime
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#from requests.exceptions import ConnectionError

dynamo_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    print event

    message = "Retrieving Requested Application API to perform health check"
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'healthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})
    
    api = event["api"]
    print api

    try:
        message = "Checking Health Status for API " + api 
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'healthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

        session = requests.Session()

        response = session.get(api, verify=False, timeout=10)
        statuscode = response.status_code
        print statuscode

        if statuscode == 200:
            health_status = "Healthy"
        else:
            health_status = "Unhealthy"
    
    except:
        message = "Error while performing health check on " + api
        time = datetime.datetime.now()
        resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'healthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

    message = "Sending Health Check Status for API " + api
    time = datetime.datetime.now()
    resp = dynamo_client.put_item(TableName="DevOpsLogsTable", Item={'ResourceName':{'S': 'healthcheckapi'}, 'Time':{'S': str(time)}, 'Message': {'S': message}})

    message = {
        "api": api,
        "statusCode": str(statuscode),
        "healthStatus": health_status
    }
    status_code = 200
    return {
            'statusCode': str(status_code),
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                }
            }


