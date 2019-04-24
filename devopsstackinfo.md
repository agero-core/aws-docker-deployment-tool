# **Get DevOps Stack Version**
    POST /stacks/devopsstackInfo

## **Description**
- This API call returns the version of the DevOps stack deployed
- It returns 200 with the version details
- It returns 400 if the parameter is missing or invalid

***
## **Parameters**
- **devopsstackName** _(required)_
   - This will be the DevOps stack name for which the version is required
***

## **Response**
### Success
- **200**
   - **version**
      - The version deployed for DevOps stack
### Error
- **400**
  - **errorMessage**
    - Parameter is not present
    - Parameter cannot be empty	

***
## **Example**
### Request
POST https://yourcustomdevopsdomain.com/stacks/devopsstackInfo
Body:
``` json
{
	"devopsstackName": "devops-ecs-resources-dev"
}
```
### Response
``` json
{
    "version": "1.0.0.0"
}
```