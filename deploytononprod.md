# **Deploy to NonProd Environments**
    POST /dev/stacks/deploytoNonProd

## **Description**
- This API call deploys image to application stack that was been created
- It returns 200 if the image is deployed to all the environments
- It returns 400 if the parameters are missing or invalid
- It returns 409 if stack does not exists

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application name to which the image needs to be deployed
- **environment** _(required)_
   - This will be the list of environments to which the image needs to be deployed
- **imageTag** _(required)_
   - This will be the image tag from ECR of the given application that needs to be deployed
- **version** _(required)_
   - This will be the version number for the associated image (It should be same as the imageTag)
***
## **Response**
### Success
- **200**
   - **message**
      - The parameter message displays "Deployed version x.x.x.x to <applicationName>"
### Error
- **400**
  - **errorMessage**
    - The value contains the message in case some values of the object body are invalid or null
- **409**
  - **errorMessage**
    - The value contains the message in case application is not present or already deleted

***
## **Example**
### Request
POST https://<api-generated>.execute-api.us-east-1.amazonaws.com/dev/stacks/deploy
Body:
``` json
{
	"applicationName": "MyDevOpsAPI",
	"environment": ["dev", "qa", "stage"],
	"imageTag": "1.0.0.0",
	"version": "1.0.0.0"
}
```
### Response
``` json
{
    "message": "Deployed version 1.0.0.0 to MyDevOpsAPI"
}
```