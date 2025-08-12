# Voice-Assisted AI Coding Prototype

An MVP for conversational AI pair programming that elevates developers of any skill level.

## Vision
Create a first gen prototype for a voice-interactive AI assistant that not only generates code but actively improves developer requests, identifies security issues, suggests best practices, and asks clarifying questions to ensure high-quality, extensible solutions.

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

### How Our Testing Works (Simple Explanation)

Think of testing like **quality control checkpoints** in a factory - each level catches different types of problems:

**Why We Test:**
- **Catch bugs early** - Fix problems before users see them
- **Prevent regressions** - Make sure new changes don't break existing features
- **Build confidence** - Know your code works before deploying
- **Save money** - Bugs caught early cost much less to fix

**Our 3-Layer Testing Approach:**

**1. Unit Tests** - Test individual pieces in isolation
- **What they do**: Test single functions like "does the voice processor handle audio correctly?"
- **How they work**: Use fake/mock AWS services so tests run fast and free
- **Like**: Testing each car part separately before assembly
- **Tools**: pytest (Python testing framework) + moto (AWS service mocking)
- **Speed**: Very fast (seconds), **Cost**: Free

**2. Integration Tests** - Test how pieces work together
- **What they do**: Test real API calls like "can the deployed system process a voice request?"
- **How they work**: Make actual HTTP requests to your deployed AWS infrastructure
- **Like**: Testing the assembled car on a test track
- **Tools**: pytest + requests (HTTP library)
- **Speed**: Slower (minutes), **Cost**: Small AWS usage fees

**3. End-to-End (E2E) Tests** - Test the complete user experience
- **What they do**: Simulate a real user clicking buttons and speaking into the microphone
- **How they work**: Control a web browser automatically to test the full workflow
- **Like**: Having a robot customer test drive the car
- **Tools**: Selenium (browser automation)
- **Speed**: Slowest (minutes), **Cost**: Minimal

**Security Testing Tools:**

- **Bandit**: Scans your Python code for common security issues
  - Finds problems like hardcoded passwords, unsafe functions
  - Like having a security guard review your code

- **Safety**: Checks if your dependencies have known vulnerabilities
  - Warns if you're using libraries with security flaws
  - Like checking if car parts have been recalled

**Testing Philosophy:**
- **Fast feedback loop**: Unit tests run in seconds for quick development
- **Realistic validation**: Integration tests use real AWS services
- **User-focused**: E2E tests ensure the actual user experience works
- **Security-first**: Automated scans catch vulnerabilities early

This layered approach means you can develop quickly (unit tests) while being confident your system works in production (integration + E2E tests).

## CI/CD Pipeline

Automated GitHub Actions workflow that ensures code quality and seamless deployments:

**Trigger Events:**
- **Pull Requests** to `main` → Run tests only
- **Push to `develop`** → Deploy to development environment
- **Push to `main`** → Deploy to production environment

**Pipeline Stages:**

1. **Test Stage** (runs on all triggers):
   - Install Python dependencies
   - Execute unit tests with pytest
   - Run security scans (Bandit + Safety)
   - Upload test reports as artifacts

2. **Deploy Development** (on `develop` branch):
   - Configure AWS credentials from GitHub Secrets
   - Build and deploy SAM application to dev environment
   - Run integration tests against deployed API
   - Validate deployment health

3. **Deploy Production** (on `main` branch):
   - Deploy SAM application to production environment
   - Update static website with production API endpoint
   - Deploy configured web client to S3

**Security Features:**
- AWS credentials stored as encrypted GitHub Secrets
- Automated vulnerability scanning on every commit
- Environment isolation (dev/prod)
- No secrets exposed in logs or code

### How the CI/CD Pipeline Works (Simple Explanation)

Think of CI/CD as a **smart assembly line** for software that automatically checks, tests, and deploys your code:

**What is CI/CD?**
- **CI (Continuous Integration)**: Automatically combines and tests code changes
- **CD (Continuous Deployment)**: Automatically releases tested code to users

**The Tools We Use:**

1. **GitHub Actions** - Like a robot assistant that watches your code
   - Runs automatically when you save changes to GitHub
   - Follows instructions written in `.github/workflows/ci-cd.yml`
   - Free for public repositories

2. **pytest** - Automated testing tool
   - Runs all your tests to make sure nothing is broken
   - Like having a QA team that never sleeps

3. **Bandit & Safety** - Security scanners
   - Bandit: Scans your code for security vulnerabilities
   - Safety: Checks if your dependencies have known security issues
   - Like having a security expert review every change

4. **AWS SAM** - Deployment tool
   - Automatically sets up all AWS services (Lambda, API Gateway, etc.)
   - Like having an infrastructure expert configure everything perfectly

**What Happens When You Make Changes:**

1. **You push code** to GitHub → GitHub Actions wakes up
2. **Tests run automatically** → Catches bugs before users see them
3. **Security scans** → Prevents vulnerable code from going live
4. **If everything passes** → Code automatically deploys to AWS
5. **If something fails** → Deployment stops, you get notified

**Why This Matters:**
- **No human errors** in deployment
- **Consistent quality** - every release is tested the same way
- **Fast feedback** - know within minutes if something is wrong
- **Professional standards** - same practices used by major tech companies

This automation means you can focus on building features while the pipeline ensures everything stays secure and working properly.

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

**Check if prerequisites are installed:**
```bash
# Check all prerequisites at once
echo "Checking prerequisites..."
echo "AWS CLI: $(aws --version 2>/dev/null || echo 'Not installed')"
echo "SAM CLI: $(sam --version 2>/dev/null || echo 'Not installed')"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not installed')"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "AWS Config: $(aws sts get-caller-identity 2>/dev/null && echo 'Configured' || echo 'Not configured')"
```

**Install missing prerequisites:**
```bash
# macOS (using Homebrew)
brew install awscli
brew install aws-sam-cli
brew install python@3.11
brew install node

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm curl unzip

# Install AWS CLI v2 (recommended)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Install SAM CLI
pip3 install aws-sam-cli

# Configure AWS (unless already configured)
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region (us-east-1), and output format (json)
```

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
