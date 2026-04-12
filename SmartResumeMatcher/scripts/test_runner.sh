#!/bin/bash

# Smart Resume Matcher - Test Runner
# This script runs the full test suite with coverage reporting.

# Ensure we are in the project root
cd "$(dirname "$0")/.."

echo "🚀 Starting Institutional Quality Assurance Suite..."
echo "-----------------------------------------------"

# Run pytest with coverage
PYTHONPATH=. python3 -m pytest --cov=backend --cov-report=term-missing tests/

echo "-----------------------------------------------"
echo "✅ Testing Complete!"
