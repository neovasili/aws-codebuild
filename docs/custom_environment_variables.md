# Custom environment variables

&#x2B11; [Return to index](../README.md)

- [Custom environment variables](#custom-environment-variables)
  - [How it works](#how-it-works)
  - [Configuration](#configuration)

CodeBuild let's you specify environment variables to pass to the agent in several ways. Those can be defined on CodeBuild project provisioning time as well as on runtime. They are very useful to parametrize your builds in many ways.

There are three types of environment variables in the CodeBuild context:

- **PLAINTEXT**: as simple as it seems, environment variables containing plain text; be careful to not expose there any sensible information
- **PARAMETER_STORE**: the value for the environment variable will be retrieved from an existing SSM parameter
- **SECRETS_MANAGER**: the value for the environment variable will be retrieved from an existing sercret

This feature will allow you to provide any of them to your CodeBuild project using this action.

Please, consider that if you specify any of `PARAMETER_STORE` or `SECRETS_MANAGER`, your CodeBuild project needs permissions to read those SSM parameters and/or secrets.

## How it works

When this feature is enabled and properly configured will work following these steps:

- Reads environment variables specified in the GitHub workflow for the action execution
  - If the environment variable name starts with `PLAINTEXT_`, it will be injected as a PLAINTEXT environment variable
  - If the environment variable name starts with `SSM_`, it will be injected as a PARAMETER_STORE environment variable
  - If the environment variable name starts with `SECRET_`, it will be injected as a SECRETS_MANAGER environment variable
- Invokes CodeBuild project passing default environment plus any other custom one defined like indicated in previous step

## Configuration

Last step is to let the GitHub workflow know where it needs to upload the code configuring the GitHub workflows native environment variables:

```yaml
---
name: "Test CodeBuild action"

jobs:
  test-codebuild-action:
    steps:

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.YOUR_IAM_USER_ACCESS_KEY_SECRET_NAME }}
          aws-secret-access-key: ${{ secrets.YOUR_IAM_USER_ACCESS_SECRET_KEY_SECRET_NAME }}
          aws-region: AWS_REGION_YOUR_GOING_TO_USE

      - name: Run CodeBuild
        uses: neovasili/aws-codebuild@v1.0.0
        with:
          aws_region: AWS_REGION_YOUR_GOING_TO_USE
          codebuild_job_name: YOUR_CODEBUILD_PROJECT_NAME
          codebuild_log_group: YOUR_CODEBUILD_PROJECT_LOG_GROUP_NAME
        env:
          PLAINTEXT_AWS_ACCOUNT_ID: MY_CUSTOM_ACCOUNT_PARAMETER
          SSM_AWS_ACCOUNT_ID: /MY/CUSTOM/ACCOUNT/PARAMETER
          SECRET_AWS_ACCOUNT_ID: /MY/CUSTOM/SECRET/ACCOUNT/PARAMETER
```
