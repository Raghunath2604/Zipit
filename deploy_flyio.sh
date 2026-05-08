#!/bin/bash

echo "🚀 Deploying ZipIt MLOps Platform to Fly.io"
echo "==========================================="

# Install flyctl if not present
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing Fly.io CLI..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

echo "🔐 Login to Fly.io (opens browser)..."
flyctl auth login

echo "🚀 Launching ZipIt MLOps Platform..."
flyctl launch --no-deploy

echo "🌐 Setting custom domain (optional)..."
echo "Run: flyctl certs add zipit.com"

echo "🚀 Deploying application..."
flyctl deploy

echo ""
echo "✅ ZipIt MLOps Platform deployed!"
echo "🌐 Your platform is live at: https://zipit-mlops.fly.dev"
echo ""
echo "🎉 All features available:"
echo "- User authentication & API keys"
echo "- Model monitoring & drift detection"  
echo "- Real-time WebSocket monitoring"
echo "- AI assistant chat"
echo "- Code workspace IDE"
echo "- Custom domain: zipit.com (after DNS setup)"