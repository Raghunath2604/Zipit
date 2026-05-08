#!/bin/bash

# MLOps Platform Launcher with Enhanced UI/UX
# Complete platform with code workspace, data management, and seamless navigation

set -e

echo "🧠 Starting NeuralFlow - AI-Powered MLOps Platform..."
echo "===================================================="
echo "🌐 Future URL: https://neuralflow.com"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_status "Docker is running ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p data/datasets
    mkdir -p data/models
    mkdir -p workspace
    mkdir -p logs
    mkdir -p mlruns
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p nginx/ssl
    
    print_status "Directory structure created ✓"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed ✓"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Start individual services
start_services() {
    print_header "Starting MLOps Platform Services..."
    
    # Start API server
    print_status "Starting API Server (Port 8000)..."
    cd src/api && python -m uvicorn platform_api:app --host 0.0.0.0 --port 8000 --reload &
    API_PID=$!
    cd ../..
    
    # Start User Dashboard with enhanced features
    print_status "Starting User Dashboard with Code Workspace (Port 8502)..."
    cd src/dashboard && streamlit run user_dashboard.py --server.port 8502 --server.address 0.0.0.0 &
    USER_DASHBOARD_PID=$!
    cd ../..
    
    # Start Admin Panel
    print_status "Starting Admin Panel (Port 8503)..."
    cd src/dashboard && streamlit run executive_dashboard.py --server.port 8503 --server.address 0.0.0.0 &
    ADMIN_PID=$!
    cd ../..
    
    # Start AutoML Studio
    print_status "Starting AutoML Studio (Port 8504)..."
    cd src/training && streamlit run automl_studio.py --server.port 8504 --server.address 0.0.0.0 &
    AUTOML_PID=$!
    cd ../..
    
    # Start MLflow
    print_status "Starting MLflow Tracking Server (Port 5000)..."
    mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns &
    MLFLOW_PID=$!
    
    # Store PIDs for cleanup
    echo $API_PID > .api.pid
    echo $USER_DASHBOARD_PID > .user_dashboard.pid
    echo $ADMIN_PID > .admin.pid
    echo $AUTOML_PID > .automl.pid
    echo $MLFLOW_PID > .mlflow.pid
    
    print_status "All services started ✓"
}

# Health check function
health_check() {
    print_status "Performing health checks..."
    
    sleep 5  # Wait for services to start
    
    # Check API
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "API Server: ✓ Healthy"
    else
        print_warning "API Server: ⚠ Not responding"
    fi
    
    # Check User Dashboard
    if curl -s http://localhost:8502 > /dev/null; then
        print_status "User Dashboard: ✓ Healthy"
    else
        print_warning "User Dashboard: ⚠ Not responding"
    fi
    
    # Check Admin Panel
    if curl -s http://localhost:8503 > /dev/null; then
        print_status "Admin Panel: ✓ Healthy"
    else
        print_warning "Admin Panel: ⚠ Not responding"
    fi
    
    # Check AutoML Studio
    if curl -s http://localhost:8504 > /dev/null; then
        print_status "AutoML Studio: ✓ Healthy"
    else
        print_warning "AutoML Studio: ⚠ Not responding"
    fi
    
    # Check MLflow
    if curl -s http://localhost:5000 > /dev/null; then
        print_status "MLflow: ✓ Healthy"
    else
        print_warning "MLflow: ⚠ Not responding"
    fi
}

# Display service URLs
show_services() {
    print_header "🌐 NeuralFlow Platform Services"
    echo "=========================================="
    echo "🏠 NeuralFlow Dashboard:       http://localhost:8502"
    echo "   └── 🔧 AI Code Workspace:   Integrated smart IDE"
    echo "   └── 📊 Data Management:     Smart data pipeline"
    echo "   └── 🤖 AutoML Studio:       http://localhost:8504"
    echo ""
    echo "🔐 Admin Panel:               http://localhost:8503"
    echo "📈 MLflow UI:                 http://localhost:5000"
    echo "🔌 API Server:                http://localhost:8000"
    echo "📚 API Documentation:         http://localhost:8000/docs"
    echo ""
    echo "=========================================="
    echo "🎯 Quick Start Guide:"
    echo "1. Open NeuralFlow: http://localhost:8502"
    echo "2. Login with demo credentials:"
    echo "   Username: demo_user"
    echo "   Password: demo123"
    echo "3. Experience AI-powered MLOps"
    echo "4. Try mobile-responsive design"
    echo "5. Install as PWA on mobile"
    echo ""
    echo "📱 Mobile: Works on iOS/Android browsers"
    echo "💻 Desktop: Optimized for all screen sizes"
    echo ""
    print_status "NeuralFlow Platform is ready! 🧠"
}

# Cleanup function
cleanup() {
    print_status "Shutting down MLOps Platform..."
    
    # Kill processes if PID files exist
    for pid_file in .api.pid .user_dashboard.pid .admin.pid .automl.pid .mlflow.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                print_status "Stopped process $PID"
            fi
            rm -f "$pid_file"
        fi
    done
    
    print_status "Platform shutdown complete ✓"
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    print_header "🧠 NeuralFlow Platform Launcher"
    print_header "===================================="
    print_header "🌐 Professional MLOps Platform"
    print_header "🚀 Future: https://neuralflow.com"
    
    check_docker
    create_directories
    install_dependencies
    start_services
    health_check
    show_services
    
    print_status "Press Ctrl+C to stop all services"
    
    # Keep script running
    while true; do
        sleep 10
        # Optional: Add periodic health checks here
    done
}

# Handle command line arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        cleanup
        exit 0
        ;;
    "status")
        health_check
        ;;
    "docker")
        print_status "Starting with Docker Compose..."
        docker-compose up -d
        ;;
    *)
        echo "Usage: $0 {start|stop|status|docker}"
        echo "  start  - Start all services (default)"
        echo "  stop   - Stop all services"
        echo "  status - Check service health"
        echo "  docker - Start with Docker Compose"
        exit 1
        ;;
esac