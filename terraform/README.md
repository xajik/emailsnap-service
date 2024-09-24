# Infrastructure 

## Use

1. `terraform fmt`
2. `terraform validate`
3. `terraform plan`
4. `terraform apply`

## State

We manage state on the Gitlab:

```
export GITLAB_ACCESS_TOKEN=<YOUR-ACCESS-TOKEN>
terraform init \
    -backend-config="address=https://gitlab.com/api/v4/projects/<PROJECT_ID>/terraform/state/default" \
    -backend-config="lock_address=https://gitlab.com/api/v4/projects/<PROJECT_ID>/terraform/state/default/lock" \
    -backend-config="unlock_address=https://gitlab.com/api/v4/projects/<PROJECT_ID>/terraform/state/default/lock" \
    -backend-config="username=<USER_NAME>" \
    -backend-config="password=$GITLAB_ACCESS_TOKEN" \
    -backend-config="lock_method=POST" \
    -backend-config="unlock_method=DELETE" \
    -backend-config="retry_wait_min=5"
```

## TF Lock 

Profide lock for Mac for local developemtn and linux for remote

* terraform providers lock \
    -platform=darwin_amd64 \
    -platform=linux_amd64 \
    -platform=darwin_arm64 \
    -platform=linux_arm64

## Troubleshooting 

On the first run it will fail to attach a certificate to Cloudfront. Please go to the console and do DNS verification with your host provider.

## RDS

* Find available engines
    * `aws rds describe-db-engine-versions --engine aurora-mysql --filters Name=engine-mode,Values=serverless --output text --query "DBEngineVersions[].EngineVersion"`