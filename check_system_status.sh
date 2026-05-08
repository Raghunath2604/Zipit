#!/bin/bash

# ZipIt Platform System Status Checker
# Verifies all components are working properly

echo "⚡ ZipIt Platform - System Status Check"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    local service_name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}✓ Online${NC}"
        return 0
    else
        echo -e "${RED}✗ Offline${NC}"
        return 1
    fi
}

check_database() {
    echo -n "Checking PostgreSQL... "
    if docker exec -it $(docker ps -q -f name=db) pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected${NC}"
        return 0
    else
        echo -e "${RED}✗ Connection Failed${NC}"
        return 1
    fi
}

check_redis() {
    echo -n "Checking Redis... "
    if docker exec -it $(docker ps -q -f name=redis) redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected${NC}"
        return 0
    else
        echo -e "${RED}✗ Connection Failed${NC}"
        return 1
    fi
}

# Main status checks
echo "🔍 Service Health Checks:"
echo "------------------------"

# Core services
check_service "ZipIt Dashboard" "http://localhost:8502"
check_service "ZipIt API" "http://localhost:8000/health"
check_service "Admin Panel" "http://localhost:8503"
check_service "AutoML Studio" "http://localhost:8504"
check_service "MLflow UI" "http://localhost:5000"

echo ""
echo "🗄️ Database & Cache:"
echo "-------------------"

# Database and cache
check_database
check_redis

echo ""
echo "📊 Monitoring & Load Balancer:"
echo "-----------------------------"

# Monitoring
check_service "Prometheus" "http://localhost:9090"
check_service "Grafana" "http://localhost:3000"
check_service "Nginx Load Balancer" "http://localhost/health"

echo ""
echo "📈 System Metrics:"
echo "-----------------"

# Docker stats
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(api|dashboard|admin|automl|mlflow|db|redis|nginx|prometheus|grafana)"

echo ""
echo "💾 Storage Usage:"
docker system df

echo ""
echo "🌐 Network Status:"
docker network ls | grep zipit

echo ""
echo "⚡ ZipIt Platform Status: Complete!"
echo "=================================="
echo "🌐 Access: http://localhost:8502"
echo "👤 Login: demo_user / demo123"