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



 
