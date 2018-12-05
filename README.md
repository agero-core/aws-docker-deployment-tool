# **DevOps Model for ECS Fargate**

- This DevOps model for ECS Fargate is API driven.
- It will provision DevOps resources in AWS using serverless template and parameters file which will contain all the information related to AWS account, VPC, subnets, and so on.
- The serverless template will give some APIs to carry out different operations related to stack creation, deployments, and deleting stacks.
- This functionality provides APIs to make calls to and perform stack creation, deploy image to non production servers, productions servers with blue/green functionality along with training/da environments, swap blue/green environments
and delete the stack for any application.

***

## **Requirements**

To run this successfully the system will require to have python and serverless installed along with an AWS account.

***

## **Getting Started**

- Edit parameters.yml file
```
#parameters.yml
apiname: <devops-demo>
stage: <stage-name>
accountid: <aws account-id>
vpc: <vpc id>
subnet1: <subnet-id1>
subnet2: <subnet-id2>
elbsubnet1: <alb-subnet-id1>
elbsubnet2: <alb-subnet-id2>
sg: <security-group-id>
elbsg: <alb-security-group-id>
region: <aws-region>
repouri: <default-repo-uri>
cftemplate: <s3-url-for-cloudformationtemplate>
```
- Run this command to deploy Serverless Architecture for DevOps

```sh
$ serverless deploy
```
- The output of serverless will look something like this

```
service: <resource-name>
stage: <stage-deployed>
region: <aws-region-name>
stack: <cloudformation-stack-name>
api keys:
    None
endpoints:
 <METHOD> <API from API Gateway>
 <METHOD> <API from API Gateway>
 <METHOD> <API from API Gateway>
functions:
 <lambda_function>: <stackname-lambdafunction>
 <lambda_function>: <stackname-lambdafunction>
 <lambda_function>: <stackname-lambdafunction>
```
- Make note of endpoints as this will be used to make RESTful API calls 
- These APIs can be used by developers to make following operations:
 1. create stack
 2. deploy image to non-production environments
 3. deploy image to production blue environment
 4. swap blue and green environment 
 5. delete stack
 
 ***

## **Endpoints & Back-End Lambda Functions**
### **Developer Endpoints**
 * [POST /dev/stacks](createstack.md)
 * [POST /dev/stacks/deploy](deploytononprod.md)
 * [POST /dev/stacks/deploytoprodBlue](deploytoprodblue.md)
 * [POST /dev/stacks/swapProdBlueAndGreen](swapbluegreen.md)
 * [DELETE /dev/stacks](deletestack.md)

***

## **Additional Resources**
### **S3 Buckets**
- ECS-Bucket
  - The purpose of this bucket is preserved for future developments like storing images
- ECS-CF-Bucket
  - This bucket is used to store CloudFormation Template that is used to deploy developer resources
  - In future it can also store custom templates based on different applications

### **Dynamo Tables**
 - ECS_Inventory_NonProduction
   - The dyanmo table keeps records of all the new application and their non production environments been deployed.
   - It dynamically also removes the records once the application is removed from the stack
 - ECS_Inventory_Production
   - The dyanmo table keeps records of all the new application and their blue & green production environments been deployed.
   - It dynamically also removes the records once the application is removed from the stack
  - ECS_Inventory_TrainingDA
    - The dyanmo table keeps records of all the new application and their training and da environments been deployed.
    - It dynamically also removes the records once the application is removed from the stack
 - DevOpsLogsTable
   - This table keeps track of all the devops events that are been called whenever a stack is created, application been deployed to various environments, swap between production blue and green, and whenever any resource is terminated.
***