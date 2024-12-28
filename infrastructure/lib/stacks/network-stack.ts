import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { BaseStack, BaseStackProps } from './base-stack';

export interface NetworkStackProps extends BaseStackProps {
    maxAzs?: number;
    natGateways?: number;
}

export class NetworkStack extends BaseStack {
    public readonly vpc: ec2.Vpc;

    constructor(scope: Construct, id: string, props: NetworkStackProps) {
        super(scope, id, props);

        // Create VPC
        this.vpc = new ec2.Vpc(this, this.createNamePrefix('vpc'), {
            maxAzs: props.maxAzs || 2,
            natGateways: props.natGateways || 1,
            subnetConfiguration: [
                {
                    name: 'Public',
                    subnetType: ec2.SubnetType.PUBLIC,
                    cidrMask: 24,
                },
                {
                    name: 'Private',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidrMask: 24,
                },
                {
                    name: 'Isolated',
                    subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
                    cidrMask: 24,
                }
            ]
        });

        // Add VPC Flow Logs
        this.vpc.addFlowLog(this.createNamePrefix('flow-log'), {
            destination: ec2.FlowLogDestination.toCloudWatchLogs(),
            trafficType: ec2.FlowLogTrafficType.ALL
        });

        // Output VPC ID
        new cdk.CfnOutput(this, 'VpcId', {
            value: this.vpc.vpcId,
            description: 'VPC ID',
            exportName: this.createNamePrefix('vpc-id')
        });
    }
} 