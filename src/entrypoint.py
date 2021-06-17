import traceback
from helper.common import CommonsHelper
from service.s3 import S3Service
from service.ssm import SSMService
from service.codebuild import CodeBuildService


def main():
    try:
        image = None
        s3_file_path = None
        commit_id = CommonsHelper.get_commit_id()
        aws_default_region, codebuild_job_name, codebuild_log_group = CommonsHelper.get_mandatory_inputs()
        (
            s3_path,
            buildspec,
            override_image_ssm_base,
            override_image_tag,
            override_image_tag_prefix,
        ) = CommonsHelper.get_optional_inputs()

        print("--  START CODEBUILD CUSTOM ACTION   --")
        print("--------------------------------------")

        codebuild_service = CodeBuildService(
            region=aws_default_region,
            codebuild_job_name=codebuild_job_name,
            build_log_group_name=codebuild_log_group,
        )

        if s3_path is not None:
            print("-> Upload code to S3 stage")
            s3_service = S3Service(region=aws_default_region)
            s3_file_path = s3_service.upload_code(
                commit_id=commit_id,
                s3_path=s3_path,
            )

        if override_image_ssm_base is not None:
            print("-> Retrieve image for override")
            ssm_service = SSMService(region=aws_default_region)
            image = ssm_service.get_override_image(
                ssm_parameter=override_image_ssm_base,
                commit_id=commit_id,
                tag=override_image_tag,
                tag_prefix=override_image_tag_prefix,
            )

        print("-> Trigger CodeBuild job stage")
        codebuild_service.invoke_codebuild_job(
            commit_id=commit_id,
            buildspec=buildspec,
            s3_path=s3_file_path,
            image=image,
        )

        print("-> Wait CodeBuild job to finish stage")
        build_status = codebuild_service.wait_codebuild_to_finish()

        print(f"Build status: {build_status}")
        if build_status == "FAILED":
            exit(1)

        print("--------------------------------------")
        print("-- CODEBUILD CUSTOM ACTION FINISHED --")

    except Exception as error:
        traceback.print_exc()
        print(f"[ERROR] {str(error)}")
        exit(1)


if __name__ == "__main__":
    main()
