import boto3


class SSMService:
    def __init__(self, region: str):
        self.ssm_client = boto3.client("ssm", region_name=region)

    def get_override_image(self, ssm_parameter: str, commit_id: str, tag: str = None, tag_prefix: str = None):
        response = self.ssm_client.get_parameter(
            Name=ssm_parameter,
        )

        image = response["Parameter"]["Value"]

        if tag is not None:
            return f"{image}:{tag}"

        if tag_prefix is not None:
            return f"{image}:{tag_prefix}{commit_id}"

        return f"{image}:{commit_id}"
