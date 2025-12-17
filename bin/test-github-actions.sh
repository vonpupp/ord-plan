#!/bin/bash

# Test GitHub Actions environment locally
set -e

echo "🐳 Building test Docker image..."
docker build -f Dockerfile -t ord-plan-test .

echo "🚀 Running test in Docker container..."
docker run --rm -v "$(pwd):/workspace" ord-plan-test

echo "✅ Test completed!"
