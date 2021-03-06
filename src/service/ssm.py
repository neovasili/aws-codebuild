import boto3
import logging


class SSMService:
    def __init__(self, region: str, logger: logging.Logger):
        self.__logger = logger

        self.ssm_client = boto3.client("ssm", region_name=region)

    def get_buildspec_override_feature_flag(self):
        try:
            response = self.ssm_client.get_parameter(
                Name="/github/buildspec/override",
            )
            self.__logger.info(response["Parameter"]["Value"])
            if response["Parameter"]["Value"] == "True":
                return True
        except Exception:
            self.__logger.debug("Buildspec override is not enabled")

        return False

    def get_override_image(self, ssm_parameter: str, commit_id: str, tag: str = None, tag_prefix: str = None):
        response = self.ssm_client.get_parameter(
            Name=ssm_parameter,
        )

        image = response["Parameter"]["Value"]

        if tag is not None:
            self.__logger.debug(f"Going to use image with tag {tag}")
            return f"{image}:{tag}"

        if tag_prefix is not None:
            self.__logger.debug(f"Going to use image with tag prefix {tag_prefix} and commit id {commit_id}")
            return f"{image}:{tag_prefix}_{commit_id}"

        self.__logger.debug(f"Going to use image with commit id {commit_id}")
        return f"{image}:{commit_id}"
