# aws-docker-deployment-tool


##  Check out the parameters.yml file to fill out all the necessary parameters for the template to work
	apiname: <api name>
	stage: <stage - dev/qa/stage/prod>
	accountid: <aws account id>
	vpc: <vpc id>
	subnet1: <subnet id1>
	subnet2: <subnet id2>
	elbsubnet1: <alb subnet id1>
	elbsubnet2: <alb subnet id2>
	sg: <security group id>
	elbsg: <alb security group id>	
	region: <aws region>
	repouri: <ecr repository uri>


##  Resources created by this serverless template

	1. DynamoDB
	   - DynamoECSInventoryNonProd:
		 - This Dyanmo Table will have inventory of all Non Production Applications with Application Name and URL as primary attributes
		 
	   - DynamoECSInventoryProd:
		 - This Dyanmo Table will have inventory of all Production Applications with Application Name and URL as primary attributes
		 
	   - DevOpsLogsTable
	     - This Table will contain all the logs for lambda functions deployed under devops resources with the message and appropriate timestamp
	
	2. S3
	   - Modify this bucket name which will store all the images of the Application with versioning enabled on this bucket
		
	3. Lambda Functions
	   - deployapi:
		 - This Lambda Function will trigger when an object (Docker Image) is uploaded to above S3 bucket. This function will deploy services with the name of the application provided as the package name.
		 - It creates Application LoadBalancer, two Target Groups (Blue and Green) running behind the same ALB, Task Definitions (Containers) and Runs Two Services as Blue and Green
	
	   - healthcheckapi:
	     - An healthcheckapi lambda function that will do the health check of any api
		 - Ex: curl -H "Content-Type: application/json" -X POST https://<api-created-by-apigateway>/?api=<api-to-perform-healthcheck>
			
	   - devopshealthcheckapi:
		 - An devopshealthcheckapi lambda function that will perform healthcheck on DevOps Resources deployed and return a JSON response with the health status of each of the resources
		 - Ex: curl -H "Content-Type: application/json" -X GET https://<api-created-by-apigateway>/<stage>/devops/health
		 
	   - querydevopslogsapi:
	     - This lambda function will return logs for the queried function within the specified timerange for devops resources
		 - Format of the api query:  https://<api-created-by-apigateway>/<stage>/devops/querylogs?resourcename=<lambda-function>&starttime=<yyyy-mm-dd> <hh:mm:ss>&endtime=<yyyy-mm-dd> <hh:mm:ss>
		


##  Once that's done execute the following command
	sls deploy
	
## Rollback the Stack
	sls remove