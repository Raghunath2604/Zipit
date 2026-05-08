#!/bin/bash

# MLOps Platform - Complete Deployment Script
# Launches platform with visualization and deployment features

echo "🚀 MLOps Platform - Complete Deployment"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "📋 Python version: $python_version"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p templates

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q fastapi uvicorn sqlalchemy pydantic python-multipart
pip install -q scikit-learn numpy scipy pandas
pip install -q python-jose[cryptography] passlib[bcrypt]
pip install -q jinja2 aiofiles

# Create minimal static files if they don't exist
if [ ! -f "static/css/style.css" ]; then
    echo "🎨 Creating basic CSS..."
    cat > static/css/style.css << 'EOF'
body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
.container { max-width: 1200px; margin: 0 auto; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }
.card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1rem; }
EOF
fi

# Check if main platform file exists
if [ ! -f "mlops_platform.py" ]; then
    echo "❌ mlops_platform.py not found!"
    exit 1
fi

# Start the platform
echo "🌟 Starting MLOps Platform..."
echo "📍 Platform will be available at: http://localhost:8002"
echo "📊 Dashboard: http://localhost:8002/dashboard"
echo "🔧 API Documentation: http://localhost:8002/docs"
echo ""
echo "🎯 Features Available:"
echo "   ✅ User Registration & Authentication"
echo "   ✅ Model Upload & Deployment"
echo "   ✅ Real-time Predictions"
echo "   ✅ Drift Detection"
echo "   ✅ Performance Metrics"
echo "   ✅ Interactive Visualizations"
echo "   ✅ Dashboard Monitoring"
echo ""
echo "Press Ctrl+C to stop the platform"
echo "======================================"

# Launch platform
python3 mlops_platform.py