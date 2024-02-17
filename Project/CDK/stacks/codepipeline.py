from constructs import Construct

from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as pipeline,
    aws_codepipeline_actions as pipelineactions,
    aws_s3 as s3,
    aws_codepipeline_actions as codepipeline_actions,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_iam as iam,
    Duration,
    Aws,
)

class HawkbitPipelineStack(Stack):
     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account=Aws.ACCOUNT_ID
        region=Aws.REGION

        # Creates an AWS CodeCommit repository
        code_repo = codecommit.Repository(
            self, "CodeRepo",
            repository_name="HawkbitDevice",
            # Copies files from app directory to the repo as the initial commit
            code=codecommit.Code.from_zip_file("./repos/Lorenzo_Device.zip", "master")
        )

        # Creates new pipeline artifacts
        source_artifact = pipeline.Artifact("SourceArtifact")
        build_artifact = pipeline.Artifact("BuildArtifact")

        #retrieve bucket for pipeline artifacts
        artifact_bucket = s3.Bucket.from_bucket_arn(self, f"codepipeline-{region}-833521754963", f"arn:aws:s3:::codepipeline-{region}-833521754963") #default codepipeline bucket

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
        hawkbit_test = codebuild.Project(
            self, "HawkbitTests",
            build_spec=codebuild.BuildSpec.from_source_filename(
                "buildspec.yml"),
            source=codebuild.Source.code_commit(
                repository=code_repo,
                branch_or_ref="master"
            ),
            environment=codebuild.BuildEnvironment(
                privileged=True
            ),
            project_name="hawkbit_test"
        )

        # Creates the test build stage for CodePipeline
        build_stage = pipeline.StageProps(
            stage_name="Test",
            actions=[
                pipelineactions.CodeBuildAction(
                    action_name="Test",
                    input=pipeline.Artifact("SourceArtifact"),
                    project=hawkbit_test,
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
            inputs=[source_artifact],
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