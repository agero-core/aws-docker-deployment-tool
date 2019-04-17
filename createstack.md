# **Create Stack**
    POST /stacks

## **Description**
- This API call creates application stack for development
- It returns 200 if the stack creation has initiated
- It returns 400 if the parameters are missing or invalid
- It returns 409 if stack with similar name already exists

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application & stack name of the application and it has to be a unique string
   - It can contain upper/lower case alphabets and numbers
- **description** _(optional)_
   - This will be the description of application that needs to be created
   - It needs to be string
 - **email** _(required)_
   - This parameter will contain email of team to which the application will belong to
   - This email might be used for notification purpose
   - It needs to be a string 
 - **environments** _(required)_
   - This parameter will be a list of strings containing the environments to be deployed
     - **training** _(required)_
       - This parameter value needs to be boolean 
       - Values: true or false
     - **da** _(required)_
       - This parameter value needs to be boolean 
       - Values: true or false  
 - **tags** _(required)_
   - This will be a object containing required tags
     - **ageroService** _(required)_
     - **tier** _(required)_
     - **complianceType** _(required)_
     - **technicalTeam** _(required)_
     - **businessTeam** _(required)_
     - **classificationLabel** _(required)_
***
## **Response**
### Success
- **200**
   - **message**
      - The parameter message displays "Stack Creation Initiated" message
   - **application**
     - The name of the application
   - **ecrName**
     - The Elastic Compute Registory name it creates for the application
   - **technicalTeam**
     - The technical team name to which the application belongs
   - **email**
     - The email of the team
   - **environmentType**
     - The list of the environments with their URL that are been created
### Error
- **400**
  - **errorMessage**
    - The value contains the message in case some values of the object body are invalid or null
- **409**
  - **errorMessage**
    - The value contains the message in case application is already created with the same name

***
## **Example**
### Request
POST https://yourcustomdevopsdomain.com/stacks
Body:
``` json
{  
   "applicationName":"MyDevOpsAPI",
   "description": "DevOps Testing API",
   "email":"team@company.com",
   "environments":{  
      "training":false,
      "da":false
   },
   "tags":{  
      "ageroService": "OneRoad",
      "tier": "Tier1",
      "complianceType": "Type1",
      "technicalTeam": "CoreApiServices",
      "businessTeam": "CoreAutomation",
      "classificationLabel": "Confidential/Level2"
   }
}
```
### Response
``` json
{
    "technicalTeam": "CoreApiServices",
    "ecrName": "mydevopsapi",
    "application": "MyDevOpsAPI",
    "message": "Stack Creation Started for MyDevOpsAPI",
    "environmentType": [
        {
            "Endpoint": "MydevOpsAPI.dkr.dev.hostedzonename.",
            "DEV": "YES"
        },
        {
            "Endpoint": "MydevOpsAPI.dkr.qa.hostedzonename.",
            "QA": "YES"
        },
        {
            "Endpoint": "MydevOpsAPI.dkr.stage.hostedzonename.",
            "STAGE": "YES"
        },
        {
            "Endpoint": "MydevOpsAPI.dkr.prod.hostedzonename.",
            "PROD": "YES"
        },
        {
            "Endpoint": "MydevOpsAPI.dkr.training.hostedzonename.",
            "TRAINING": "NO"
        },
        {
            "Endpoint": "MydevOpsAPI.dkr.da.hostedzonename.",
            "DA": "NO"
        }
    ],
    "email": "team@company.com"
}
```