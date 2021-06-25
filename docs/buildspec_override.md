# Buildspec override

&#x2B11; [Return to index](../README.md)

- [Buildspec override](#buildspec-override)
  - [How it works](#how-it-works)
  - [Configuration](#configuration)

```txt
⚠️ WARNING

Overriding buildspec file in a CodeBuild project can lead into security issues. Consider enable it only into isolated/sandbox environments or in private repositories.
```

The buildspec references the definition of a CodeBuild project steps to execute once it's invoked. These steps can be defined on CodeBuild project provisioning time as well as on runtime, so for some specific cases you can easily alter the CodeBuild invoked job behaviour.

This action, will use inline "injection" to override buildspec, that means that the buildspec file should exists in the repository.

## How it works

When this feature is enabled and properly configured will work following these steps:

- Reads the buildspec file content from the provided file path in the `buildspec` input
- Invokes CodeBuild passing the new buildspec definition

## Configuration

This feature is **disabled by default**, to enable it you need to create an SSM parameter with this path `/github/buildspec/override` containing `True` and it will act as a feature flag in the same account the CodeBuild project lives.

Remember that that also requires extra permissions to your GitHub IAM user to get the value of that parameter to enable the feature.

Last step is to let the GitHub workflow know where it needs to upload the code configuring the optional input `buildspec`:

```yaml
---
name: "Test CodeBuild action"

jobs:
  test-codebuild-action:
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

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
          buildspec: RELATIVE_PATH_TO_BUILDSPEC_FILE_IN_REPO
```

As mentioned in the beginning, your need this to exists in the repository, so don't forget to add to your workflow a step that first checkouts the repository code into the GitHub actions agent.
