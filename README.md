# aws-docker-deployment-tool


##  Check out the parameters.yml file to fill out all the necessary parameters for the template to work
	apiname: <api name>
	stage: <stage - dev/qa/stage/prod>
	accountid: <aws account id>
	vpc: <vpc id>
	subnet: <subnet id>
	sg: <security group id>
	region: <aws region>


##  Resources created by this serverless template

	1) DynamoDB
		a) DynamoECSInventoryNonProd:
			This Dyanmo Table will have inventory of all Non Production Applications with Application Name and URL as primary attributes
		b) DynamoECSInventoryProd:
			This Dyanmo Table will have inventory of all Production Applications with Application Name and URL as primary attributes
	
	2) S3:
		a) Modify this bucket name which will store all the images of the Application with versioning enabled on this bucket
		
	3) Lambda Functions
		a) deployapi:
			This Lambda Function will trigger when an object (Docker Image) is uploaded to above S3 bucket. This function will simply pull out the name and print it out.
			Future Scope: It will create ECR, Task Definitions (Containers) and Run Services
	
		b) healthcheckapi:
			An healthcheckapi lambda function that will do the health check of any api
			Ex: curl -H "Content-Type: application/json" -X POST https://<api-created-by-apigateway>/?api=<api-to-perform-healthcheck>
		


##  Once that's done execute the following command
	sls deploy
	
## Rollback the Stack
	sls remove