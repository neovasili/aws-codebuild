# Source code from S3

&#x2B11; [Return to index](../README.md)

- [Source code from S3](#source-code-from-s3)
  - [How it works](#how-it-works)
  - [Additional AWS resources needed](#additional-aws-resources-needed)
  - [Permissions](#permissions)
  - [Configuration](#configuration)

Even though with CodeBuild you can configure a GitHub connection directly to your GitHub repository, a CodeBuild project cannot be connected to several projects at the same time, and if you want to change it in runtime (which is also possible), the setup is far to be trivial, specially if you are dealing with multiple organizations because you need to deal with Oauth tokens.

Another easier approach is to push the code to a S3 bucket accessible for the CodeBuild project and override that source for the CodeBuild project in runtime, so you can reuse the same CodeBuild project with multiple repositories. A good example is to have one CodeBuild project to build docker images, you only have it defined and maintained just once, but you use it as many times you need.

## How it works

When this feature is enabled and properly configured will work following these steps:

- Reads the `.gitignore` file in your repository and will ignore all files containing the gitignore patterns as well as anything under `.git/` folder
- Pack files into a `source.zip` zip file
- Upload zip file to S3 with the following pattern:
  - If you are pushing a commit:
    - `YOUR_BUCKET_NAME/WHATEVER_PREFIX_KEY_YOU_WANT/COMMIT_HASH_ID/source.zip`
  - If you are pushing a tag:
    - `YOUR_BUCKET_NAME/WHATEVER_PREFIX_KEY_YOU_WANT/TAG_NAME/source.zip`
- Once CodeBuild is invoked, the CodeBuild source is changed to use the uploaded source zip file, so CodeBuild will automatically download and unzip your source code

## Additional AWS resources needed

In this case you will need a S3 bucket previously provisioned accessible by CodeBuild project; thus, no bucket policy or SCP restricting it. No versioning, or other setup is needed.

Even though, as this bucket is intended to contain source code temporary, [it's recommended to create a lifecycle policy](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) that expires objects or at least change storage tier.

## Permissions

The following permissions in your CodeBuild project role (if your bucket have versioning enabled you will require some extra permissions):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
            ],
            "Resource": [
                "YOUR_BUCKET_ARN",
                "YOUR_BUCKET_ARN/*"
            ],
            "Effect": "Allow"
        }
    ]
}
```

Also, as you are going to upload to S3 our GitHub repository source code, you need to add the following permissions to the [IAM user created for GitHub action](../README.md#minimal-permissions):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "YOUR_BUCKET_ARN",
                "YOUR_BUCKET_ARN/*"
            ],
            "Effect": "Allow"
        }
    ]
}
```

## Configuration

Last step is to let the GitHub workflow know where it needs to upload the code configuring the optional input `s3_path`:

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
          s3_path: YOUR_BUCKET_NAME/WHATEVER_PREFIX_KEY_YOU_WANT
```
