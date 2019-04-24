import boto3
import json

cf = boto3.client('cloudformation')


###    RETURN BODY FOR API     ###
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



def lambda_handler(event, context):
    body = json.loads(event['body'])
    print body

    try:
        devopsstack = body['devopsstackName']
        if devopsstack == "":
            status_code = 400
            message = {"errorMessage": "devopsstackName cannot be empty"}
            return_message = return_body(status_code, message)
            return return_message
    except KeyError:
        status_code = 400
        message = {"errorMessage": "devopsstackName needs to be mentioned"}
        return_message = return_body(status_code, message)
        return return_message

    try:        
        resp = cf.describe_stacks(StackName=devopsstack)
        tags = resp['Stacks'][0]['Tags']
        print tags
        for eachtag in tags:
            if eachtag['Key'] == 'version':
                version = eachtag['Value']
                print version

        status_code = 200
        message = {"version": version}
        return_message = return_body(status_code, message)
        return return_message

    except Exception as e:
        status_code = 404
        message = {"errorMessage": "Error Fetching the version of the DevOps Stack"}
        return_message = return_body(status_code, message)
        return return_message
        
