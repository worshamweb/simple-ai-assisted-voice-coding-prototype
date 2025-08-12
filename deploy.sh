#!/bin/bash

# Voice-Assisted AI Coding Prototype Deployment Script

set -e

STACK_NAME="voice-ai-coding-prototype"
REGION="us-east-1"  # Change as needed

echo "🚀 Deploying Voice-Assisted AI Coding Prototype..."

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Build the application
echo "📦 Building SAM application..."
cd infrastructure
sam build

# Deploy the application
echo "🚀 Deploying to AWS..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides Environment=dev \
    --confirm-changeset

# Get outputs
echo "✅ Deployment complete!"
echo ""
echo "📋 Stack Outputs:"
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output text)

echo "$OUTPUTS" | column -t

# Extract key values for easy access
API_ENDPOINT=$(echo "$OUTPUTS" | grep "ApiEndpoint" | awk '{print $2}')
WEBSITE_URL=$(echo "$OUTPUTS" | grep "WebsiteURL" | awk '{print $2}')
WEBSITE_BUCKET=$(echo "$OUTPUTS" | grep "WebsiteBucket" | awk '{print $2}')

# Deploy the test client to S3
echo ""
echo "🌐 Deploying test client to S3..."
cd ..

# Update the test client with the API endpoint
sed "s|placeholder=\"https://your-api-gateway-url/dev/process-voice\"|value=\"$API_ENDPOINT/process-voice\"|g" test_client.html > test_client_configured.html

# Upload to S3
aws s3 cp test_client_configured.html s3://$WEBSITE_BUCKET/index.html --region $REGION
rm test_client_configured.html

echo ""
echo "🎯 Deployment Summary:"
echo "API Endpoint: $API_ENDPOINT"
echo "Website URL:  $WEBSITE_URL"
echo ""
echo "🧪 To run tests:"
echo "export API_ENDPOINT=\"$API_ENDPOINT\""
echo "export WEBSITE_URL=\"$WEBSITE_URL\""
echo "./run_tests.sh"
echo ""
echo "⚠️  Remember: This uses paid services (Transcribe, Polly, Bedrock)"
echo "   Keep sessions short during development to minimize costs."