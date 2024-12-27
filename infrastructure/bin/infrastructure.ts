#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { NetworkStack } from '../lib/stacks/network-stack';
import { BackendStack } from '../lib/stacks/backend-stack';
import { FrontendStack } from '../lib/stacks/frontend-stack';
import { EmailUsageStack } from '../lib/stacks/email-usage-stack';

console.log('Starting CDK app...');

const app = new cdk.App();

console.log('Created CDK app');

// Common props for all stacks
const commonProps = {
    projectName: 'smart-dine',
    environment: 'dev',
    env: {
        account: '863518414064',
        region: 'ap-southeast-2'
    }
};

console.log('Common props:', commonProps);

try {
    // Create Network Stack
    console.log('Creating network stack...');
    const networkStack = new NetworkStack(app, 'SmartDineNetworkStack', {
        ...commonProps,
        maxAzs: 2,
        natGateways: 1,
        description: 'Smart Dine Network Infrastructure'
    });
    console.log('Network stack created');

    // Create Backend Stack
    console.log('Creating backend stack...');
    const backendStack = new BackendStack(app, 'SmartDineBackendStack', {
        ...commonProps,
        vpc: networkStack.vpc,
        containerPort: 3000,
        cpu: 256,
        memoryLimitMiB: 512,
        minCapacity: 1,
        maxCapacity: 4,
        description: 'Smart Dine Backend Service'
    });
    backendStack.addDependency(networkStack);
    console.log('Backend stack created');

    // Create Frontend Stack
    console.log('Creating frontend stack...');
    const frontendStack = new FrontendStack(app, 'SmartDineFrontendStack', {
        ...commonProps,
        description: 'Smart Dine Frontend Application'
    });
    console.log('Frontend stack created');

    // Add email usage stack
    new EmailUsageStack(app, 'SmartDineEmailUsageStack', {
        ...commonProps,
        description: 'Smart Dine Email Usage Notifications'
    });

    console.log('Synthesizing...');
    app.synth();
    console.log('Synthesis complete');
} catch (error) {
    console.error('Error:', error);
    process.exit(1);
}