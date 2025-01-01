import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codedeploy from 'aws-cdk-lib/aws-codedeploy';
import * as iam from 'aws-cdk-lib/aws-iam';
import { BaseStack, BaseStackProps } from './base-stack';

export interface BackendStackProps extends BaseStackProps {
    vpc: ec2.IVpc;
    containerPort: number;
    cpu: number;
    memoryLimitMiB: number;
    minCapacity: number;
    maxCapacity: number;
}

export class BackendStack extends BaseStack {
    public readonly service: ecs.FargateService;
    public readonly loadBalancer: elbv2.ApplicationLoadBalancer;

    constructor(scope: cdk.App, id: string, props: BackendStackProps) {
        super(scope, id, props);

        // Create ECS Cluster
        const cluster = new ecs.Cluster(this, 'Cluster', {
            vpc: props.vpc,
            clusterName: this.createNamePrefix('cluster'),
            containerInsights: true,
        });

        // Create ALB Security Group
        const albSecurityGroup = new ec2.SecurityGroup(this, 'AlbSecurityGroup', {
            vpc: props.vpc,
            allowAllOutbound: true,
            description: 'Security group for smart-dine ALB'
        });

        // Allow inbound HTTP from anywhere to ALB
        albSecurityGroup.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(80),
            'Allow HTTP traffic from anywhere'
        );

