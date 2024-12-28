import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface BaseStackProps extends cdk.StackProps {
    projectName: string;
    environment: string;
}

export abstract class BaseStack extends cdk.Stack {
    protected projectName: string;
    protected environmentName: string;

    constructor(scope: Construct, id: string, props: BaseStackProps) {
        super(scope, id, props);

        this.projectName = props.projectName;
        this.environmentName = props.environment;

        // Add common tags to all resources in the stack
        cdk.Tags.of(this).add('Project', this.projectName);
        cdk.Tags.of(this).add('Environment', this.environmentName);
        cdk.Tags.of(this).add('ManagedBy', 'CDK');
    }

    protected createNamePrefix(resourceName: string): string {
        return `${this.projectName}-${this.environmentName}-${resourceName}`;
    }

    protected validateProps(): void {
        if (!this.projectName) {
            throw new Error('Project name must be specified');
        }
        if (!this.environmentName) {
            throw new Error('Environment must be specified');
        }
    }
} 