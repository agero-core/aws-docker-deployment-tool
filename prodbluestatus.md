# **ShutDown/StartUp Prod Blue Tasks**
    POST /stacks/prodblueStatus

## **Description**
- This API call shuts down or starts up tasks for the prod-blue environment
- It returns 200 if the tasks are been stopped/started
- It returns 400 if the parameters are missing or invalid

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application name for which the tasks needs to be stopped/started
- **environment** _(required)_
   - This will be the environment for which the tasks needs to be stopped/started
- **action** _(required)_
   - This will be the type of action that needs to be performed on tasks. Valid values: stop/start
***

## **Response**
### Success
- **200**
   - **message**
      - The Tasks for given application and environment has been stopped/started
### Error
- **400**
  - **errorMessage**
    - Parameter is not present
    - Parameter cannot be empty	

***
## **Example**
### Request
POST https://yourcustomdevopsdomain.com/stacks/prodblueStatus
Body:
``` json
{
	"applicationName": "MyDevOpsAPI",
	"action": "stop"
}
```
### Response
``` json
{
    "message": "Environment MyDevOpsAPI-prod1 for Application MyDevOpsAPI is been Stopped"
}
```