import os
import logging

from helper.exception import MissingMandatoryParameters


class CommonsHelper:
    @staticmethod
    def get_commit_id():
        missing_params = list()
        github_sha = github_ref = None

        if "GITHUB_SHA" in os.environ:
            github_sha = os.environ["GITHUB_SHA"]
        else:
            missing_params.append("GITHUB_SHA")

        if "GITHUB_REF" in os.environ:
            github_ref = os.environ["GITHUB_REF"]
        else:
            missing_params.append("GITHUB_REF")

        if len(missing_params) > 0:
            raise MissingMandatoryParameters(missing_parameters=missing_params)

        commit_id = github_sha

        if "tags" in github_ref:
            tag_name = github_ref.split("/")[-1]
            commit_id = tag_name

        return commit_id

    @staticmethod
    def get_mandatory_inputs():
        missing_params = list()
        aws_default_region = codebuild_job_name = codebuild_log_group = None

        if "INPUT_AWS_REGION" in os.environ:
            aws_default_region = os.environ["INPUT_AWS_REGION"]
        else:
            missing_params.append("AWS_REGION")

        if "INPUT_CODEBUILD_JOB_NAME" in os.environ:
            codebuild_job_name = os.environ["INPUT_CODEBUILD_JOB_NAME"]
        else:
            missing_params.append("CODEBUILD_JOB_NAME")

        if "INPUT_CODEBUILD_LOG_GROUP" in os.environ:
            codebuild_log_group = os.environ["INPUT_CODEBUILD_LOG_GROUP"]
        else:
            missing_params.append("CODEBUILD_LOG_GROUP")

        if len(missing_params) > 0:
            raise MissingMandatoryParameters(missing_parameters=missing_params)

        return aws_default_region, codebuild_job_name, codebuild_log_group

    @staticmethod
    def get_formated_input_name(input_name: str):
        return input_name.replace("-", "_").upper()

    @staticmethod
    def get_input(input_name: str):
        environment_variable_name = f"INPUT_{CommonsHelper.get_formated_input_name(input_name=input_name)}"

        if environment_variable_name not in os.environ:
            return None

        value = os.environ[environment_variable_name]
        if value == "":
            return None

        return value

    @staticmethod
    def get_optional_inputs():
        s3_path = buildspec = override_image_ssm_base = override_image_tag = override_image_tag_prefix = None

        s3_path = CommonsHelper.get_input(input_name="s3_path")
        buildspec = CommonsHelper.get_input(input_name="buildspec")
        override_image_ssm_base = CommonsHelper.get_input(input_name="override_image_ssm_base")
        override_image_tag = CommonsHelper.get_input(input_name="override_image_tag")
        override_image_tag_prefix = CommonsHelper.get_input(input_name="override_image_tag_prefix")

        return s3_path, buildspec, override_image_ssm_base, override_image_tag, override_image_tag_prefix

    @staticmethod
    def get_log_level():
        log_level_router = {
            None: logging.DEBUG,
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        return log_level_router[CommonsHelper.get_input(input_name="log_level")]
