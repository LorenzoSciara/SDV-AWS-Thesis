from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    custom_resources as cr,
    aws_codecommit as codecommit,
    Aws,
    Stack,
)

from constructs import Construct

class HawkbitServerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Environment variables
        account=Aws.ACCOUNT_ID
        region=Aws.REGION

        # VPC
        vpc = ec2.Vpc(self, "VPC",
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC)]
            )

         # AMI
        generic_linux = ec2.MachineImage.generic_linux({
            'eu-west-1': 'ami-0905a3c97561e0b69',
        })

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))

        new_key = ec2.CfnKeyPair(self, "MyNewKeyPair",
            key_name="HawkbitServer",
        )

        # Instance
        instance = ec2.Instance(self, "Instance",
            instance_type=ec2.InstanceType("t2.small"),
            machine_image=generic_linux,
            vpc = vpc,
            role = role,
        )
        instance.connections.connections.allow_from_any_ipv4(ec2.Port.tcp(8080), "Allow inbound HTTP traffic")
        instance.connections.connections.allow_from_any_ipv4(ec2.Port.tcp(5672), "Allow inbound HTTP traffic")

        
        file_path = "./files/application.properties"
        with open(file_path, 'r') as file:
            application_properties = file.read()
        file_path = "./files/docker-compose.yml"
        with open(file_path, 'r') as file:
            docker_compose = file.read()
        
        instance.user_data.add_commands(
            'sudo apt-get update -y',
            'sudo apt-get install -y docker-compose',
            #f'sudo echo "{application_properties}" > /home/ubuntu/application.properties',
            #"sudo sed -i 's/\\//g' /home/ubuntu/application.properties",
            #'sudo sed -i "s/\[server_ip_address\]/$(sudo curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/g" /home/ubuntu/application.properties',
            f'sudo echo -e "{docker_compose}" > /home/ubuntu/docker-compose.yml',
            'sudo sed -i "s/\[server_ip_address\]/$(sudo curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/g" /home/ubuntu/docker-compose.yml',
            'sudo docker-compose -f /home/ubuntu/docker-compose.yml up -d',
        )

        create_param1 = cr.AwsCustomResource(self, "CreateParam1",
            on_create=cr.AwsSdkCall(
                service="SSM",
                action="PutParameter",
                parameters={
                    "Name": "/hawkbitServer/username",
                    "Value": "admin",
                    "Type": "SecureString"
                },
                physical_resource_id=cr.PhysicalResourceId.of("create_param1")
            ),
            on_delete=cr.AwsSdkCall(
                service="SSM",
                action="DeleteParameter",
                parameters={
                    "Name": "/hawkbitServer/username",
                },
                physical_resource_id=cr.PhysicalResourceId.of("delete_param1")
            ),
            # Will ignore any resource and use the assumedRoleArn as resource and 'sts:AssumeRole' for service:action
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )

        create_param2 = cr.AwsCustomResource(self, "CreateParam2",
            on_create=cr.AwsSdkCall(
                service="SSM",
                action="PutParameter",
                parameters={
                    "Name": "/hawkbitServer/password",
                    "Value": "admin",
                    "Type": "SecureString"
                },
                physical_resource_id=cr.PhysicalResourceId.of("create_param2")
            ),
            on_delete=cr.AwsSdkCall(
                service="SSM",
                action="DeleteParameter",
                parameters={
                    "Name": "/hawkbitServer/password",
                },
                physical_resource_id=cr.PhysicalResourceId.of("delete_param3")
            ),
            # Will ignore any resource and use the assumedRoleArn as resource and 'sts:AssumeRole' for service:action
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )

        create_param3 = cr.AwsCustomResource(self, "CreateParam3",
            on_create=cr.AwsSdkCall(
                service="SSM",
                action="PutParameter",
                parameters={
                    "Name": "/hawkbitServer/ip_address",
                    "Value": f"{instance.instance_public_ip}",
                    "Type": "String"
                },
                physical_resource_id=cr.PhysicalResourceId.of("create_param3")
            ),
            on_delete=cr.AwsSdkCall(
                service="SSM",
                action="DeleteParameter",
                parameters={
                    "Name": "/hawkbitServer/ip_address",
                },
                physical_resource_id=cr.PhysicalResourceId.of("delete_param3")
            ),
            # Will ignore any resource and use the assumedRoleArn as resource and 'sts:AssumeRole' for service:action
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )

        '''#ssm Secure variables
        param1 = ssm.StringParameter(self, "username",
            parameter_name="/hawkbitServer/username",
            string_value="admin",
            type=ssm.ParameterType.SECURE_STRING
        )

        param2 = ssm.StringParameter(self, "password",
            parameter_name="/hawkbitServer/password",
            string_value="admin",
            type=ssm.ParameterType.SECURE_STRING
        )

        param3 = ssm.StringParameter(self, "ip_address",
            parameter_name="/hawkbitServer/ip_address",
            string_value=f"{public_ip}",
        )'''