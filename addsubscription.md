# **Add Additional Subscriptions**
    POST /stacks/addSubscription

## **Description**
- This API call adds additional subscription to SNS topics of the environments
- It returns 200 if the subscription is added successfully
- It returns 400 if the parameters are missing or invalid

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application name to which the subscription needs to be added
- **environments** _(required)_
   - This will be the list of environments to which the subscription needs to be added
- **protocol** _(required)_
   - This will be the protocol that needs to be added as subscription
- **endpoint** _(required)_
   - This will be the endpoint to which the notification needs to be sent
***

## **Response**
### Success
- **200**
   - **message**
      - The Subscription has been added
### Error
- **400**
  - **errorMessage**
    - Parameter is not present
    - Parameter cannot be empty	

***
## **Example**
### Request
POST https://yourcustomdevopsdomain.com/stacks/addSubscription
Body:
``` json
{
	"applicationName": "MyDevOpsAPI",
	"environments": ["dev","qa","stage","prod"],
	"protocol": "email",
	"endpoint": "myemail@company.com"
}
```
### Response
``` json
{
    "message": "The Subscription has been added"
}
```