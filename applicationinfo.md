# **Add Additional Subscriptions**
    POST /stacks/applicationInfo

## **Description**
- This API call returns information regarding the application, environments, version, and so on
- It returns 200 if the application exists and call is made correctly
- It returns 400 if the parameters are missing or invalid

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application name to which the subscription needs to be added
***

## **Response**
### Success
- **200**
   - **message**
      - Returns list of environments and related information regading the application
### Error
- **400**
  - **errorMessage**
    - Parameter is not present
    - Parameter cannot be empty	

***
## **Example**
### Request
POST https://yourcustomdevopsdomain.com/stacks/applicationInfo
Body:
``` json
{
	"applicationName": "ECSDemoAPI",
}
```
### Response
``` json
[
    {
        "applicationName": "ECSDemoAPI",
        "url": "https://ECSDemoAPI.dkr.dev.aut-nonprod.corppvt.cloud",
        "techTeam": "TechTeam",
        "environment": "DEV",
        "version": "1.0.0.6",
        "time": "2019-06-20 18:48:09.661999"
    },
    {
        "applicationName": "ECSDemoAPI",
        "url": "https://ECSDemoAPI.dkr.qa.aut-nonprod.corppvt.cloud",
        "techTeam": "TechTeam",
        "environment": "QA",
        "version": "0.0.0.0",
        "time": "2019-06-20 17:20:47.719049"
    },
    {
        "applicationName": "ECSDemoAPI",
        "url": "https://ECSDemoAPI.dkr.stage.aut-nonprod.corppvt.cloud",
        "techTeam": "TechTeam",
        "environment": "STAGE",
        "version": "1.0.0.6",
        "time": "2019-06-20 18:48:10.083572"
    },
    {
        "applicationName": "ECSDemoAPI",
        "url": "https://ECSDemoAPI.dkr.prod.aut-prod.corppvt.cloud",
        "techTeam": "TechTeam",
        "environment": "PROD1",
        "version": "1.0.0.6",
        "time": "2019-06-20 19:11:57.469406"
    },
    {
        "applicationName": "ECSDemoAPI",
        "url": "https://ECSDemoAPI.dkr.prod-blue.aut-prod.corppvt.cloud",
        "techTeam": "TechTeam",
        "environment": "PROD2",
        "version": "0.0.0.0",
        "time": "2019-06-20 19:11:57.469406"
    }
]
```