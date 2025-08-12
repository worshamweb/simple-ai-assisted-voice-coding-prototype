#!/bin/bash

# Test runner script for Voice AI Coding Prototype

set -e

echo "🧪 Running Voice AI Coding Prototype Tests"

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r tests/requirements.txt

# Run unit tests
echo "🔬 Running unit tests..."
pytest tests/unit/ -v --tb=short

# Run integration tests (if API_ENDPOINT is set)
if [ ! -z "$API_ENDPOINT" ]; then
    echo "🔗 Running integration tests..."
    pytest tests/integration/ -v --tb=short
else
    echo "⚠️  Skipping integration tests (API_ENDPOINT not set)"
fi

# Run E2E tests (if WEBSITE_URL is set and chromedriver available)
if [ ! -z "$WEBSITE_URL" ] && command -v chromedriver &> /dev/null; then
    echo "🌐 Running E2E tests..."
    pytest tests/e2e/ -v --tb=short -m "not slow"
else
    echo "⚠️  Skipping E2E tests (WEBSITE_URL not set or chromedriver not available)"
fi

echo "✅ All available tests completed!"
echo ""
echo "💡 To run specific test types:"
echo "   Unit only:        pytest tests/unit/"
echo "   Integration only: API_ENDPOINT=<url> pytest tests/integration/"
echo "   E2E only:         WEBSITE_URL=<url> pytest tests/e2e/"