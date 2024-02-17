from constructs import Construct

from aws_cdk import (
    Stack,
    aws_kinesis as kinesis,
    aws_iot as iot,
    aws_iam as iam,
    aws_timestream as timestream,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_lambda_event_sources as eventSources,
    Aws,
    CfnParameter,
    Duration,
)

class HawkbitTimestreamStack(Stack):
     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account=Aws.ACCOUNT_ID
        region=Aws.REGION

        # Kinsesis stream (take stream from device)
        kinesis_stream = kinesis.Stream(self, "hawkbitDeviceData",
            stream_mode=kinesis.StreamMode.ON_DEMAND,
            stream_name="hawkbitDeviceData"
        )

        device_to_kinesis_role = iam.Role(self, "hawkbitDeviceToKinesis", assumed_by=iam.ServicePrincipal("iot.amazonaws.com"),  role_name="hawkbitDeviceToKinesis")
        device_to_kinesis_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["kinesis:*"],
            resources=[kinesis_stream.stream_arn],
        ))

        device_to_kinesis_rule = iot.CfnTopicRule(self, "fromDeviceToKinesis",
            rule_name="HawkbitDeviceDataToKinesis",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                sql="SELECT * FROM 'device/HawkbitDevice001/telemetry'",
                actions=[iot.CfnTopicRule.ActionProperty(
                    kinesis=iot.CfnTopicRule.KinesisActionProperty(
                        role_arn=device_to_kinesis_role.role_arn,
                        stream_name=kinesis_stream.stream_name,
                        partition_key="${DeviceID}"
                    ),
                )]
            )
        )

        # Timestream database 
        memory_retention_param = CfnParameter(self, "memoryRetentionParam", type="Number",
                                                   min_value=1, max_value=8766, default=12,
                                                   description="The duration (in hours) for which data must be retained "
                                                               "in the memory store per table.")

        magnetic_retention_param = CfnParameter(self, "magneticRetentionParam", type="Number",
                                                     min_value=1, max_value=73000, default=5,
                                                     description="The duration (in days) for which data must be retained "
                                                                 "in the magnetic store per table.")

        database = timestream.CfnDatabase(self, id="hawkbitDevice", database_name="hawkbitDevice")

        retention = {
            "MemoryStoreRetentionPeriodInHours": memory_retention_param.value_as_number,
            "MagneticStoreRetentionPeriodInDays": magnetic_retention_param.value_as_number
        }

        ABS_table = timestream.CfnTable(self, "ABS", database_name=database.database_name,
            schema=timestream.CfnTable.SchemaProperty(
                composite_partition_key=[timestream.CfnTable.PartitionKeyProperty(
                    type="DIMENSION",
                    enforcement_in_record="REQUIRED",
                    name="DeviceID"
                )]
            ),
            retention_properties=retention,
            table_name="ABS"
        )
        ABS_table.add_dependency(database)

        Airbag_table = timestream.CfnTable(self, "Airbag", database_name=database.database_name,
            schema=timestream.CfnTable.SchemaProperty(
                composite_partition_key=[timestream.CfnTable.PartitionKeyProperty(
                    type="DIMENSION",
                    enforcement_in_record="REQUIRED",
                    name="DeviceID"
                )]
            ),
            retention_properties=retention,
            table_name="Airbag",
        )
        Airbag_table.add_dependency(database)

        AirConditioning_table = timestream.CfnTable(self, "AirConditioning", database_name=database.database_name,
            schema=timestream.CfnTable.SchemaProperty(
                composite_partition_key=[timestream.CfnTable.PartitionKeyProperty(
                    type="DIMENSION",
                    enforcement_in_record="REQUIRED",
                    name="DeviceID"
                )]
            ),
            retention_properties=retention,
            table_name="AirConditioning",
        )
        AirConditioning_table.add_dependency(database)

        Battery_table = timestream.CfnTable(self, "Battery", database_name=database.database_name,
            schema=timestream.CfnTable.SchemaProperty(
                composite_partition_key=[timestream.CfnTable.PartitionKeyProperty(
                    type="DIMENSION",
                    enforcement_in_record="REQUIRED",
                    name="DeviceID"
                )]
            ),
            retention_properties=retention,
            table_name="Battery",
        )
        Battery_table.add_dependency(database)

        Engine_table = timestream.CfnTable(self, "Engine", database_name=database.database_name,                               
            schema=timestream.CfnTable.SchemaProperty(
                composite_partition_key=[timestream.CfnTable.PartitionKeyProperty(
                    type="DIMENSION",
                    enforcement_in_record="REQUIRED",
                    name="DeviceID"
                )]
            ),
            retention_properties=retention,
            table_name="Engine",
        )
        Engine_table.add_dependency(database)

        HeatSeats_table = timestream.CfnTable(self, "HeatSeats", database_name=database.database_name,
            schema=timestream.CfnTable.SchemaProperty(
                composite_partition_key=[timestream.CfnTable.PartitionKeyProperty(
                    type="DIMENSION",
                    enforcement_in_record="REQUIRED",
                    name="DeviceID"
                )]
            ),
            retention_properties=retention,
            table_name="HeatSeats",
        )
        HeatSeats_table.add_dependency(database)

        # Lambda that transfer data from kinesis to timestream
        lambda_role = iam.Role(self, "hawkbitFromKinesisToTimestreamLambdaRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["timestream:*", "kms:DescribeKey", "s3:ListAllMyBuckets", "kinesis:DescribeStream", "kinesis:DescribeStreamSummary", "kinesis:GetRecords", "kinesis:GetShardIterator", "kinesis:ListShards", "kinesis:ListStreams", "kinesis:SubscribeToShard", "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=["*"],
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["kms:CreateGrant"],
                resources=["*"],
                conditions={"ForAnyValue:StringEquals": {
                        "kms:EncryptionContextKeys": "aws:timestream:database-name"
                    }}
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["kms:CreateGrant"],
                resources=["*"],
                conditions={"Bool": {
                        "kms:GrantIsForAWSResource": True
                    }}
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["kms:CreateGrant"],
                resources=["*"],
                conditions={"StringLike": {
                            "kms:ViaService": "timestream.*.amazonaws.com"
                    }}
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
                actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/hawkbitFromKinesisToTimestream:*"],
            )
        )
        
        lambda_function = _lambda.Function(
            self,"hawkbitFromKinesisToTimestream",
            function_name="hawkbitFromKinesisToTimestream",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("./lambda/hawkbitFromKinesisToTimestream.zip"),
            handler="hawkbitFromKinesisToTimestream.lambda_handler",
            role=lambda_role,
            timeout=Duration.seconds(60),
        )

        lambda_function.add_event_source(eventSources.KinesisEventSource(
            kinesis_stream,
            batch_size=100,  # default
            starting_position=_lambda.StartingPosition.LATEST
        ))
        