import boto3


class SSMService:
    def __init__(self, region: str):
        self.ssm_client = boto3.client("ssm", region_name=region)

    def get_override_image(self, ssm_parameter: str, commit_id: str, tag_prefix: str = None):
        response = self.ssm_client.get_parameter(
            Name=ssm_parameter,
        )

        image = response["Parameter"]["Value"]

        if tag_prefix is not None:
            image = f"{image}:{tag_prefix}{commit_id}"

        else:
            image = f"{image}:{commit_id}"

        return image
