# AWS CodeBuild github action

This repository contains a GitHub action to invoke and integrate CodeBuild as part of a GitHub workflow with advanced features, like override environment image or passthrough source code using a S3 bucket, thus making your CodeBuild projects more reusable and agnostic to the git repository.

[Project Roadmap](https://github.com/neovasili/aws-codebuild/projects/1)

## References

- [CodeBuild environment variables](https://docs.aws.amazon.com/codebuild/latest/APIReference/API_EnvironmentVariable.html)
- [CodeBuild environment variables secrets](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager)
- [CodeBuild environment SSM parameter](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.parameter-store)
- [Boto3 CodeBuild reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.start_build)
- [AWS official CodeBuild action](https://github.com/aws-actions/aws-codebuild-run-build)
