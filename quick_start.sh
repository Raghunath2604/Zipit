#!/bin/bash

# MLOps Monitoring Platform - Quick Start Script
# Sets up and runs the open-source MLOps monitoring platform

echo "🚀 MLOps Monitoring Platform - Quick Start"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "Please check your internet connection and try again."
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create static directory for assets
mkdir -p static/images
echo "📁 Created static directories"

# Start the platform
echo ""
echo "🚀 Starting MLOps Monitoring Platform..."
echo "📊 Dashboard will be available at: http://localhost:8000"
echo "🏠 Home page will be available at: http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the platform
python3 mlops_platform.py