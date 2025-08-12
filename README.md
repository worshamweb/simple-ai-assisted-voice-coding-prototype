# Voice-Assisted AI Coding Prototype

An MVP for conversational AI pair programming that elevates developers of any skill level.

## Vision
Create a voice-interactive AI assistant that not only generates code but actively improves developer requests, identifies security issues, suggests best practices, and asks clarifying questions to ensure high-quality, extensible solutions.

## Key Features
- **Voice-First Interface**: Natural conversation with AI
- **Expert Developer Advisor**: Uses Claude 3 Haiku via Bedrock with specialized system prompts that act as a senior developer with 15+ years of experience. The AI actively identifies security vulnerabilities, suggests modern architectural patterns, asks clarifying questions for vague requirements, and guides developers toward scalable, maintainable solutions rather than just implementing what's requested.
- **Conversation Memory**: Maintains context across interactions
- **Security-Focused**: Built-in vulnerability detection and secure coding guidance
- **Comprehensive Testing**: Unit, integration, and E2E test coverage
- **Production-Ready CI/CD**: Automated deployment and quality gates

## Architecture
- **API Gateway**: REST endpoints for voice processing
- **Lambda Functions**: Core processing logic (Python 3.11)
- **Amazon Transcribe**: Speech-to-text conversion
- **Amazon Bedrock**: AI processing with Claude 3 Haiku
- **Amazon Polly**: Text-to-speech with Neural voices
- **S3**: Temporary audio storage + static website hosting
- **DynamoDB**: Conversation history with TTL
- **CloudFormation/SAM**: Infrastructure as Code

## Quick Start

```bash
# Deploy infrastructure
./deploy.sh

# Run tests
export API_ENDPOINT="<from deployment output>"
export WEBSITE_URL="<from deployment output>"
./run_tests.sh
```

## Development Workflow

1. **Local Development**: Unit tests with mocked AWS services
2. **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions
3. **Environment Promotion**: `develop` → dev environment, `main` → production
4. **Quality Gates**: Security scanning, automated testing, deployment validation

## Testing Strategy

- **Unit Tests**: Fast, isolated, mocked AWS services (`tests/unit/`)
- **Integration Tests**: Real API endpoints and AWS services (`tests/integration/`)
- **E2E Tests**: Full browser automation with Selenium (`tests/e2e/`)
- **Security Scanning**: Bandit (code analysis) + Safety (dependency vulnerabilities)
- **CI/CD Integration**: All tests run automatically on push/PR

## Cost Breakdown ⚠️

**Free Tier Services:**
- API Gateway: 1M requests/month
- Lambda: 1M requests + 400K GB-seconds/month
- S3: 5GB storage + 20K GET requests/month
- DynamoDB: 25GB storage + 25 RCU/WCU

**Paid Services (Development Costs):**
- **Transcribe**: ~$0.024/minute (~$1.44/hour of voice)
- **Polly Neural**: ~$16/1M characters (~$0.016 per typical response)
- **Bedrock Claude 3 Haiku**: ~$0.25/1M input tokens, ~$1.25/1M output tokens
- **Estimated dev cost**: ~$5-10/day for active development

**Cost Optimization Features:**
- S3 lifecycle policy: Audio files deleted after 1 day
- DynamoDB TTL: Conversations expire after 7 days
- Cheapest Bedrock model (Haiku) for development
- Unit tests use mocks (no AWS costs)

## Development Approach
Using "vibe coding" methodology with quality guardrails - rapid iteration with AI assistance while maintaining professional standards through automated testing, security scanning, and expert AI guidance.

## Project Structure

```
├── infrastructure/          # SAM templates
│   └── template.yaml       # Complete AWS infrastructure
├── src/                    # Lambda functions
│   ├── voice_processor.py  # Main processing pipeline
│   ├── api_handler.py      # API Gateway integration
│   └── requirements.txt    # Python dependencies
├── tests/                  # Comprehensive test suite
│   ├── unit/              # Isolated unit tests
│   ├── integration/       # API integration tests
│   ├── e2e/               # End-to-end browser tests
│   └── requirements.txt   # Test dependencies
├── .github/workflows/     # CI/CD pipeline
│   └── ci-cd.yml          # Automated testing & deployment
├── deploy.sh              # One-click deployment
├── run_tests.sh           # Test runner
├── test_client.html       # Voice interface
└── pytest.ini            # Test configuration
```

## Getting Started

### Prerequisites
- AWS CLI configured with appropriate permissions
- SAM CLI installed
- Python 3.11+
- Node.js (for E2E tests)

### Setup GitHub Actions (Optional)
1. Fork this repository
2. Add AWS credentials to GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. Push to `develop` branch for dev deployment
4. Push to `main` branch for production deployment

### Local Development
```bash
# Install dependencies
pip install -r src/requirements.txt
pip install -r tests/requirements.txt

# Run unit tests (no AWS costs)
pytest tests/unit/

# Deploy and test
./deploy.sh
./run_tests.sh
```