Create LAMBDAS AWS

Key data

| Variable        | Description                           | Value                        |
| --------------- | ------------------------------------- | ---------------------------- |
| REPOSITORY_NAME | Nombre del repositorio en ECR.        | "fastapi-demo"               |
| AWS_ACCOUNT_ID  | el ID del usuario                     | -                            |
| function-name   | nombre de la función lambda           | "kitchen-planner-api-lambda" |
| ROLE_NAME       | El valor del rol para crear la lambda | "kitcher_planner_lambda      |
|LAMBDA_FUNCTION_NAME|NOmbre de la lambda|kitchen-planner-api-lambda|
|REGION|La región|us-east-1|
|API_NAME|Nombre de la API GATEWAY| kitchen-planner-api|
|UNIQUE_STATEMENT_ID|-|apigateway-kitchen-invoke-permission|
|API_ID| Este valor se obtiene del punto 1 de la creación de la api gateway| kjtpujf0f8|

|INTEGRATION_ID|Id de la integración entre API Gateway y Lambda|4qj4syp|

Steps
1.  Install AWS
2.  Set up
 > aws configure
    then look like this:

        AWS Access Key ID [None]: <aqui el ID>
        AWS Secret Access Key [None]: xxxxxx/xxxxxxxxx
        Default region name [None]: us-east-1
        Default output format [None]: json

3.  Create docker image of your app

    > docker build -f Dockerfile.aws -t fastapi-demo .

4.  When we use docker we need create a repository in ECR for first time.

        > aws ecr create-repository --repository-name fastapi-demo --region us-east-1

if after run above line suddenly show this error then you need ask the right access.

An error occurred (AccessDeniedException) when calling the CreateRepository operation: User: arn:aws:iam::782101734068:user/mvk_demo is not authorized to perform: ecr:CreateRepository on resource: arn:aws:ecr:us-east-1:782101734068:repository/fastapi-demo because no identity-based policy allows the ecr:CreateRepository action


5. Review if the AWS User is authenticated

   > aws sts get-caller-identity

6. Log in in ECR.
   > aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

Note:
--username AWS: Forever this user is AWS because ECR use AWS as user name when it use docker.

7. Tag the created image on the 3 point.

docker tag fastapi-demo:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-demo:latest

8. Push the docker imagen to ECR.

   docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-demo:latest

9. Validate that imagen is uploaded to AWS ECR.

   aws ecr describe-images --repository-name <REPOSITORY_NAME> --region <REGION>

10. Before create lambda ask a role

11. Then create the lambda

aws lambda create-function \
 --function-name fastapi-demo \
 --package-type Image \
 --code ImageUri=<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/<REPOSITORY_NAME>:latest \
 --role arn:aws:iam::<AWS_ACCOUNT_ID>:role/<ROLE_NAME>


Set up API GATEWAY

1. Create Api gateway

aws apigatewayv2 create-api \
  --name <API_NAME> \
  --protocol-type HTTP \
  --target arn:aws:lambda:<REGION>:<AWS_ACCOUNT_ID>:function:<LAMBDA_FUNCTION_NAME>
Aqui hay que guardar el valor de la propiedad ApiId porque en los puntos siguientes se requiere.

API_NAME: El nombre que quieres darle a tu API (por ejemplo, fastapi-api).
REGION: La región donde se encuentra tu Lambda (por ejemplo, us-east-1).
AWS_ACCOUNT_ID: El ID de tu cuenta de AWS.
LAMBDA_FUNCTION_NAME: El nombre de tu función Lambda (por ejemplo, fastapi-demo).


Si el usuario no tiene el rol pedir que le asignen el rol "AmazonAPIGatewayAdministrator".

2. Permitir que el API GATEWAY invoque la función lambda

aws lambda add-permission \
  --function-name <LAMBDA_FUNCTION_NAME> \
  --principal apigateway.amazonaws.com \
  --statement-id <UNIQUE_STATEMENT_ID> \
  --action "lambda:InvokeFunction"

  <LAMBDA_FUNCTION_NAME>: El nombre de tu función Lambda (por ejemplo, fastapi-demo).
<UNIQUE_STATEMENT_ID>: Un identificador único para este permiso (puedes usar algo como apigateway-invoke-permission).

3. Obtener la url publica de la API

aws apigatewayv2 get-api \
  --api-id <API_ID>

  Aqui nos da los siguientes datos
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

4. Create integration between API Gateway y lambda

aws apigatewayv2 create-integration \
  --api-id <API_ID> \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:<REGION>:<ACCOUNT_ID>:function:<LAMBDA_FUNCTION_NAME> \
  --payload-format-version "2.0"

Los guardar el valor (IntegrationId) porque en el siguiente punto se requiere.

5. Agregar los endpoints al gapiateway

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "POST /register" \
  --target "integrations/4qj4syp"

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "POST /token" \
  --target "integrations/4qj4syp"

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "GET /Users/me" \
  --target "integrations/4qj4syp"

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "GET /recipes" \
  --target "integrations/4qj4syp"

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "POST /recipes" \
  --target "integrations/4qj4syp"

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "PUT /recipes/{id}" \
  --target "integrations/4qj4syp"

aws apigatewayv2 create-route \
  --api-id kjtpujf0f8 \
  --route-key "DELETE /recipes/{id}" \
  --target "integrations/4qj4syp"


6. Desplegar la apigateway

aws apigatewayv2 create-deployment \
  --api-id <API_ID> \
  --stage-name <STAGE_NAME>