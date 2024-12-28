import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as iam from 'aws-cdk-lib/aws-iam';
import { BaseStack, BaseStackProps } from './base-stack';

export interface FrontendStackProps extends BaseStackProps {
    // Add any frontend-specific props here
}

export class FrontendStack extends BaseStack {
    public readonly bucket: s3.Bucket;
    public readonly distribution: cloudfront.Distribution;

    constructor(scope: cdk.App, id: string, props: FrontendStackProps) {
        super(scope, id, props);

        // Create S3 bucket for website hosting
        this.bucket = new s3.Bucket(this, 'WebsiteBucket', {
            bucketName: this.createNamePrefix('website'),
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            removalPolicy: cdk.RemovalPolicy.DESTROY, // For dev environment
            autoDeleteObjects: true, // For dev environment
            encryption: s3.BucketEncryption.S3_MANAGED,
        });

        // Create Origin Access Identity for CloudFront
        const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OAI', {
            comment: `OAI for ${this.createNamePrefix('website')}`,
        });

        // Grant read access to CloudFront
        this.bucket.addToResourcePolicy(new iam.PolicyStatement({
            actions: ['s3:GetObject'],
            resources: [this.bucket.arnForObjects('*')],
            principals: [new iam.CanonicalUserPrincipal(originAccessIdentity.cloudFrontOriginAccessIdentityS3CanonicalUserId)],
        }));

        // Create CloudFront distribution
        this.distribution = new cloudfront.Distribution(this, 'Distribution', {
            defaultBehavior: {
                origin: new origins.S3Origin(this.bucket, { originAccessIdentity }),
                viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
                cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
                responseHeadersPolicy: new cloudfront.ResponseHeadersPolicy(this, 'SecurityHeadersPolicy', {
                    responseHeadersPolicyName: this.createNamePrefix('security-headers'),
                    securityHeadersBehavior: {
                        contentSecurityPolicy: {
                            contentSecurityPolicy: "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
                            override: true,
                        },
                        strictTransportSecurity: {
                            accessControlMaxAge: cdk.Duration.days(365),
                            includeSubdomains: true,
                            preload: true,
                            override: true,
                        },
                        contentTypeOptions: { override: true },
                        frameOptions: { frameOption: cloudfront.HeadersFrameOption.DENY, override: true },
                        referrerPolicy: { referrerPolicy: cloudfront.HeadersReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN, override: true },
                        xssProtection: { protection: true, modeBlock: true, override: true },
                    },
                }),
            },
            errorResponses: [
                {
                    httpStatus: 404,
                    responseHttpStatus: 200,
                    responsePagePath: '/index.html',
                },
                {
                    httpStatus: 403,
                    responseHttpStatus: 200,
                    responsePagePath: '/index.html',
                },
            ],
            defaultRootObject: 'index.html',
            enableLogging: true,
            minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            priceClass: cloudfront.PriceClass.PRICE_CLASS_ALL,
        });

        // Output the CloudFront URL
        new cdk.CfnOutput(this, 'DistributionDomainName', {
            value: this.distribution.distributionDomainName,
            description: 'CloudFront Distribution Domain Name',
        });
    }
} 