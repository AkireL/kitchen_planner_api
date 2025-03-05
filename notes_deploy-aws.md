## Create LAMBDA AWS

Key data.

| Variable             | Description                                                        | Value                                |
| -------------------- | ------------------------------------------------------------------ | ------------------------------------ |
| REPOSITORY_NAME      | Nombre del repositorio en ECR.                                     | "fastapi-demo"                       |
| AWS_ACCOUNT_ID       | el ID del usuario                                                  | -                                    |
| function-name        | nombre de la función lambda                                        | "kitchen-planner-api-lambda"         |
| ROLE_NAME            | El valor del rol para crear la lambda                              | "kitcher_planner_lambda              |
| LAMBDA_FUNCTION_NAME | NOmbre de la lambda                                                | kitchen-planner-api-lambda           |
| REGION               | La región                                                          | us-east-1                            |
| API_NAME             | Nombre de la API GATEWAY                                           | kitchen-planner-api                  |
| UNIQUE_STATEMENT_ID  | -                                                                  | apigateway-kitchen-invoke-permission |
| API_ID               | Este valor se obtiene del punto 1 de la creación de la api gateway | kjtpujf0f8                           |
| INTEGRATION_ID       | Id de la integración entre API Gateway y Lambda                    | 4qj4syp                              |

### Steps

1. Install AWS.
2. Set up, aws configure then look like this:

> ####
>
> - AWS Access Key ID [None]: xxxxxxx
> - AWS Secret Access Key [None]: xxxxxx/xxxxxxxxx
> - Default region name [None]: us-east-1
> - Default output format [None]: json

3. Create docker image of your app.

```bash
docker build -f Dockerfile.aws -t fastapi-demo .
```

4. When we use docker we need create a repository in ECR for first time.

```bash
aws ecr create-repository --repository-name fastapi-demo --region us-east-1
```

If after run above line suddenly show this error then you need ask the right access.

> An error occurred (AccessDeniedException) when calling the CreateRepository operation: User: arn:aws:iam::782101734068:user/mvk_demo is not authorized to perform: ecr:CreateRepository on resource: arn:aws:ecr:us-east-1:782101734068:repository/fastapi-demo because no identity-based policy allows the ecr:CreateRepository action

5. Review if the AWS User is authenticated

```bash
aws sts get-caller-identity
```

6. Log in in ECR.

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

Note:
--username AWS: Forever this user is AWS because ECR use AWS as user name when it use docker.

7. Tag the created image on the 3 point.

```bash
docker tag fastapi-demo:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-demo:latest
```

8. Push the docker imagen to ECR.

```bash
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-demo:latest
```

9. Validate that imagen is uploaded to AWS ECR.

```bash
aws ecr describe-images --repository-name <REPOSITORY_NAME> --region <REGION>
```

10. Before create lambda ask a role to administrator.
11. Then create the lambda.

```bash
aws lambda create-function \
 --function-name fastapi-demo \
 --package-type Image \
 --code ImageUri=<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/<REPOSITORY_NAME>:latest \
 --role arn:aws:iam::<AWS_ACCOUNT_ID>:role/<ROLE_NAME>
```

## Set up API GATEWAY

1. Create Api gateway.

```bash
aws apigatewayv2 create-api \
  --name <API_NAME> \
  --protocol-type HTTP \
  --target arn:aws:lambda:<REGION>:<AWS_ACCOUNT_ID>:function:<LAMBDA_FUNCTION_NAME>
```

Save the ApiId value from the result of this step because it is required in the following steps.

For this step, it is very important to check if the user does not have the role and request that the 'AmazonAPIGatewayAdministrator' role be assigned to them.

2. Allow the API Gateway to invoke the Lambda function.

```bash
aws lambda add-permission \
  --function-name <LAMBDA_FUNCTION_NAME> \
  --principal apigateway.amazonaws.com \
  --statement-id <UNIQUE_STATEMENT_ID> \
  --action "lambda:InvokeFunction"
```

**<UNIQUE_STATEMENT_ID>**: A unique identifier for this permission (you can use something like **apigateway-invoke-permission**).

3. Obtain the public URL of the API.

```bash
aws apigatewayv2 get-api \
  --api-id <API_ID>
```

The result of this step will be displayed like this.

```
{
    "ApiEndpoint": "https://kjtpujf0f8.execute-api.us-east-1.amazonaws.com",
    "ApiId": "kjtpujf0f8",
    "ApiKeySelectionExpression": "$request.header.x-api-key",
    "CreatedDate": "2025-02-28T23:49:34+00:00",
    "DisableExecuteApiEndpoint": false,
    "Name": "kitchen-planner-api",
    "ProtocolType": "HTTP",
    "RouteSelectionExpression": "$request.method $request.path",
    "Tags": {}
}
```

4. Create integration between API Gateway and lambda.

```bash
aws apigatewayv2 create-integration \
  --api-id <API_ID> \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:<REGION>:<ACCOUNT_ID>:function:<LAMBDA_FUNCTION_NAME> \
  --payload-format-version "2.0"
```

Note:
Save the value (IntegrationId) because it is required in the next step.

5. Register the routes in the API GATEWAY.

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "POST /register" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "POST /token" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "GET /Users/me" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "GET /recipes" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "POST /recipes" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "PUT /recipes/{id}" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "DELETE /recipes/{id}" \
  --target "integrations/4qj4syp"
```

```bash
aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "GET /docs" \
  --target "integrations/4qj4syp"
```

6. Deploy api gateway.

```bash
aws apigatewayv2 create-deployment \
  --api-id <API_ID> \
  --stage-name <STAGE_NAME>
```

## Create database

Ask the administrator to create the database with your credentials and create the tables. Finally, the administrator will provide you with the host and port.

## Connect database with lambda

Ask the administrator to create a proxy to connect the database and Lambda.
