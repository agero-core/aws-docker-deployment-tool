# **Swap Production Blue/Green Environments for West Region**
    POST /stacks/swapProdWestBlueAndGreen

## **Description**
- This API call swaps production blue & green environments in west region
- This way the latest version deployed to blue now will be in the live(green) environment
- This feature helps with easy rollback by switching back blue/green environment
- It returns 200 if the swap is completed
- It returns 400 if the parameters are missing or invalid
- It returns 409 if stack does not exists

***
## **Parameters**
- **applicationName** _(required)_
   - This will be the application name for which blue/green environments needs to be swapped
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
POST https://yourcustomdevopsdomain.com/stacks/swapProdWestBlueAndGreen
Body:
``` json
{
	"applicationName": "MyDevOpsAPI"
}
```
### Response
``` json
{
    "message": "Prod Blue/Green Swap Completed Successfully for MyDevOpsAPI in West Region"
}
```