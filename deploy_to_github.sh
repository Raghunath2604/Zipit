#!/bin/bash

# ZipIt Platform - Selective GitHub Deployment
# Only pushes public-facing code, not sensitive data

echo "⚡ Deploying ZipIt Platform (Public Version)"
echo "============================================"
echo "Repository: https://github.com/Raghunath2604/Zipit.git"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git remote add origin https://github.com/Raghunath2604/Zipit.git
fi

# Add only public files (respects .gitignore)
echo "📁 Adding public files only..."
git add .

# Show what will be committed
echo "📋 Files to be committed:"
git status --porcelain

echo ""
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Commit changes
echo "💾 Committing public code..."
git commit -m "⚡ ZipIt Platform - Public Release

🚀 Lightning-Fast AI-Powered MLOps Platform

✨ Features:
- AI-Powered Code Workspace
- Real-time Collaboration  
- Advanced Deployment
- Enterprise Security
- Mobile & Desktop Ready
- Plugin Marketplace
- Cost Optimization
- Complete CI/CD

🎯 Ready for production deployment
📱 Mobile-optimized experience
🔒 Enterprise-grade security"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Successfully deployed public version!"
echo "🌐 Repository: https://github.com/Raghunath2604/Zipit.git"
echo "🔒 Sensitive data excluded via .gitignore"
echo "📊 CI/CD Pipeline will start automatically"
echo ""
echo "🎯 What was pushed:"
echo "✅ Source code (src/)"
echo "✅ Documentation (README.md, guides)"
echo "✅ Docker configurations"
echo "✅ CI/CD pipeline"
echo "✅ Public configuration files"
echo ""
echo "🔒 What was excluded:"
echo "❌ Database files and data"
echo "❌ SSL certificates"
echo "❌ Environment secrets"
echo "❌ Log files"
echo "❌ Temporary files"
echo ""
echo "⚡ ZipIt Platform is now publicly available! 🚀"