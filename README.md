# **DevOps Model for ECS Fargate**

- This DevOps model for ECS Fargate is API driven.
- It will provision DevOps resources in AWS using serverless template and parameters file which will contain all the information related to AWS accounts (NonProd and Prod), VPC, subnets, and so on.
- There will be an additional SharedAccount for which one needs to create 3 different Dynamo Tables for application inventory. A cross account role needs to be created for that.
- The serverless template will give some APIs to carry out different operations related to stack creation, deployments, and deleting stacks.
- This functionality provides APIs to make calls to and perform stack creation, deploy image to non production servers in non production account, productions servers with blue/green functionality along with training/da environments in production account, swap blue/green environments
and delete the stack for any application.

***

## **Requirements**

To run this successfully the system will require to have python and serverless installed along with an AWS account.

***

## **Getting Started**

- Edit parameters.yml file
```
#parameters.yml
#parameters.yml
apiname: <api-name>
stage: <dev/qa/stage/prod>
nonprod_accountid: <NonProdAccountId>
prod_accountid: <ProdAccountId>
devqa_vpc: <devqa-vpc>
stage_vpc: <stage-vpc>
training_vpc: <training-vpc>
da_vpc: <da-vpc>
prod_vpc: <production-vpc>
devqa_subnet: <devqa-container-subnets>
stage_subnet: <stage-container-subnets>
training_subnet: <training-container-subnets>
da_subnet: <da-container-subnets>
prod_subnet: <prod-container-subnets>
devqa_elbsubnet: <devqa-elb-subnets>
stage_elbsubnet: <stage-elb-subnets>
training_elbsubnet: <training-elb-subnets>
da_elbsubnet: <da-elb-subnets>
prod_elbsubnet: <prod-elb-subnet>
devqa_sg: <devqa-sg>
stage_sg: <stage-sg>
training_sg: <training-sg>
da_sg: <da-sg>
prod_sg: <prod-sg>
devqa_elbsg: <devqa-elb-sg>
stage_elbsg: <stage-elb-sg>
training_elbsg: <training-elb-sg>
da_elbsg: <da-elb-sg>
prod_elbsg: <prod-elb-sg>
region: us-east-1
repouri: <repo-uri-sample-image>
ecscftemplatebucket: <bucket-for-storing-cf-template>
cftemplate: <url-for-cf-template>
hostedzonename: <hostedzonename-NonProdAccount>
prodhostedzonename: <hostedzonename-ProdAccount>
admin_rolearn: <admin-rolearn-for-cloudformation-stack>
execution_rolename: <execution_rolename>
stsrolearn: <stsrolearn>
stsrole_prod: <stsrole_prod>
nonprod_certarn: <Certificate Manager ARN to be used in ALBs>
prod_certarn: <Certificate Manager ARN to be used in ALBs>
ecsautoscaling_arn: <IAM Role ARN for ECS AutoScaling - NonProd Account>
prod_ecsautoscaling_arn: <IAM Role ARN for ECS AutoScaling - Prod Account>
admin_sso_role_arn: <Administrator User SSO Role>
poweruser_sso_role_arn: <PowerUser SSO Role>
dev1_sso_role_arn: <Dev1 User SSO Role>
dev2_sso_role_arn: <Dev2 User SSO Role>
dev3_sso_role_arn: <Dev3 User SSO Role>
customDomain:
  domainName: <Custom Domain Name>
  stage: <API Gateway Stage Name>
  basePath:
  certificateName: <Name of the Certificate associated with custom domain>
  createRoute53Record: true
  endpointType: <regional/edge>


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
 5. deploy to training/da environments
 6. add additional notification subscriptions to SNS
 7. shutdown nonprod tasks when not needed
 8. shutdown prod blue tasks when not needed
 9. find out devopsstack version deployed
 10. delete stack
 
 ***

## **Endpoints & Back-End Lambda Functions**
### **Developer Endpoints**
 * [POST /stacks](createstack.md)
 * [POST /stacks/deploytoNonProd](deploytononprod.md)
 * [POST /stacks/deploytoProdBlue](deploytoprodblue.md)
 * [POST /stacks/swapProdBlueAndGreen](swapbluegreen.md)
 * [POST /stacks/deploytoTrainDA](deploytotrainda.md)
 * [POST /stacks/addSubscription](addsubscription.md)
 * [POST /stacks/nonprodStatus](nonprodstatus.md)
 * [POST /stacks/prodblueStatus](prodbluestatus.md) 
 * [DELETE /stacks](deletestack.md)

***

## **Additional Resources**
### **ECR Repository**
- The purpose of this Repository is to store an sample image for the initial creation of the stack.

### **Cluster**
- A DevOps Cluster that can be used to launch ECS Service for the sample image

### **S3 Buckets**
- ECS-CF-Bucket
  - This bucket is used to store CloudFormation Template that is used to deploy developer resources
  - In future it can also store custom templates based on different applications