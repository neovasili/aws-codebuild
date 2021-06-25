import os
import time
import boto3
import logging


class CodeBuildService:
    def __init__(self, region: str, codebuild_job_name: str, build_log_group_name: str, logger: logging.Logger):
        self.region = region
        self.codebuild_job_name = codebuild_job_name
        self.build_log_group_name = build_log_group_name
        self.build_id = None
        self.__logger = logger

        self.codebuild_client = boto3.client("codebuild", region_name=self.region)
        self.logs_client = boto3.client("logs", region_name=region)

    @staticmethod
    def get_codebuild_custom_env_vars():
        custom_environment_variables = list()

        for env_var_key, env_var_value in os.environ.items():
            if env_var_key.startswith("PLAINTEXT"):
                environment_variable = {
                    "name": env_var_key.replace("PLAINTEXT_", ""),
                    "value": env_var_value,
                    "type": "PLAINTEXT",
                }
                custom_environment_variables.append(environment_variable)

            if env_var_key.startswith("SECRET"):
                environment_variable = {
                    "name": env_var_key.replace("SECRET_", ""),
                    "value": env_var_value,
                    "type": "SECRETS_MANAGER",
                }
                custom_environment_variables.append(environment_variable)

            if env_var_key.startswith("SSM"):
                environment_variable = {
                    "name": env_var_key.replace("SSM_", ""),
                    "value": env_var_value,
                    "type": "PARAMETER_STORE",
                }
                custom_environment_variables.append(environment_variable)

        return custom_environment_variables

    @staticmethod
    def get_current_build_phase(phases: list):
        return phases[-1]["phaseType"]

    def invoke_codebuild_job(
        self,
        commit_id: str,
        s3_path: str = None,
        buildspec: str = None,
        image: str = None,
    ):
        environment_variables = [
            {
                "name": "COMMIT_ID",
                "value": commit_id,
                "type": "PLAINTEXT",
            },
            {
                "name": "AWS_DEFAULT_REGION",
                "value": self.region,
                "type": "PLAINTEXT",
            },
        ]

        custom_environment_variables = CodeBuildService.get_codebuild_custom_env_vars()

        if len(custom_environment_variables) > 0:
            environment_variables.extend(custom_environment_variables)

        self.__logger.debug(f"CodeBuild project: {self.codebuild_job_name}")
        self.__logger.debug(
            f"""
            Environment variables: {[f'''{env_var['name']}: {env_var['value']}''' for env_var in environment_variables]}
            """
        )

        codebuild_arguments = {
            "projectName": self.codebuild_job_name,
            "environmentVariablesOverride": environment_variables,
        }

        if buildspec is not None:
            self.__logger.debug(f"Use buildspec: {buildspec}")
            buildspec_content = ""

            with open(buildspec, "r") as file:
                buildspec_content = file.read()

            if "AWS_ACCESS_KEY_ID" not in str(buildspec_content):
                codebuild_arguments["buildspecOverride"] = buildspec_content

            else:
                self.__logger.warning(
                    "Detected obvious attempt of getting AWS credentials from CodeBuild; buildspec file won't be overridden"
                )

        if image is not None:
            self.__logger.debug(f"Use image with tag: {image.split(':')[1]}")
            codebuild_arguments["imageOverride"] = image

        if s3_path is not None:
            self.__logger.debug(f"Use s3 source: {s3_path}")
            codebuild_arguments["sourceTypeOverride"] = "S3"
            codebuild_arguments["sourceLocationOverride"] = s3_path

        response = None

        response = self.codebuild_client.start_build(
            **codebuild_arguments,
        )

        self.build_id = response["build"]["id"]

        self.__logger.debug(f"Build ID: {self.build_id}")

        return self.build_id

    def get_log_events(self, start_time: int):
        response = None
        build_id = self.build_id.split(":")[1]

        get_log_events_arguments = {
            "logGroupName": self.build_log_group_name,
            "logStreamName": build_id,
            "startFromHead": True,
        }

        try:
            if start_time is not None:
                get_log_events_arguments["startTime"] = start_time

            response = self.logs_client.get_log_events(**get_log_events_arguments)
            events = response["events"]

            if len(events) > 0:
                for event in events:
                    start_time = event["timestamp"]
                    message = event["message"].replace("\n", "")
                    self.__logger.debug(message)

        except Exception:
            pass

        return start_time

    def wait_codebuild_to_finish(self):
        build_complete = False
        build_status = "IN_PROGRESS"
        build_current_phase = None
        start_time = None

        while not build_complete:
            response = self.codebuild_client.batch_get_builds(ids=[self.build_id])

            build = response["builds"][0]
            build_complete = build["buildComplete"]
            build_status = build["buildStatus"]
            current_phase = CodeBuildService.get_current_build_phase(phases=build["phases"])

            if current_phase != build_current_phase:
                build_current_phase = current_phase
                self.__logger.info(f"Build phase: {build_current_phase}")

            start_time = self.get_log_events(start_time=start_time)

            if not build_complete:
                time.sleep(5)

        time.sleep(10)
        self.get_log_events(start_time=(start_time + 10))

        return build_status
