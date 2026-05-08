#!/bin/bash

# ZipIt MLOps Platform - Quick Deploy Script
echo "🚀 ZipIt Platform Deployment"
echo "=============================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️ Don't run as root for security"
    exit 1
fi

# Install basic dependencies
echo "📦 Installing dependencies..."
pip install streamlit pandas numpy scikit-learn bcrypt sqlalchemy

# Create data directory
echo "📁 Creating directories..."
mkdir -p data logs static/images

# Initialize database
echo "🗄️ Setting up database..."
python -c "
from src.database.database import create_tables, init_admin_user
try:
    create_tables()
    init_admin_user()
    print('✅ Database initialized')
except Exception as e:
    print(f'⚠️ Database setup: {e}')
"

# Generate SSL certificates (self-signed for development)
echo "🔒 Generating SSL certificates..."
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/private.key -out ssl/certificate.crt -days 365 -nodes -subj "/C=IN/ST=State/L=City/O=ZipIt/CN=zipit.com" 2>/dev/null || echo "⚠️ SSL generation failed (optional)"

# Set permissions
echo "🔐 Setting permissions..."
chmod 600 ssl/private.key 2>/dev/null || true
chmod 644 ssl/certificate.crt 2>/dev/null || true

# Create startup script
echo "📝 Creating startup script..."
cat > start_zipit.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ZipIt Platform..."

# Start Streamlit app
echo "Starting dashboard on http://localhost:8501"
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# Wait for startup
sleep 3

echo "✅ ZipIt Platform is running!"
echo "📊 Dashboard: http://localhost:8501"
echo "💰 Admin Login: admin / zip@2604"
echo "💳 UPI Payment: 8660735943@ybl"
echo ""
echo "Press Ctrl+C to stop"

# Keep script running
wait
EOF

chmod +x start_zipit.sh

# Final status
echo ""
echo "✅ ZipIt Platform Deployed Successfully!"
echo "======================================"
echo "📊 Dashboard: http://localhost:8501"
echo "🔐 Admin: admin / zip@2604"
echo "💰 UPI: 8660735943@ybl"
echo ""
echo "🚀 Start Platform:"
echo "./start_zipit.sh"
echo ""
echo "💡 Quick Test:"
echo "python test_working.py"