import os


class CommonsHelper:
    @staticmethod
    def get_commit_id():
        github_sha = os.environ["GITHUB_SHA"]
        github_ref = os.environ["GITHUB_REF"]

        commit_id = github_sha

        if "tags" in github_ref:
            tag_name = github_ref.split("/")[-1]
            commit_id = tag_name

        return commit_id

    @staticmethod
    def get_formated_input_name(input_name: str):
        return input_name.replace("-", "_").upper()

    @staticmethod
    def get_input(input_name: str):
        environment_variable_name = f"INPUT_{CommonsHelper.get_formated_input_name(input_name=input_name)}"

        value = os.environ[environment_variable_name]
        if value == "":
            value = None

        return value

    @staticmethod
    def get_mandatory_inputs():
        missing_params = list()
        aws_default_region = None
        codebuild_job_name = None
        codebuild_log_group = None

        try:
            aws_default_region = os.environ["INPUT_AWS_REGION"]
        except Exception:
            missing_params.append("AWS_REGION")

        try:
            codebuild_job_name = os.environ["INPUT_CODEBUILD_JOB_NAME"]
        except Exception:
            missing_params.append("CODEBUILD_JOB_NAME")

        try:
            codebuild_log_group = os.environ["INPUT_CODEBUILD_LOG_GROUP"]
        except Exception:
            missing_params.append("CODEBUILD_LOG_GROUP")

        if len(missing_params) > 0:
            raise Exception(f"Missing mandatory input params: {missing_params}")

        return aws_default_region, codebuild_job_name, codebuild_log_group

    @staticmethod
    def get_optional_inputs():
        s3_path = None
        buildspec = None
        override_image_ssm_base = None
        override_image_tag = None
        override_image_tag_prefix = None

        s3_path = CommonsHelper.get_input(input_name="s3_path")
        buildspec = CommonsHelper.get_input(input_name="buildspec")
        override_image_ssm_base = CommonsHelper.get_input(input_name="override_image_ssm_base")
        override_image_tag = CommonsHelper.get_input(input_name="override_image_tag")
        override_image_tag_prefix = CommonsHelper.get_input(input_name="override_image_tag_prefix")

        return s3_path, buildspec, override_image_ssm_base, override_image_tag, override_image_tag_prefix
