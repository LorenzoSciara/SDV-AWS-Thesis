import os

import aws_cdk as cdk
from function.cert_handler import cert_handler
from stacks.codepipeline import HawkbitPipelineStack
from stacks.timestream import HawkbitTimestreamStack
from stacks.device import HawkbitDeviceStack
from stacks.server import HawkbitServerStack
from stacks.codepipelineCpp import HawkbitPipelineCppStack


status = os.environ.get("STATUS", None)
if (status is None):
    raise ValueError("Insert status variable!")

app = cdk.App()
HawkbitDeviceStack(app, "HawkbitDeviceStack", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="eu-west-1"), status=status)
HawkbitServerStack(app, "HawkbitServerStack", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="eu-west-1"),)
#HawkbitPipelineStack(app, "HawkbitPipelineStack", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="eu-west-1"),) #Pipeline for Python codecommit and codedoploy
HawkbitTimestreamStack(app, "HawkbitTimestreamStack", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="eu-west-1"),)
HawkbitPipelineCppStack(app, "HawkbitPipelineCppStack", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="eu-west-1"),)
app.synth()