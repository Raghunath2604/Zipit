#!/bin/bash

# Complete MLOps Platform Launcher
# Starts all services with proper configuration

set -e

echo "🚀 Complete MLOps Platform Launcher"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required"
        exit 1
    fi
    
    # Docker (optional)
    if command -v docker &> /dev/null; then
        print_status "Docker found - containerized deployment available"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not found - using local deployment"
        DOCKER_AVAILABLE=false
    fi
    
    # MLflow
    if ! python3 -c "import mlflow" 2>/dev/null; then
        print_info "Installing MLflow..."
        pip install mlflow
    fi
    
    print_status "Dependencies checked"
}

# Install requirements
install_requirements() {
    print_info "Installing Python requirements..."
    pip install -r requirements.txt
    print_status "Requirements installed"
}

# Initialize MLflow
setup_mlflow() {
    print_info "Setting up MLflow..."
    
    if [ ! -d "mlruns" ]; then
        mkdir -p mlruns
    fi
    
    export MLFLOW_TRACKING_URI="file:./mlruns"
    print_status "MLflow configured"
}

# Initialize DVC
setup_dvc() {
    print_info "Setting up DVC..."
    
    if command -v dvc &> /dev/null; then
        if [ ! -d ".dvc" ]; then
            dvc init --no-scm
            print_status "DVC initialized"
        else
            print_status "DVC already initialized"
        fi
    else
        print_warning "DVC not installed - data versioning disabled"
    fi
}

# Start services
start_services() {
    print_info "Starting MLOps Platform services..."
    
    # Create logs directory
    mkdir -p logs
    
    # Start FastAPI backend
    print_info "Starting API server (port 8000)..."
    cd src/api && python platform_api.py > ../../logs/api.log 2>&1 &
    API_PID=$!
    cd ../..
    
    sleep 3
    
    # Start User Dashboard
    print_info "Starting User Dashboard (port 8502)..."
    cd src/dashboard && streamlit run user_dashboard.py --server.port 8502 --server.address 0.0.0.0 > ../../logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    cd ../..
    
    sleep 3
    
    # Start Admin Panel
    print_info "Starting Admin Panel (port 8503)..."
    cd src/dashboard && streamlit run admin_panel.py --server.port 8503 --server.address 0.0.0.0 > ../../logs/admin.log 2>&1 &
    ADMIN_PID=$!
    cd ../..
    
    sleep 3
    
    # Start AutoML Studio
    print_info "Starting AutoML Studio (port 8504)..."
    cd src/training && streamlit run automl_studio.py --server.port 8504 --server.address 0.0.0.0 > ../../logs/automl.log 2>&1 &
    AUTOML_PID=$!
    cd ../..
    
    sleep 3
    
    # Start MLflow UI
    print_info "Starting MLflow UI (port 5000)..."
    mlflow ui --backend-store-uri file:./mlruns --host 0.0.0.0 --port 5000 > logs/mlflow.log 2>&1 &
    MLFLOW_PID=$!
    
    sleep 3
    
    # Save PIDs
    echo $API_PID > logs/api.pid
    echo $DASHBOARD_PID > logs/dashboard.pid
    echo $ADMIN_PID > logs/admin.pid
    echo $AUTOML_PID > logs/automl.pid
    echo $MLFLOW_PID > logs/mlflow.pid
    
    print_status "All services started successfully!"
}

# Display service URLs
show_services() {
    echo ""
    echo "🌐 MLOps Platform Services"
    echo "=========================="
    echo ""
    echo "📊 User Dashboard:     http://localhost:8502"
    echo "🔧 Admin Panel:        http://localhost:8503"
    echo "🤖 AutoML Studio:      http://localhost:8504"
    echo "🔬 MLflow UI:          http://localhost:5000"
    echo "📡 API Documentation:  http://localhost:8000/docs"
    echo ""
    echo "🎯 Quick Start:"
    echo "1. Visit User Dashboard to register"
    echo "2. Use AutoML Studio to train models"
    echo "3. Monitor with real-time dashboards"
    echo "4. Track experiments with MLflow"
    echo ""
}

# Stop services
stop_services() {
    print_info "Stopping MLOps Platform services..."
    
    if [ -f logs/api.pid ]; then
        kill $(cat logs/api.pid) 2>/dev/null || true
        rm logs/api.pid
    fi
    
    if [ -f logs/dashboard.pid ]; then
        kill $(cat logs/dashboard.pid) 2>/dev/null || true
        rm logs/dashboard.pid
    fi
    
    if [ -f logs/admin.pid ]; then
        kill $(cat logs/admin.pid) 2>/dev/null || true
        rm logs/admin.pid
    fi
    
    if [ -f logs/automl.pid ]; then
        kill $(cat logs/automl.pid) 2>/dev/null || true
        rm logs/automl.pid
    fi
    
    if [ -f logs/mlflow.pid ]; then
        kill $(cat logs/mlflow.pid) 2>/dev/null || true
        rm logs/mlflow.pid
    fi
    
    print_status "All services stopped"
}

# Docker deployment
deploy_docker() {
    print_info "Deploying with Docker Compose..."
    
    if [ ! -f docker-compose.yml ]; then
        print_error "docker-compose.yml not found"
        exit 1
    fi
    
    docker-compose up -d
    print_status "Docker deployment started"
    
    echo ""
    echo "🐳 Docker Services"
    echo "=================="
    echo "Access via: http://localhost"
    echo ""
}

# Health check
health_check() {
    print_info "Performing health check..."
    
    # Check API
    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_status "API server healthy"
    else
        print_error "API server not responding"
    fi
    
    # Check Dashboard
    if curl -s http://localhost:8502 > /dev/null; then
        print_status "Dashboard healthy"
    else
        print_error "Dashboard not responding"
    fi
    
    # Check MLflow
    if curl -s http://localhost:5000 > /dev/null; then
        print_status "MLflow UI healthy"
    else
        print_error "MLflow UI not responding"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) 🚀 Start All Services (Local)"
    echo "2) 🐳 Deploy with Docker"
    echo "3) 🔍 Health Check"
    echo "4) 🛑 Stop All Services"
    echo "5) 📊 Show Service Status"
    echo "6) 🧹 Clean Up"
    echo "7) ❌ Exit"
    echo ""
}

# Service status
show_status() {
    echo ""
    echo "📊 Service Status"
    echo "================"
    
    services=("api:8000" "dashboard:8502" "admin:8503" "automl:8504" "mlflow:5000")
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s http://localhost:$port > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name (port $port) - Running${NC}"
        else
            echo -e "${RED}❌ $name (port $port) - Not running${NC}"
        fi
    done
    echo ""
}

# Cleanup
cleanup() {
    print_info "Cleaning up..."
    
    stop_services
    
    # Clean logs
    if [ -d logs ]; then
        rm -rf logs/*
    fi
    
    # Clean temporary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete
    
    print_status "Cleanup completed"
}

# Trap for cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    check_dependencies
    
    while true; do
        show_menu
        read -p "Enter your choice [1-7]: " choice
        
        case $choice in
            1)
                install_requirements
                setup_mlflow
                setup_dvc
                start_services
                show_services
                ;;
            2)
                if [ "$DOCKER_AVAILABLE" = true ]; then
                    deploy_docker
                else
                    print_error "Docker not available"
                fi
                ;;
            3)
                health_check
                ;;
            4)
                stop_services
                ;;
            5)
                show_status
                ;;
            6)
                cleanup
                ;;
            7)
                print_info "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-7."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main