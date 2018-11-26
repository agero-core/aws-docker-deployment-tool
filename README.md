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

	1. API Gateway
	   **<api>/dev/createstack/**
	     - Parameters to be passed
		   - applicationname
		   - email
		   - NonProd : Required Values: dev,qa,stage (Values must be seperated by ',' and if empty dev will be provisioned by default
		   - Prod : Required Values - Yes or No
		   - Train : Required Values - Yes or No
		   - ageroservice
		   - tier
		   - compliancetype
		   - technicalteam
		   - businessteam
		   - classificationlabel
		 - Triggers: createstackapi Lambda handler
		   
	   **<api>/dev/deploy/**
	     - Parameters to be passed	   
	       - application : Application Name
		   - environment : Values like dev,qa,stage (seperated by ',')
		   - repouri : Repouri that gets created when image is pushed
	     - Triggers: ecs_deployapi Lambda handler
	   
	   **<api>/dev/deletestack/**
	     - Parameters to be passed	   
	       - stack : Name of the stack to be deleted
		 - Triggers: deletestackapi Lambda handler
		 
	   **<api>/dev/**
	     - Parameters to be passed	  
	       - api : API Health URL to perform health check
		 - Triggers: healthcheckapi Lambda handler
		 
	   **<api>/dev/devops/querylogs**
	     - Parameters to be passed	   
	       - resourcename : Name of the Lambda resource deployed
		   - starttime : Time to start retrieving logs from. Format: yyyy-mm-dd hh:mm:ss
		   - endtime : Time till which logs needs to be retrieved from. Format: yyyy-mm-dd hh:mm:ss
	     - Triggers: querydevopslogsapi Lambda handler
		   
	2. DynamoDB
	   - DynamoECSInventoryNonProd:
		 - This Dyanmo Table will have inventory of all Non Production Applications with Application Name and URL as primary attributes
		 
	   - DynamoECSInventoryProd:
		 - This Dyanmo Table will have inventory of all Production Applications with Application Name and URL as primary attributes
		 
	   - DevOpsLogsTable
	     - This Table will contain all the logs for lambda functions deployed under devops resources with the message and appropriate timestamp
	
	3. S3
	   - Modify this bucket name which will store all the images of the Application with versioning enabled on this bucket
		
	4. Lambda Functions
	   - createstackapi:
	     - This lambda function will be triggered by the API and will create the application stack for developers.
		 - It creates application load balancer for the desired environments 
		 
	   - ecs_deployapi:
		 - This Lambda Function will triggered by the API and will deploy the image with the given repouri in the environments
		 - It creates Target Groups and Listeners running behind the same ALB, Task Definitions (Containers) and Runs the task as Service in the given Cluster
	
	   - healthcheckapi:
	     - An healthcheckapi lambda function that will do the health check of any api
		 - Ex: curl -H "Content-Type: application/json" -X POST https://<api-created-by-apigateway>/?api=<api-to-perform-healthcheck>
			
	   - devopshealthcheckapi:
		 - An devopshealthcheckapi lambda function that will perform healthcheck on DevOps Resources deployed and return a JSON response with the health status of each of the resources
		 - Ex: curl -H "Content-Type: application/json" -X GET https://<api-created-by-apigateway>/<stage>/devops/health
		 
	   - querydevopslogsapi:
	     - This lambda function will return logs for the queried function within the specified timerange for devops resources
		 - Format of the api query:  https://<api-created-by-apigateway>/<stage>/devops/querylogs?resourcename=<lambda-function>&starttime=<yyyy-mm-dd> <hh:mm:ss>&endtime=<yyyy-mm-dd> <hh:mm:ss>
		 
	   - deletestackapi:
	     - This Lambda handler will delete the stack that's provided in the parameter


##  Once that's done execute the following command
	sls deploy
	
## Rollback the Stack
	sls remove