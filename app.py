#!/usr/bin/env python3

import aws_cdk as cdk
import os
from ecs.ecs_stack import EcsStack

app = cdk.App()
EcsStack(app, "ecs", env={"region": "eu-central-1", "account": os.environ['CDK_DEFAULT_ACCOUNT']})

app.synth()

