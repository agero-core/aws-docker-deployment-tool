# **Delete Stack**
    DELETE /dev/stacks

## **Description**
- This API call deletes application stack that was been deployed
- It returns 200 if the stack deletion has initiated
- It returns 400 if the parameters are missing or invalid
- It returns 409 if stack does not exists

***
## **Parameters**
- **stack** _(required)_
   - This will be the application name that has been deployed
***
## **Response**
### Success
- **200**
   - **message**
      - The parameter message displays "Stack Deletion Initiated" message
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
DELETE https://<api-generated>.execute-api.us-east-1.amazonaws.com/dev/stacks
Body:
``` json
{
	"stack": "MyDevOpsAPI"
}
```
### Response
``` json
{
    "message": "Stack MyDevOpsAPI has been deleted"
}
```