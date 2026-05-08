#!/bin/bash

# MLOps Platform - Production Deployment Script
# Supports Railway, Render, Vercel, and Docker deployments

echo "🚀 MLOps Platform - Production Deployment"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - MLOps Platform"
fi

echo "🌐 Choose deployment platform:"
echo "1. Railway (Recommended - Free tier available)"
echo "2. Render (Free tier available)"
echo "3. Vercel (Serverless)"
echo "4. Docker (Self-hosted)"
echo "5. Heroku"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🚂 Deploying to Railway..."
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Deploy: railway up"
        echo ""
        echo "📋 Railway deployment commands:"
        echo "railway login"
        echo "railway up"
        echo ""
        echo "🌍 Your app will be available at: https://your-app.railway.app"
        ;;
    2)
        echo "🎨 Deploying to Render..."
        echo "1. Push code to GitHub"
        echo "2. Connect GitHub repo to Render"
        echo "3. Use render.yaml configuration"
        echo ""
        echo "📋 GitHub setup:"
        echo "git remote add origin https://github.com/yourusername/mlops-platform"
        echo "git push -u origin main"
        echo ""
        echo "🌍 Then connect at: https://render.com"
        ;;
    3)
        echo "⚡ Deploying to Vercel..."
        echo "1. Install Vercel CLI: npm install -g vercel"
        echo "2. Login: vercel login"
        echo "3. Deploy: vercel --prod"
        echo ""
        echo "📋 Vercel deployment commands:"
        echo "vercel login"
        echo "vercel --prod"
        echo ""
        echo "🌍 Your app will be available at: https://your-app.vercel.app"
        ;;
    4)
        echo "🐳 Building Docker container..."
        docker build -t mlops-platform .
        echo "🚀 Starting with Docker Compose..."
        docker-compose -f docker-compose.prod.yml up -d
        echo ""
        echo "🌍 Your app is running at: http://localhost"
        echo "📊 Dashboard: http://localhost/dashboard"
        echo "📚 API Docs: http://localhost/docs"
        ;;
    5)
        echo "🟣 Deploying to Heroku..."
        echo "1. Install Heroku CLI"
        echo "2. Login: heroku login"
        echo "3. Create app: heroku create your-mlops-platform"
        echo "4. Deploy: git push heroku main"
        echo ""
        echo "📋 Heroku deployment commands:"
        echo "heroku login"
        echo "heroku create your-mlops-platform"
        echo "git push heroku main"
        echo ""
        echo "🌍 Your app will be available at: https://your-mlops-platform.herokuapp.com"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment configuration ready!"
echo ""
echo "🎯 Features available in production:"
echo "   ✅ User Registration & Authentication"
echo "   ✅ Model Upload & Deployment"
echo "   ✅ Real-time Predictions"
echo "   ✅ Drift Detection"
echo "   ✅ Performance Metrics"
echo "   ✅ Interactive Visualizations"
echo "   ✅ Professional Dashboard"
echo ""
echo "🔗 Important URLs:"
echo "   🏠 Home: https://your-domain.com"
echo "   🔐 Login: https://your-domain.com/login"
echo "   📊 Dashboard: https://your-domain.com/dashboard"
echo "   📚 API Docs: https://your-domain.com/docs"
echo ""
echo "🔧 Next Steps:"
echo "1. Follow the platform-specific instructions above"
echo "2. Update domain URLs in your templates if needed"
echo "3. Configure environment variables for production"
echo "4. Set up SSL certificates for HTTPS"
echo ""
echo "🎉 Your MLOps Platform is ready for production!"