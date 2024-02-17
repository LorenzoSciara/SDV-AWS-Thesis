import os

from aws_cdk import (
    aws_iot as iot,
    cloud_assembly_schema as cloud_assembly_schema,
    custom_resources as cr,
    Stack,
    Aws,
)

from constructs import Construct
import aws_cdk as cdk
from function.cert_handler import cert_handler

class HawkbitDeviceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, status:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
        # Environment variables
        account=Aws.ACCOUNT_ID
        region=Aws.REGION

        print(status)

        # Create an IoT Thing
        cfn_thing=iot.CfnThing(self, "HawkbitDevice",
            thing_name="HawkbitDevice001"
        )
        
        # Create a policy of the certificate
        cfn_policy = iot.CfnPolicy(self, "CfnPolicy",
            policy_document={
                "Version":"2012-10-17",
                "Statement":[
                    {
                        "Effect":"Allow",
                        "Action":[
                            "iot:Connect"
                        ],
                        "Resource":[
                            f"arn:aws:iot:"+region+":"+account+":client/"+cfn_thing.thing_name
                            ]
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Publish"
                        ],
                        "Resource":[f"arn:aws:iot:"+region+":"+account+":topic/*"]
                    }
                ]
            },
            policy_name=f"{cfn_thing.thing_name}IoTCertPolicy",
        )

        '''create_certificate_resource = cr.AwsCustomResource(self, "CreateCertificateResource",
            on_create=cr.AwsSdkCall(
                service="Iot",
                action="CreateKeysAndCertificate",
                parameters={
                    "setAsActive": f"{True}"
                },
                physical_resource_id=cr.PhysicalResourceId.of("create_certificate_resource")
            ),
            # Will ignore any resource and use the assumedRoleArn as resource and 'sts:AssumeRole' for service:action
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )'''

        # Creation of certificate with boto3
        if (status=="deploy"):
            certificate=cert_handler(cfn_thing.thing_name)
        else:
            certificate={"Data": {"certificateId": "Null"}}
        print(f"{certificate['Data']['certificateId']}")

        # Connect the certificate and policy
        policy_attchment = iot.CfnPolicyPrincipalAttachment(
            self,
            id=cfn_thing.thing_name+"PolicyPrincipalAttachment",
            policy_name=cfn_policy.policy_name,
            principal=f"arn:aws:iot:{region}:{account}:cert/{certificate['Data']['certificateId']}",
        )
        policy_attchment.add_dependency(cfn_policy)

        # Connect the IoT thing and certificate
        thing_attchmnt = iot.CfnThingPrincipalAttachment(
            self,
            id=cfn_thing.thing_name+"ThingPrincipalAttachment",
            principal=f"arn:aws:iot:{region}:{account}:cert/{certificate['Data']['certificateId']}",
            thing_name=cfn_thing.thing_name,
        )
        thing_attchmnt.add_dependency(cfn_thing)

        deactive_certificate_resource = cr.AwsCustomResource(self, "DeactiveCertificateResource",
            on_delete=cr.AwsSdkCall(
                service="Iot",
                action="UpdateCertificate",
                parameters={
                    "certificateId": f"{certificate['Data']['certificateId']}",
                    "newStatus": "INACTIVE",
                },
            ),
            # Will ignore any resource and use the assumedRoleArn as resource and 'sts:AssumeRole' for service:action
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )

        delete_certificate_resource = cr.AwsCustomResource(self, "DeleteCertificateResource",
            on_delete=cr.AwsSdkCall(
                service="Iot",
                action="DeleteCertificate",
                parameters={
                    "certificateId": f"{certificate['Data']['certificateId']}",
                    "forceDelete": f"{True}"
                },
            ),
            # Will ignore any resource and use the assumedRoleArn as resource and 'sts:AssumeRole' for service:action
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )
        deactive_certificate_resource.node.add_dependency(delete_certificate_resource)
