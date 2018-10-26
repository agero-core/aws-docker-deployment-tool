import json
import requests

def lambda_handler(event, context):
    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    print event    

    record = event["Records"][0]
    package = record["s3"]["object"]["key"]
    print package
    ecr_repo = package.replace(".zip","")
    ecr_repo = ecr_repo.lower()
    print ecr_repo
    print "Pushing " + ecr_repo + " to ECR"

    api = event["api"]
    print api
   
    session = requests.Session()
    
    response = session.get(api, verify=False, timeout=10)
    statuscode = response.status_code
    print statuscode

    if statuscode == 200:
        health_status = "Healthy"
    else:
        health_status = "Unhealthy"
    
    return {
        "API": api,
        "Status Code": statuscode,
        "Health Status": health_status
    }

"""
event = {}
event["api"] = "https://2waycommunicationapi-stage.us-east-1.elasticbeanstalk.com/health"
context = ""
lambda_handler(event, context)
""" 
 
