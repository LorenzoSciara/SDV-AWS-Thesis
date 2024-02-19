from constructs import Construct

from aws_cdk import (
    aws_codebuild as codebuild,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_codecommit as codecommit,
    aws_codepipeline as pipeline,
    aws_codepipeline_actions as pipelineactions,
    aws_s3 as s3,
    aws_codepipeline_actions as codepipeline_actions,
    aws_lambda as _lambda,
    aws_logs as logs,
    Duration,
    Aws,
    Stack,
    RemovalPolicy,
)

class HawkbitPipelineCppStack(Stack):
     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account=Aws.ACCOUNT_ID
        region=Aws.REGION

        source_artifact_c = pipeline.Artifact("SourceArtifact")

        cpp_custom_code_repo = codecommit.Repository(
            self, "HawkbitCppCustomBuildImageRepo",
            repository_name="HawkbitCppCustomBuildImage",
            # Copies files from app directory to the repo as the initial commit
            code=codecommit.Code.from_zip_file("./repos/HawkbitCppCustomBuildImage.zip", "main")
        )
        source_stage_c = pipeline.StageProps(
            stage_name="Source",
            actions=[
                pipelineactions.CodeCommitSourceAction(
                    action_name="CodeCommit",
                    branch="main",
                    output=source_artifact_c,
                    repository=cpp_custom_code_repo,
                )
            ]
        )

        codebuild_role = iam.Role(self, "hawkbitCppCustomImageBuildRole", 
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com")
        )
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codecommit:GitPull"],
                resources=[f"arn:aws:codecommit:{region}:{account}:HawkbitCppCustomBuildImage"],
            )
        )
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/codebuild/HawkbitCppCustomBuildImage:*", f"arn:aws:logs:{region}:{account}:log-group:/aws/codebuild/HawkbitCppCustomBuildImage"],
            )
        )
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codebuild:BatchPutCodeCoverages", "codebuild:BatchPutTestCases", "codebuild:CreateReport", "codebuild:CreateReportGroup", "codebuild:UpdateReport"],
                resources=[f"arn:aws:codebuild:{region}:{account}:report-group/HawkbitCppCustomBuildImage-*"],
            )
        )
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:GetRepositoryPolicy", "ecr:DescribeRepositories", "ecr:ListImages", "ecr:DescribeImages", "ecr:BatchGetImage", "ecr:GetLifecyclePolicy", "ecr:GetLifecyclePolicyPreview", "ecr:ListTagsForResource", "ecr:DescribeImageScanFindings", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage"],
                resources=["*"],
            )
        )

        ecr_repository = ecr.Repository(self, "HawkbitCppBlogRepo",
            repository_name="hawkbit-cpp-blog",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

        codebuild_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "ecr:BatchCheckLayerAvailability",
                "ecr:BatchGetImage",
                "ecr:CompleteLayerUpload",
                "ecr:GetDownloadUrlForLayer",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage",
                "ecr:UploadLayerPart"
            ],
            resources=[ecr_repository.repository_arn],
        )

        # CodeBuild project that builds the Docker image
        cpp_custom_build = codebuild.Project(
            self, "HawkbitCppCustomBuildImageBuild",
            build_spec=codebuild.BuildSpec.from_source_filename(
                "buildspec.yml"),
            source=codebuild.Source.code_commit(
                repository=cpp_custom_code_repo,
                branch_or_ref="master"
            ),
            environment=codebuild.BuildEnvironment(
                privileged=True
            ),
            role=codebuild_role,
            project_name="HawkbitCppCustomBuildImage",
            environment_variables={
                'ecr': codebuild.BuildEnvironmentVariable(
                    value=ecr_repository.repository_uri),
                'tag': codebuild.BuildEnvironmentVariable(
                    value='v1'),
            },
            timeout=Duration.minutes(60)
        )
        ecr_repository.grant_pull_push(cpp_custom_build)

        build_stage_c = pipeline.StageProps(
            stage_name="Build",
            actions=[
                pipelineactions.CodeBuildAction(
                    action_name="Build",
                    project=cpp_custom_build,
                    input=source_artifact_c,
                )
            ]
        )

        #retrieve bucket for pipeline artifacts
        artifact_bucket = s3.Bucket.from_bucket_arn(self, f"codepipeline-{region}-833521754963", f"arn:aws:s3:::codepipeline-{region}-833521754963") #default codepipeline bucket


        cpp_custom_pipeline = pipeline.Pipeline(
            self, "hawkbit-device-c",
            pipeline_name="hawkbit-device-c",
            artifact_bucket=artifact_bucket,
            stages=[source_stage_c, build_stage_c]
        )

        # Creates an AWS CodeCommit repository
        code_repo = codecommit.Repository(
            self, "HawkbitDeviceC",
            repository_name="HawkbitDeviceC",
            # Copies files from app directory to the repo as the initial commit
            code=codecommit.Code.from_zip_file("./repos/Lorenzo_DeviceC.zip", "master")
        )
        
        source_artifact = pipeline.Artifact("SourceArtifact")
        build_artifact = pipeline.Artifact("BuildArtifact")

        # Creates the source stage for CodePipeline
        source_stage = pipeline.StageProps(
            stage_name="Source",
            actions=[
                pipelineactions.CodeCommitSourceAction(
                    action_name="CodeCommit",
                    branch="master",
                    output=source_artifact,
                    repository=code_repo,
                    variables_namespace="SourceVariables"
                )
            ]
        )

        # CodeBuild project that builds the Docker image
        hawkbit_build = codebuild.Project(
            self, "HawkbitDeviceBuildC",
            build_spec=codebuild.BuildSpec.from_source_filename(
                "buildspec.yml"),
            source=codebuild.Source.code_commit(
                repository=code_repo,
                branch_or_ref="master"
            ),
            environment=codebuild.BuildEnvironment(
                privileged=True,
                 build_image=codebuild.LinuxBuildImage.from_ecr_repository(ecr_repository, "v1")
            ),
            project_name="HawkbitDeviceBuildC"
        )

        # Creates the test build stage for CodePipeline
        build_stage = pipeline.StageProps(
            stage_name="Build",
            actions=[
                pipelineactions.CodeBuildAction(
                    action_name="Build",
                    input=pipeline.Artifact("SourceArtifact"),
                    project=hawkbit_build,
                    outputs=[build_artifact]
                )
            ]
        )

        # Lambda role for Delpoying Software on Hawkbit Server
        lambda_role = iam.Role(self, "hawkbitDeploySoftwareOnHawkbitServerLambdaRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:Describe*","ssm:Get*","ssm:List*","kms:CreateAlias","kms:CreateKey","kms:DeleteAlias","kms:Describe*","kms:GenerateRandom","kms:Get*","kms:List*","kms:TagResource","kms:UntagResource","iam:ListGroups","iam:ListRoles","iam:ListUsers","codepipeline:PutJobSuccessResult","codepipeline:PutJobFailureResult"],
                resources=["*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogStream",
                "logs:PutLogEvents"],
                resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/hawkbitDeploySoftwareOnHawkbitServer:*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:{region}:{account}:*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:*"],
                resources=["arn:aws:logs:*:*:*"],
            )
        )
        # Lambda for the new stage
        lambda_function = _lambda.Function(
            self,"hawkbitDeploySoftwareOnHawkbitServer",
            function_name="hawkbitDeploySoftwareOnHawkbitServer",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("./lambda/hawkbitDeploySoftwareOnHawkbitServer.zip"),
            handler="hawkbitDeploySoftwareOnHawkbitServer.lambda_handler",
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_DAY,
            timeout=Duration.seconds(60)
        )

        hawkbitDeploySoftwareOnHawkbitServer_output = pipeline.Artifact("DeploySoftwareOnHawkbitServerArtifacts")

        hawkbitDeploySoftwareOnHawkbitServer_invoke = codepipeline_actions.LambdaInvokeAction(
            action_name="hawkbitDeploySoftwareOnHawkbitServer",
            lambda_=lambda_function,
            inputs=[build_artifact],
            user_parameters_string="#{SourceVariables.RepositoryName}",
            variables_namespace="LambdaVariables",
            outputs=[hawkbitDeploySoftwareOnHawkbitServer_output],
        )

        # New stage for Deploying Software on Hawkbit Server
        hawkbitDeploySoftwareOnHawkbitServer_stage = pipeline.StageProps(
            stage_name="hawkbitDeploySoftwareOnHawkbitServer",
            actions=[hawkbitDeploySoftwareOnHawkbitServer_invoke],
        )

        # Lambda role for Rolling out Software on device
        lambda_role = iam.Role(self, "hawkbitRolloutSoftwareOnDeviceLambdaRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:Describe*","ssm:Get*","ssm:List*","kms:CreateAlias","kms:CreateKey","kms:DeleteAlias","kms:Describe*","kms:GenerateRandom","kms:Get*","kms:List*","kms:TagResource","kms:UntagResource","iam:ListGroups","iam:ListRoles","iam:ListUsers","codepipeline:PutJobSuccessResult","codepipeline:PutJobFailureResult"],
                resources=["*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogStream",
                "logs:PutLogEvents"],
                resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/hawkbitRolloutSoftwareOnDevice:*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:{region}:{account}:*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:*"],
                resources=["arn:aws:logs:*:*:*"],
            )
        )
        # Lambda for the new stage
        lambda_function = _lambda.Function(
            self,"hawkbitRolloutSoftwareOnDevice",
            function_name="hawkbitRolloutSoftwareOnDevice",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("./lambda/hawkbitRolloutSoftwareOnDevice.zip"),
            handler="hawkbitRolloutSoftwareOnDevice.lambda_handler",
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_DAY,
            timeout=Duration.seconds(60),
        )

        hawkbitRolloutSoftwareOnDevice_output = pipeline.Artifact("hawkbitRolloutSoftwareOnDeviceArtifacts")
        invoke_action = codepipeline_actions.LambdaInvokeAction(
            action_name="hawkbitRolloutSoftwareOnDevice",
            lambda_=lambda_function,
            inputs=[hawkbitDeploySoftwareOnHawkbitServer_output],
            user_parameters_string="#{LambdaVariables.DistributioSet}",
            outputs=[hawkbitRolloutSoftwareOnDevice_output],
        )

        # New stage for Rolling out Software on Device
        hawkbitRolloutSoftwareOnDevice = pipeline.StageProps(
            stage_name="hawkbitRolloutSoftwareOnDevice",
            actions=[invoke_action],
            transition_disabled_reason="Stage is not needed now",
            transition_to_enabled=False
        )

        # Lambda role for assign Software To a single Device
        lambda_role = iam.Role(self, "hawkbitAssignSoftwareToDeviceLambdaRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:Describe*","ssm:Get*","ssm:List*","kms:CreateAlias","kms:CreateKey","kms:DeleteAlias","kms:Describe*","kms:GenerateRandom","kms:Get*","kms:List*","kms:TagResource","kms:UntagResource","iam:ListGroups","iam:ListRoles","iam:ListUsers","codepipeline:PutJobSuccessResult","codepipeline:PutJobFailureResult"],
                resources=["*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogStream",
                "logs:PutLogEvents"],
                resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/hawkbitAssignSoftwareToDevice:*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:{region}:{account}:*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:*"],
                resources=["arn:aws:logs:*:*:*"],
            )
        )
        
        # Lambda for the new stage
        lambda_function = _lambda.Function(
            self,"hawkbitAssignSoftwareToDevice",
            function_name="hawkbitAssignSoftwareToDevice",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("./lambda/hawkbitAssignSoftwareToDevice.zip"),
            handler="hawkbitAssignSoftwareToDevice.lambda_handler",
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_DAY,
            timeout=Duration.seconds(60),
        )

        hawkbitAssignSoftwareToDevice_output = pipeline.Artifact("hawkbitAssignSoftwareToDeviceArtifacts")

        invoke_action = codepipeline_actions.LambdaInvokeAction(
            action_name="hawkbitAssignSoftwareToDevice",
            lambda_=lambda_function,
            inputs=[hawkbitDeploySoftwareOnHawkbitServer_output],
            user_parameters_string="#{LambdaVariables.DistributioSet}",
            outputs=[hawkbitAssignSoftwareToDevice_output],
        )

        # New stage for Deploying Software on Hawkbit Server
        hawkbitAssignSoftwareToDevice_stage = pipeline.StageProps(
            stage_name="hawkbitAssignSoftwareToDevice",
            actions=[invoke_action],
            transition_disabled_reason="Stage is not needed now",
            transition_to_enabled=False
        )

        # Creates an AWS CodePipeline with source, build, and deploy stages
        pipeline_istance = pipeline.Pipeline(
            self, "hawkbit-device",
            pipeline_name="hawkbit-device",
            artifact_bucket=artifact_bucket,
            stages=[source_stage, build_stage, hawkbitDeploySoftwareOnHawkbitServer_stage, hawkbitRolloutSoftwareOnDevice, hawkbitAssignSoftwareToDevice_stage]
        )
        cpp_custom_pipeline.node.add_dependency(pipeline_istance)