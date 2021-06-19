# AWS CodeBuild GitHub action

|Name|Badge|
|:-:|:-:|
|Checks, linters and formatters|[![Checks, linters and formatters](https://github.com/neovasili/aws-codebuild/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/neovasili/aws-codebuild/actions/workflows/pre-commit.yml)|
|Quality|[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=neovasili_aws-codebuild&metric=alert_status)](https://sonarcloud.io/dashboard?id=neovasili_aws-codebuild)|

This repository contains a GitHub action to invoke and integrate CodeBuild as part of a GitHub workflow with advanced features, like override environment image or passthrough source code using a S3 bucket, thus making your CodeBuild projects more reusable and agnostic to the git repository.

Here you can see the [project roadmap](https://github.com/neovasili/aws-codebuild/projects/1) for this GitHub action.

- [AWS CodeBuild GitHub action](#aws-codebuild-github-action)
  - [Motivation](#motivation)
  - [Quick Start](#quick-start)
    - [Minimal permissions](#minimal-permissions)
    - [Setup your github workflow](#setup-your-github-workflow)
  - [Features](#features)
  - [References](#references)

## Motivation

Why this CodeBuild GitHub action if there is already an official one by AWS? There are two main motivations:

- I already have it done and working since a while for private purposes, so I decided to "formalize" it and publish it.
- Reusability of CodeBuild projects. There are several parameters that can be overridden in runtime that gives you a lot of flexibility and reusability of your CodeBuild projects with minimal effort. This GitHub Action is focused on it.

## Quick Start

This section will cover minimal usage of this action with no optional extra features; thus essentially, ability to call a CodeBuild project from GitHub actions and see log events from CodeBuild in GitHub actions logs.

Unless you setup your CodeBuild project source from the repository, **this action will not pass your repository code automatically to CodeBuild** with this minimal setup.

### Minimal permissions

You will need to create an IAM user with the following minimum set of permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "codebuild:StartBuild",
                "codebuild:BatchGetBuilds"
            ],
            "Resource": [
                "YOUR_CODEBUILD_PROJECT_ARN"
            ],
            "Effect": "Allow"
        },
        {
            "Action": "logs:GetLogEvents",
            "Resource": [
                "YOUR_CODEBUILD_PROJECT_LOG_GROUP_ARN"
            ],
            "Effect": "Allow"
        }
    ]
}
```

Once you created it, it's recommended to store user AccessKey and AccessSecretKey as [GitHub secrets](https://docs.github.com/es/actions/reference/encrypted-secrets) to further use in the workflow.

### Setup your github workflow

You need to create a GitHub workflow yaml with this minimal content:

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
```

As you can see, you need to first setup IAM credentials to be able to run the action against AWS resources.

There are also three mandatory parameters to setup:

- `aws_region`: The AWS region you are going to use, where your CodeBuild project is located
- `codebuild_job_name`: The name of your CodeBuild project
- `codebuild_log_group`: The name of your CodeBuild project log group

## Features

As mentioned before, the minimal setup of this action will let you:

- Run a CodeBuild project from a GitHub workflow
- See logs from CodeBuild in the GitHub workflow logs

Nevertheless, as mentioned before, this action is intended mainly for reusability of CodeBuild projects with minimal effort, so it also implements some extra really useful features:

- [Source code from S3](./docs/s3_source.md)
- [Image override](./docs/image_override.md)
- [Buildspec override](./docs/buildspec_override.md)
- [Custom environment variables](./docs/custom_environment_variables.md)

## References

- [S3 objects lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [ECR images lifecycle](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html)
- [ECR cross account permissions](https://docs.amazonaws.cn/en_us/AmazonECR/latest/userguide/repository-policy-examples.html#IAM_allow_other_accounts)
- [CodeBuild buildspec](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)
- [CodeBuild environment variables](https://docs.aws.amazon.com/codebuild/latest/APIReference/API_EnvironmentVariable.html)
- [CodeBuild environment variables secrets](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager)
- [CodeBuild environment SSM parameter](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.parameter-store)
- [Boto3 CodeBuild reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.start_build)
- [AWS official CodeBuild action](https://github.com/aws-actions/aws-codebuild-run-build)
