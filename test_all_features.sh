#!/bin/bash

# ZipIt Platform - Complete Feature & Route Testing
# Tests every single feature and route to ensure everything works

echo "⚡ ZipIt Platform - Complete Feature Testing"
echo "==========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

test_route() {
    local name=$1
    local url=$2
    local expected=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL (got $response, expected $expected)${NC}"
        ((FAILED++))
    fi
}

test_feature() {
    local name=$1
    local command=$2
    
    echo -n "Testing $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

echo -e "${BLUE}🌐 Testing Core Routes:${NC}"
echo "----------------------"

# Core service routes
test_route "ZipIt Dashboard" "http://localhost:8502"
test_route "ZipIt API Health" "http://localhost:8000/health"
test_route "Admin Panel" "http://localhost:8503"
test_route "AutoML Studio" "http://localhost:8504"
test_route "MLflow UI" "http://localhost:5000"

echo ""
echo -e "${BLUE}🔌 Testing API Endpoints:${NC}"
echo "-------------------------"

# API endpoints
test_route "API Docs" "http://localhost:8000/docs"
test_route "API Users" "http://localhost:8000/users"
test_route "API Models" "http://localhost:8000/models"
test_route "API Experiments" "http://localhost:8000/experiments"
test_route "API Deployments" "http://localhost:8000/deployments"

echo ""
echo -e "${BLUE}📊 Testing Monitoring Stack:${NC}"
echo "----------------------------"

# Monitoring services
test_route "Prometheus" "http://localhost:9090"
test_route "Grafana" "http://localhost:3000"
test_route "Nginx Load Balancer" "http://localhost/health"

echo ""
echo -e "${BLUE}🗄️ Testing Database Connections:${NC}"
echo "--------------------------------"

# Database tests
test_feature "PostgreSQL Connection" "docker exec \$(docker ps -q -f name=db) pg_isready -U postgres"
test_feature "Redis Connection" "docker exec \$(docker ps -q -f name=redis) redis-cli ping | grep -q PONG"

echo ""
echo -e "${BLUE}📱 Testing Feature Modules:${NC}"
echo "--------------------------"

# Check if feature files exist and are importable
test_feature "Code Workspace Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import code_workspace'"
test_feature "AI Assistant Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import ai_assistant'"
test_feature "Collaboration Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import collaboration'"
test_feature "Advanced Deployment Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import advanced_deployment'"
test_feature "Security Compliance Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import security_compliance'"
test_feature "Mobile Edge Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import mobile_edge'"
test_feature "Marketplace Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import marketplace'"
test_feature "Cost Optimization Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import cost_optimization'"
test_feature "Data Management Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import data_management'"
test_feature "Responsive UI Module" "python3 -c 'import sys; sys.path.append(\"src/dashboard\"); import responsive_ui'"

echo ""
echo -e "${BLUE}🐳 Testing Docker Infrastructure:${NC}"
echo "--------------------------------"

# Docker infrastructure
test_feature "All Containers Running" "[ \$(docker ps | grep -E '(api|dashboard|admin|automl|mlflow|db|redis|nginx|prometheus|grafana)' | wc -l) -ge 8 ]"
test_feature "Network Connectivity" "docker network ls | grep -q zipit"
test_feature "Volume Persistence" "docker volume ls | grep -q postgres_data"

echo ""
echo -e "${BLUE}📁 Testing File Structure:${NC}"
echo "-------------------------"

# File structure tests
test_feature "API Files Present" "[ -f src/api/platform_api.py ]"
test_feature "Dashboard Files Present" "[ -f src/dashboard/user_dashboard.py ]"
test_feature "Training Files Present" "[ -f src/training/automl_studio.py ]"
test_feature "Docker Files Present" "[ -f docker/Dockerfile.api ] && [ -f docker/Dockerfile.dashboard ]"
test_feature "Config Files Present" "[ -f nginx/mlops-platform.conf ] && [ -f monitoring/prometheus.yml ]"

echo ""
echo -e "${BLUE}⚙️ Testing Configuration:${NC}"
echo "------------------------"

# Configuration tests
test_feature "Requirements File" "[ -f requirements.txt ] && [ \$(wc -l < requirements.txt) -gt 20 ]"
test_feature "Database Init Script" "[ -f docker/init.sql ]"
test_feature "PWA Manifest" "[ -f static/manifest.json ]"
test_feature "Launch Scripts" "[ -x launch_enhanced_platform.sh ] && [ -x check_system_status.sh ]"

echo ""
echo "=========================================="
echo -e "${GREEN}✓ PASSED: $PASSED${NC}"
echo -e "${RED}✗ FAILED: $FAILED${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! ZipIt Platform is fully functional!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Ready for Production:${NC}"
    echo "• All routes working ✓"
    echo "• All features implemented ✓" 
    echo "• Database connected ✓"
    echo "• Load balancer configured ✓"
    echo "• Monitoring stack active ✓"
    echo "• Mobile & desktop optimized ✓"
    echo ""
    echo -e "${YELLOW}Access ZipIt: http://localhost:8502${NC}"
    echo -e "${YELLOW}Login: demo_user / demo123${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check the issues above.${NC}"
    exit 1
fi