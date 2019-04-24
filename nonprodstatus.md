# **ShutDown/StartUp NonProd Tasks**
    POST /stacks/nonprodStatus

## **Description**
- This API call shuts down or starts up tasks of the nonprod environments
- It returns 200 if the tasks are been stopped
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
POST https://yourcustomdevopsdomain.com/stacks/nonprodStatus
Body:
``` json
{
	"applicationName": "MyDevOpsAPI",
	"environment": "dev",
	"action": "stop"
}
```
### Response
``` json
{
    "message": "Environment MyDevOpsAPI-dev for Application MyDevOpsAPI is been Stopped"
}
```