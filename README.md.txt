1) Resources created by this serverless template:
	a) DynamoDB which will store the invemtory of all the deployed applications
	b) S3 bucket which will store all the images
	c) A deployapi lambda function which will create the ecs resources and will trigger whenever a new object is uploaded to s3 bucket
	d) An healthcheckapi lambda function that will do the health check of any api
		Ex: curl -H "Content-Type: application/json" -X POST https://<api-created-by-apigateway>/?api=<api-to-perform-healthcheck>
2) Check out the parameters.yml file to fill out all the necessary parameters for the template to work
3) Once that's done execute the following command:
	sls deploy