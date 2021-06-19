# Image override

&#x2B11; [Return to index](../README.md)

- [Image override](#image-override)
  - [How it works](#how-it-works)
  - [Additional AWS resources needed](#additional-aws-resources-needed)
  - [Permissions](#permissions)
  - [Configuration](#configuration)

Another very interesting feature that CodeBuild has, is the ability to change the underlying docker image that's is going to be used by the CodeBuild agent to perform you build actions in runtime. That allows you, for example, build snapshots of your source code and dependencies in docker images and use CodeBuild for Continuous Deployment purposes passing different versions of you code snapshot according to you needs in the same process/pipeline.

However, one important concern is to not let anybody push any docker image to our CodeBuild project, as that constitutes a potential security issue.

Nevertheless, this action implements an approach using an SSM parameter to build the complete image uri using the value stored there, so only the GitHub IAM user created will have permissions to read it to only push images to override according to what have previously stored there, and not any image.

## How it works

When this feature is enabled and properly configured will work following these steps:

- Reads the configured SSM parameter (provided by the `override_image_ssm_base` input) to obtain the docker image repository URI
- Concatenates the retrieved repository URI with the desired tag; can be configured in several ways:
  - You can specify directly which tag to use using the `override_image_tag` input
  - You can specify a tag prefix with the `override_image_tag_prefix` input; this input is overridden by hte previous one if it's provided
  - If you don't specify any of the previous inputs, it will use the current commit hash id for commit pushes and the current tag name for tag pushes
- Invokes CodeBuild project overriding the image using the full URI built in the previous step

The input `override_image_tag_prefix` is very useful for temporary images created for CI purposes, for example if you are using ECR, you can use a `ci` prefix that will produce `ci_COMMIT_HASH_ID` images tagged and at the same time you can specify an [images expiry policy](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html) filtering by tag prefix, so you don't keep CI temporary images in the ECR repository for too long.

## Additional AWS resources needed

In this case, you will need to have at least one SSM parameter containing the image repository URI. For example, if you are using a private ECR repository to store the image, your SSM parameter should contain something like this: `AWS_ACCOUNT_ID.dkr.ecr.AWS_REGION.amazonaws.com/REPOSITORY_NAME`.

In the case you want to use ECR, you obviously will also need to have that repository beforehand and have the images to use there.

## Permissions

To be able to read the SSM parameter, you need to add the following permissions to the [IAM user created for GitHub action](../README.md#minimal-permissions):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "ssm:GetParameter"
            ],
            "Resource": [
                "YOUR_SSM_PARAMETER_ARN"
            ],
            "Effect": "Allow"
        }
    ]
}
```

In the case you want to use ECR, you also need to add the following parameters to your CodeBuild project role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": [
                "YOUR_ECR_REPOSITORY_ARN"
            ],
            "Effect": "Allow"
        },
        {
            "Action": "ecr:GetAuthorizationToken",
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```

Additionally, if you are using ECR and the ECR repository is not in the same account the CodeBuild project is, consider to [add ECR permissions to the CodeBuild account](https://docs.amazonaws.cn/en_us/AmazonECR/latest/userguide/repository-policy-examples.html#IAM_allow_other_accounts).

## Configuration

Last step is to let the GitHub workflow know where it needs to upload the code configuring the optional input `override_image_ssm_base`:

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
          override_image_ssm_base: /YOUR/SSM/PARAMETER/CONTAINING/IMAGE/BASE
```

Let's assume that you want to use a tag prefix `ci`, so you will pick up an image with this pattern: `IMAGE_REPO_URI:ci_COMMIT_HASH_ID`, you will need to add the `override_image_tag_prefix` input:

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
          override_image_ssm_base: /YOUR/SSM/PARAMETER/CONTAINING/IMAGE/BASE
          override_image_tag_prefix: ci
```

Imagine that you are using this action for Continuous Deployment, as mentioned before, and you want to trigger it on the tag push on your repository, then your workflow can be something like this:

```yaml
---
name: "Release Workflow"
on:
  push:
    tags:
      - "v*"

jobs:
  test-codebuild-action:
    steps:

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.YOUR_IAM_USER_ACCESS_KEY_SECRET_NAME }}
          aws-secret-access-key: ${{ secrets.YOUR_IAM_USER_ACCESS_SECRET_KEY_SECRET_NAME }}
          aws-region: AWS_REGION_YOUR_GOING_TO_USE

      - name: Get tag name
        id: get_current_tag
        run: |
          TAG=$(git describe --tags --abbrev=0)
          echo "Current tag: $TAG"
          echo ::set-output name=tag::${TAG}

      - name: Run CodeBuild
        uses: neovasili/aws-codebuild@v1.0.0
        with:
          aws_region: AWS_REGION_YOUR_GOING_TO_USE
          codebuild_job_name: YOUR_CODEBUILD_PROJECT_NAME
          codebuild_log_group: YOUR_CODEBUILD_PROJECT_LOG_GROUP_NAME
          override_image_ssm_base: /YOUR/SSM/PARAMETER/CONTAINING/IMAGE/BASE
          override_image_tag: ${{ steps.get_current_tag.outputs.tag }}
```

So you are picking up the pushed tag name and passing it as a parameter to the CodeBuild action.
