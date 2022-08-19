#!/usr/bin/env python3

import aws_cdk as cdk

from ecs.ecs_stack import EcsStack


app = cdk.App()
EcsStack(app, "ecs")

app.synth()
