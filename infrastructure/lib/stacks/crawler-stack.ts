import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { BaseStack, BaseStackProps } from './base-stack';

export interface CrawlerStackProps extends BaseStackProps {
    vpc: cdk.aws_ec2.IVpc;
    scheduleExpression: string; // e.g., 'rate(1 day)'
}

export class CrawlerStack extends BaseStack {
    public readonly crawlerFunction: lambda.Function;
    public readonly restaurantTable: dynamodb.Table;

    constructor(scope: cdk.App, id: string, props: CrawlerStackProps) {
        super(scope, id, props);

        // Create DynamoDB table
        this.restaurantTable = new dynamodb.Table(this, 'RestaurantTable', {
            tableName: this.createNamePrefix('restaurants'),
            partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'location', type: dynamodb.AttributeType.STRING },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: cdk.RemovalPolicy.DESTROY, // For dev environment
            pointInTimeRecovery: true,
            timeToLiveAttribute: 'ttl',
        });

        // Add Global Secondary Indexes
        this.restaurantTable.addGlobalSecondaryIndex({
            indexName: 'byRating',
            partitionKey: { name: 'location', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'rating', type: dynamodb.AttributeType.NUMBER },
            projectionType: dynamodb.ProjectionType.ALL,
        });

        this.restaurantTable.addGlobalSecondaryIndex({
            indexName: 'byCuisine',
            partitionKey: { name: 'cuisine', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'rating', type: dynamodb.AttributeType.NUMBER },
            projectionType: dynamodb.ProjectionType.ALL,
        });

        // Create Lambda function
        this.crawlerFunction = new lambda.Function(this, 'CrawlerFunction', {
            functionName: this.createNamePrefix('crawler'),
            runtime: lambda.Runtime.NODEJS_18_X,
            handler: 'index.handler',
            code: lambda.Code.fromAsset('../crawler/dist'), // Will be created later
            timeout: cdk.Duration.minutes(5),
            memorySize: 1024,
            environment: {
                TABLE_NAME: this.restaurantTable.tableName,
                ENVIRONMENT: this.environmentName,
            },
            vpc: props.vpc,
            vpcSubnets: {
                subnetType: cdk.aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
            logRetention: logs.RetentionDays.ONE_MONTH,
            tracing: lambda.Tracing.ACTIVE,
        });

        // Grant DynamoDB permissions to Lambda
        this.restaurantTable.grantWriteData(this.crawlerFunction);

        // Add CloudWatch Events rule to trigger the crawler
        const rule = new events.Rule(this, 'CrawlerSchedule', {
            ruleName: this.createNamePrefix('crawler-schedule'),
            schedule: events.Schedule.expression(props.scheduleExpression),
            description: 'Schedule for running the restaurant data crawler',
        });

        rule.addTarget(new targets.LambdaFunction(this.crawlerFunction));

        // Add additional IAM permissions for crawler
        this.crawlerFunction.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'ec2:CreateNetworkInterface',
                'ec2:DescribeNetworkInterfaces',
                'ec2:DeleteNetworkInterface',
                'ec2:AssignPrivateIpAddresses',
                'ec2:UnassignPrivateIpAddresses'
            ],
            resources: ['*'],
        }));

        // Add CloudWatch metrics permissions
        this.crawlerFunction.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'cloudwatch:PutMetricData',
            ],
            resources: ['*'],
        }));

        // Output the function name and table name
        new cdk.CfnOutput(this, 'CrawlerFunctionName', {
            value: this.crawlerFunction.functionName,
            description: 'Crawler Lambda Function Name',
        });

        new cdk.CfnOutput(this, 'RestaurantTableName', {
            value: this.restaurantTable.tableName,
            description: 'Restaurant DynamoDB Table Name',
        });
    }
} 