import logging

from helper.config import CustomFormatter
from helper.common import CommonsHelper
from helper.exception import (
    FailedBuild,
    MissingMandatoryParameters,
)
from service.s3 import S3Service
from service.ssm import SSMService
from service.codebuild import CodeBuildService


def main():
    logger = logging.getLogger("CodeBuild GitHub action")
    logger.setLevel(CommonsHelper.get_log_level())
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())
    logger.addHandler(stream_handler)

    try:
        image = s3_file_path = None
        commit_id = CommonsHelper.get_commit_id()
        (
            aws_default_region,
            codebuild_job_name,
            codebuild_log_group,
        ) = CommonsHelper.get_mandatory_inputs()
        (
            s3_path,
            buildspec,
            override_image_ssm_base,
            override_image_tag,
            override_image_tag_prefix,
        ) = CommonsHelper.get_optional_inputs()

        logger.header("START CODEBUILD GITHUB ACTION")
        codebuild_service = CodeBuildService(
            region=aws_default_region,
            codebuild_job_name=codebuild_job_name,
            build_log_group_name=codebuild_log_group,
            logger=logger,
        )

        if s3_path is not None:
            logger.header("-- Override source with S3 source")
            s3_service = S3Service(region=aws_default_region, logger=logger)
            s3_file_path = s3_service.upload_code(
                commit_id=commit_id,
                s3_path=s3_path,
            )

        if override_image_ssm_base is not None:
            logger.header("-- Override CodeBuild image")
            ssm_service = SSMService(region=aws_default_region, logger=logger)
            image = ssm_service.get_override_image(
                ssm_parameter=override_image_ssm_base,
                commit_id=commit_id,
                tag=override_image_tag,
                tag_prefix=override_image_tag_prefix,
            )

        logger.header("Trigger CodeBuild job stage")

        if buildspec is not None:
            logger.header("-- Override buildpec file")

        codebuild_service.invoke_codebuild_job(
            commit_id=commit_id,
            buildspec=buildspec,
            s3_path=s3_file_path,
            image=image,
        )

        logger.header("Wait CodeBuild job to finish stage")
        build_status = codebuild_service.wait_codebuild_to_finish()

        if build_status == "FAILED":
            raise FailedBuild("Build failed")

        logger.info("Build succeeded")

    except MissingMandatoryParameters as error:
        logger.error(str(error))
        exit(1)

    except FailedBuild as error:
        logger.error(str(error))
        exit(1)

    except Exception as error:
        logger.critical(f"Unexpected exception: {str(error)}")
        exit(1)

    finally:
        logger.header("CODEBUILD CUSTOM ACTION FINISHED")


if __name__ == "__main__":
    main()
