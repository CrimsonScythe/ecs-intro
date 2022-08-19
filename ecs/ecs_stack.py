import json
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ecs_patterns,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager
)
import os

class EcsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, id="myVPC", cidr="10.0.0.0/16")
        rdsSecGroup = ec2.SecurityGroup(self, id="rdssecgroup", vpc=vpc)
        fargateSecGroup = ec2.SecurityGroup(self, id="fargatesecgroup", vpc=vpc)

        rdsSecGroup.connections.allow_from(fargateSecGroup, ec2.Port.all_tcp())

        templatedSecret = secretsmanager.Secret(
            self,
            id="templatedSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({'username': "postgres"}),
                generate_string_key='password',
                exclude_characters="/@\" "
                )
            )
        
        rdsInstance = rds.DatabaseInstance(
            self,
            id="myDB",
            credentials=rds.Credentials.from_secret(templatedSecret),
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            instance_type=ec2.InstanceType.of(instance_class=ec2.InstanceClass.T3, instance_size=ec2.InstanceSize.MICRO),
            vpc=vpc,
            database_name="ecs",
            security_groups=[rdsSecGroup],
            )

        fargateService = aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            id="mycluster",
            vpc=vpc,
            cpu=256,
            memory_limit_mib=512,
            public_load_balancer=True,
            assign_public_ip=True,
            security_groups=[fargateSecGroup],
            task_image_options=aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("./"),
                secrets={
                    "username": ecs.Secret.from_secrets_manager(templatedSecret, "username"),
                    "password": ecs.Secret.from_secrets_manager(templatedSecret, "password")
                },
                environment={
                    "endpoint": rdsInstance.db_instance_endpoint_address,
                }
                
                )
        ).node.add_dependency(rdsInstance)

       

        
