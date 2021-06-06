import os
import time
import boto3
import datetime


class CodeBuildService:
    def __init__(self, region: str, codebuild_job_name: str, build_log_group_name: str):
        self.region = region
        self.codebuild_job_name = codebuild_job_name
        self.build_log_group_name = build_log_group_name
        self.build_id = None

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

    def invoke_codebuild_job(self, commit_id: str, image: str = None):
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

        response = None

        if image is None:
            response = self.codebuild_client.start_build(
                projectName=self.codebuild_job_name,
                environmentVariablesOverride=environment_variables,
            )

        else:
            response = self.codebuild_client.start_build(
                projectName=self.codebuild_job_name,
                environmentVariablesOverride=environment_variables,
                imageOverride=image,
            )
        self.build_id = response["build"]["id"]

        return self.build_id

    def get_log_events(self, start_time: int):
        response = None
        build_id = self.build_id.split(":")[1]

        try:
            if start_time is not None:
                response = self.logs_client.get_log_events(
                    logGroupName=self.build_log_group_name,
                    logStreamName=build_id,
                    startTime=start_time,
                    startFromHead=True,
                )
            else:
                response = self.logs_client.get_log_events(
                    logGroupName=self.build_log_group_name,
                    logStreamName=build_id,
                    startFromHead=True,
                )
            events = response["events"]

            if len(events) > 0:
                for event in events:
                    start_time = event["timestamp"]
                    formated_time = datetime.datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    message = event["message"].replace("\n", "")
                    print(f"{formated_time} -- {message}")

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
                print(f"Build phase: {build_current_phase}")

            start_time = self.get_log_events(start_time=start_time)

            if not build_complete:
                time.sleep(5)

        time.sleep(10)
        self.get_log_events(start_time=(start_time + 10))

        return build_status
