import * as cdk from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as budgets from 'aws-cdk-lib/aws-budgets';
import { BaseStack, BaseStackProps } from './base-stack';

export class MonitoringStack extends BaseStack {
    constructor(scope: cdk.App, id: string, props: BaseStackProps) {
        super(scope, id, props);

        // Create SNS Topic for cost alerts
        const costAlertTopic = new sns.Topic(this, 'CostAlertTopic', {
            topicName: this.createNamePrefix('cost-alerts'),
            displayName: 'Daily AWS Cost Alerts',
        });

        // Add email subscription
        costAlertTopic.addSubscription(
            new subscriptions.EmailSubscription('rayc9823@gmail.com')
        );

        // Create daily cost budget
        new budgets.CfnBudget(this, 'DailyCostBudget', {
            budget: {
                budgetName: this.createNamePrefix('daily-cost-tracking'),
                budgetType: 'COST',
                timeUnit: 'DAILY',
                budgetLimit: {
                    amount: 10, // Set a default of $10 per day
                    unit: 'USD',
                },
            },
            notificationsWithSubscribers: [
                {
                    notification: {
                        comparisonOperator: 'GREATER_THAN',
                        notificationType: 'ACTUAL',
                        threshold: 100,
                        thresholdType: 'PERCENTAGE',
                    },
                    subscribers: [
                        {
                            address: costAlertTopic.topicArn,
                            subscriptionType: 'SNS',
                        },
                    ],
                },
                {
                    notification: {
                        comparisonOperator: 'GREATER_THAN',
                        notificationType: 'FORECASTED',
                        threshold: 100,
                        thresholdType: 'PERCENTAGE',
                    },
                    subscribers: [
                        {
                            address: costAlertTopic.topicArn,
                            subscriptionType: 'SNS',
                        },
                    ],
                },
            ],
        });

        // Output the SNS topic ARN
        new cdk.CfnOutput(this, 'CostAlertTopicArn', {
            value: costAlertTopic.topicArn,
            description: 'ARN of SNS topic for cost alerts',
        });
    }
} 