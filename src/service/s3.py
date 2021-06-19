import os
import boto3
import logging
import zipfile

from pathlib import Path


class S3Service:
    def __init__(self, region: str, logger: logging.Logger):
        self.__logger = logger

        self.s3_resource = boto3.resource("s3", region_name=region)

    @staticmethod
    def get_filesize_in_kb(file_path: str) -> str:
        return f"{str(round(os.path.getsize(file_path) / 1024, 0))} KB"

    @staticmethod
    def read_gitignore():
        content = open(file=".gitignore", mode="r").readlines()
        content = [line.replace("\n", "") for line in content]
        content.append("./.git/")
        content.append("./.gitignore")

        return list(
            filter(
                lambda line: line != "" and not line.startswith("#"),
                content,
            ),
        )

    @staticmethod
    def to_ignore(ignore_patterns: list, element: str):
        for ignore_pattern in ignore_patterns:
            if ignore_pattern in element:
                return True

        return False

    @staticmethod
    def get_files_to_upload(ignore_patterns: list):
        subdirs = os.walk("./")
        files_to_upload = list()

        for subdir in subdirs:
            path = subdir[0]
            for files_set in subdir[1:]:
                for file in files_set:
                    if path == "./":
                        file_path = f"{path}{file}"
                    else:
                        file_path = f"{path}/{file}"
                    if Path(file_path).is_file():
                        if not S3Service.to_ignore(ignore_patterns=ignore_patterns, element=file_path):
                            file_path = file_path[2:]
                            files_to_upload.append(file_path)

        return files_to_upload

    def upload_code(self, s3_path: str, commit_id: str):
        ignore_list = S3Service.read_gitignore()
        files_to_upload = S3Service.get_files_to_upload(ignore_patterns=ignore_list)
        bucket_name = s3_path.split("/")[0]
        key_base_path = "".join(s3_path.split("/")[1:])

        s3_file_name = "source.zip"

        s3_file = zipfile.ZipFile(s3_file_name, "w")

        for filename in files_to_upload:
            s3_file.write(filename)

        s3_file.close()

        s3_file_path = f"{s3_path}/{commit_id}/{s3_file_name}"

        file_size = S3Service.get_filesize_in_kb(file_path=s3_file_name)

        self.__logger.info("Uploading source code to S3...")

        self.__logger.debug(f"S3 path: {s3_file_path}")
        self.__logger.debug(f"Total number of files: {len(files_to_upload)}")
        self.__logger.debug(f"Compressed size: {file_size}")

        self.s3_resource.meta.client.upload_file(
            Filename=s3_file_name,
            Bucket=bucket_name,
            Key=f"{key_base_path}/{commit_id}/{s3_file_name}",
        )
        self.__logger.info("Upload complete")

        return s3_file_path