        // Create ALB
        this.loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'ALB', {
            vpc: props.vpc,
            internetFacing: true,
            loadBalancerName: this.createNamePrefix('alb'),
            securityGroup: albSecurityGroup
        });

        // Create target group
        const targetGroup = new elbv2.ApplicationTargetGroup(this, 'TargetGroup', {
            vpc: props.vpc,
            port: props.containerPort,
            protocol: elbv2.ApplicationProtocol.HTTP,
            targetType: elbv2.TargetType.IP,
            healthCheck: {
                path: '/',
                interval: cdk.Duration.seconds(60),
                timeout: cdk.Duration.seconds(30),
                healthyThresholdCount: 2,
                unhealthyThresholdCount: 5,
                healthyHttpCodes: '200,302,404',
            },
            deregistrationDelay: cdk.Duration.seconds(30),
        });

        // Create ALB listener
        this.loadBalancer.addListener('Listener', {
            port: 80,
            protocol: elbv2.ApplicationProtocol.HTTP,
            defaultTargetGroups: [targetGroup],
        });

        // Create ECR Repository
        const repository = new ecr.Repository(this, 'Repository', {
            repositoryName: this.createNamePrefix('backend'),
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteImages: true,
        });

        // Create Fargate Task Definition
        const taskDef = new ecs.FargateTaskDefinition(this, 'ServiceTask', {
            cpu: props.cpu,
            memoryLimitMiB: props.memoryLimitMiB,
        });

        // Add container
        taskDef.addContainer('FastAPI', {
            image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
            containerName: this.createNamePrefix('backend'),
            portMappings: [{ containerPort: 80 }],
            logging: ecs.LogDrivers.awsLogs({
                streamPrefix: this.createNamePrefix('backend'),
                logRetention: logs.RetentionDays.ONE_MONTH,
            }),
            environment: {
                ENVIRONMENT: this.environmentName,
            },
            healthCheck: {
                command: ['CMD-SHELL', 'curl -f http://localhost/health || exit 1'],
                interval: cdk.Duration.seconds(30),
                timeout: cdk.Duration.seconds(5),
                retries: 3,
                startPeriod: cdk.Duration.seconds(60),
            },
        });

        // Create ECS Service Security Group
        const serviceSecurityGroup = new ec2.SecurityGroup(this, 'ServiceSecurityGroup', {
            vpc: props.vpc,
            allowAllOutbound: true,
            description: 'Security group for smart-dine backend service'
        });

        // Allow inbound from ALB to ECS Service
        serviceSecurityGroup.addIngressRule(
            ec2.Peer.securityGroupId(albSecurityGroup.securityGroupId),
            ec2.Port.tcp(80),
            'Allow traffic from ALB'
        );

        // Create Fargate Service
        this.service = new ecs.FargateService(this, 'Service', {
            cluster,
            taskDefinition: taskDef,
            serviceName: this.createNamePrefix('backend'),
            desiredCount: props.minCapacity,
            assignPublicIp: false,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
            securityGroups: [serviceSecurityGroup],
            healthCheckGracePeriod: cdk.Duration.seconds(60),
            deploymentController: {
                type: ecs.DeploymentControllerType.CODE_DEPLOY
            }
        });

        // Attach the service to the target group
        targetGroup.addTarget(this.service);

        // Setup Auto Scaling
        const scaling = this.service.autoScaleTaskCount({
            minCapacity: props.minCapacity,
            maxCapacity: props.maxCapacity,
        });

        scaling.scaleOnCpuUtilization('CpuScaling', {
            targetUtilizationPercent: 70,
            scaleInCooldown: cdk.Duration.seconds(60),
            scaleOutCooldown: cdk.Duration.seconds(60),
        });

        // Get GitHub token from Secrets Manager
        const githubToken = secretsmanager.Secret.fromSecretNameV2(this, 'GitHubToken', 'github-token');

        // Create GitHub source credentials
        const sourceCredentials = new codebuild.CfnSourceCredential(this, 'GitHubCredentials', {
            authType: 'PERSONAL_ACCESS_TOKEN',
            serverType: 'GITHUB',
            token: githubToken.secretValue.unsafeUnwrap()
        });

        // Create CodeBuild Project
        const buildProject = new codebuild.Project(this, 'BuildProject', {
            projectName: this.createNamePrefix('build'),
            environment: {
                buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged: true,
                environmentVariables: {
                    AWS_DEFAULT_REGION: { value: 'ap-southeast-2' },
                    AWS_ACCOUNT_ID: { value: this.account },
                    REPOSITORY_URI: { value: repository.repositoryUri }
                }
            },
            source: codebuild.Source.gitHub({
                owner: this.node.tryGetContext('github_owner'),
                repo: this.node.tryGetContext('github_repo'),
                webhook: false,
                branchOrRef: 'mainline'
            })
        });

        // Grant necessary permissions to CodeBuild
        buildProject.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'ecr:GetAuthorizationToken',
                'ecr:BatchCheckLayerAvailability',
                'ecr:GetDownloadUrlForLayer',
                'ecr:GetRepositoryPolicy',
                'ecr:DescribeRepositories',
                'ecr:ListImages',
                'ecr:DescribeImages',
                'ecr:BatchGetImage',
                'ecr:InitiateLayerUpload',
                'ecr:UploadLayerPart',
                'ecr:CompleteLayerUpload',
                'ecr:PutImage'
            ],
            resources: ['*']
        }));

        // Create CodeDeploy Service Role
        const codeDeployServiceRole = new iam.Role(this, 'CodeDeployServiceRole', {
            assumedBy: new iam.ServicePrincipal('codedeploy.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AWSCodeDeployRoleForECS')
            ]
        });

        // Create CodeDeploy Application
        const application = new codedeploy.EcsApplication(this, 'CodeDeployApplication', {
            applicationName: this.createNamePrefix('app'),
        });

        // Create CodeDeploy Deployment Group
        const deploymentGroup = new codedeploy.EcsDeploymentGroup(this, 'CodeDeployDeploymentGroup', {
            application,
            deploymentGroupName: this.createNamePrefix('deployment-group'),
            service: this.service,
            deploymentConfig: codedeploy.EcsDeploymentConfig.ALL_AT_ONCE,
            role: codeDeployServiceRole,
            blueGreenDeploymentConfig: {
                deploymentApprovalWaitTime: cdk.Duration.minutes(5),
                terminationWaitTime: cdk.Duration.minutes(5),
                listener: this.loadBalancer.listeners[0],
                blueTargetGroup: targetGroup,
                greenTargetGroup: new elbv2.ApplicationTargetGroup(this, 'GreenTargetGroup', {
                    vpc: props.vpc,
                    port: 80,
                    protocol: elbv2.ApplicationProtocol.HTTP,
                    targetType: elbv2.TargetType.IP,
                    healthCheck: {
                        path: '/',
                        interval: cdk.Duration.seconds(60),
                        timeout: cdk.Duration.seconds(30),
                        healthyThresholdCount: 2,
                        unhealthyThresholdCount: 5,
                        healthyHttpCodes: '200,302,404',
                    },
                    deregistrationDelay: cdk.Duration.seconds(30),
                })
            }
        });

        // Source Stage
        const sourceOutput = new codepipeline.Artifact('SourceOutput');
        const sourceAction = new codepipeline_actions.GitHubSourceAction({
            actionName: 'GitHub_Source',
            owner: this.node.tryGetContext('github_owner'),
            repo: this.node.tryGetContext('github_repo'),
            branch: 'mainline',
            oauthToken: githubToken.secretValue,
            output: sourceOutput,
            trigger: codepipeline_actions.GitHubTrigger.WEBHOOK,
            runOrder: 1
        });

        // Build Stage with artifacts
        const buildOutput = new codepipeline.Artifact('BuildOutput');
        const buildAction = new codepipeline_actions.CodeBuildAction({
            actionName: 'Build',
            project: buildProject,
            input: sourceOutput,
            outputs: [buildOutput],
            runOrder: 1
        });

        // Deploy Stage using CodeDeploy
        const deployAction = new codepipeline_actions.CodeDeployEcsDeployAction({
            actionName: 'Deploy',
            deploymentGroup,
            appSpecTemplateFile: buildOutput.atPath('appspec.yaml'),
            taskDefinitionTemplateFile: buildOutput.atPath('taskdef.json'),
            runOrder: 1
        });

        // Create Pipeline
        const pipeline = new codepipeline.Pipeline(this, 'Pipeline', {
            pipelineName: this.createNamePrefix('pipeline'),
            crossAccountKeys: false,
            stages: [
                {
                    stageName: 'Source',
                    actions: [sourceAction],
                },
                {
                    stageName: 'Build',
                    actions: [buildAction],
                },
                {
                    stageName: 'Deploy',
                    actions: [deployAction],
                },
            ],
        });

        // Grant pipeline role permission to read the GitHub token
        githubToken.grantRead(pipeline.role);

        // Output the Pipeline Console URL
        new cdk.CfnOutput(this, 'PipelineConsoleUrl', {
            value: `https://${this.region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/${pipeline.pipelineName}/view`,
            description: 'Pipeline Console URL',
        });

        // Grant ECR permissions to CodeBuild
        repository.grantPullPush(buildProject.role!);

        // Output the service security group ID
        new cdk.CfnOutput(this, 'ServiceSecurityGroupId', {
            value: serviceSecurityGroup.securityGroupId,
            description: 'Service Security Group ID',
        });

        // Output the task execution role ARN
        new cdk.CfnOutput(this, 'TaskExecutionRoleArn', {
            value: taskDef.executionRole!.roleArn,
            description: 'Task Execution Role ARN',
        });

        // Output the ALB DNS name
        new cdk.CfnOutput(this, 'LoadBalancerDNS', {
            value: this.loadBalancer.loadBalancerDnsName,
            description: 'Backend Load Balancer DNS Name',
        });
    }
} 