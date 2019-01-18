# **Deploy to NonProd Environments**
    POST /dev/stacks/deploytoprodBlue

## **Description**
- This API call deploys image to production blue environment
- It by default picks the version that was been deployed to non production environments of the application
- It returns 200 if the image is deployed
- It returns 400 if the parameters are missing or invalid
- It returns 409 if stack does not exists

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application name to which the image needs to be deployed
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
POST https://<api-generated>.execute-api.us-east-1.amazonaws.com/dev/stacks/deploytoprodBlue
Body:
``` json
{
	"applicationName": "MyDevOpsAPI"
}
```
### Response
``` json
{
    "message": "Deployed version 1.0.0.0 to MyDevOpsAPI in ProdBlue Environment"
}
```