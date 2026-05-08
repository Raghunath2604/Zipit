#!/bin/bash

echo "🚂 Deploying MLOps Platform to Railway"
echo "====================================="
echo ""
echo "🎯 Why Railway is BEST for this project:"
echo "   ✅ FREE tier with generous limits"
echo "   ✅ Persistent file system (model uploads work)"
echo "   ✅ SQLite database persists"
echo "   ✅ No timeout limits"
echo "   ✅ Background processes supported"
echo "   ✅ Automatic HTTPS"
echo "   ✅ Custom domains"
echo "   ✅ Zero configuration needed"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "🔐 Login to Railway..."
railway login

echo "🚀 Deploying platform..."
railway up

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 Your MLOps Platform is now LIVE at:"
echo "   https://your-app.railway.app"
echo ""
echo "📊 Available URLs:"
echo "   🏠 Home: https://your-app.railway.app/"
echo "   🔐 Login: https://your-app.railway.app/login"
echo "   📊 Dashboard: https://your-app.railway.app/dashboard"
echo "   📚 API Docs: https://your-app.railway.app/docs"
echo ""
echo "🧪 Test your deployment:"
echo "   curl https://your-app.railway.app/"
echo ""
echo "🎉 Your MLOps Platform is LIVE and ready for users!"