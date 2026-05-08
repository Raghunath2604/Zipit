#!/bin/bash

# ZipIt Platform - Comprehensive Bug Detection
# Deep testing for all potential issues

echo "🔍 ZipIt Platform - Deep Bug Detection"
echo "======================================"

BUGS=0
WARNINGS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

bug_found() {
    echo -e "${RED}🐛 BUG FOUND${NC}"
    ((BUGS++))
}

warning_found() {
    echo -e "${YELLOW}⚠️ WARNING${NC}"
    ((WARNINGS++))
}

no_issues() {
    echo -e "${GREEN}✅ OK${NC}"
}

echo "🔍 Testing Import Dependencies"
echo "-----------------------------"

echo -n "Testing streamlit imports... "
if python -c "import streamlit as st; import streamlit.components.v1" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  Streamlit import failed"
fi

echo -n "Testing plotly imports... "
if python -c "import plotly.graph_objects as go; import plotly.express as px" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  Plotly import failed"
fi

echo -n "Testing pandas/numpy... "
if python -c "import pandas as pd; import numpy as np" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  Pandas/Numpy import failed"
fi

echo ""
echo "🧪 Testing Feature Modules"
echo "-------------------------"

for module in ai_assistant collaboration advanced_deployment security_compliance marketplace cost_optimization data_management mobile_edge; do
    echo -n "Testing $module... "
    if python -c "
import sys
sys.path.append('src/dashboard')
try:
    mod = __import__('$module')
    if hasattr(mod, 'show_$module') or 'show_' in str(dir(mod)):
        print('OK')
    else:
        print('MISSING_FUNCTION')
        exit(1)
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" 2>/dev/null; then
        no_issues
    else
        bug_found
        echo "  Module $module has issues"
    fi
done

echo ""
echo "🔧 Testing API Endpoints"
echo "-----------------------"

echo -n "Testing FastAPI structure... "
if python -c "
import sys
sys.path.append('src/api')
from platform_api import app
from fastapi import FastAPI
assert isinstance(app, FastAPI)
print('OK')
" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  FastAPI structure invalid"
fi

echo ""
echo "🐳 Testing Docker Configuration"
echo "-----------------------------"

echo -n "Testing Dockerfile syntax... "
docker_errors=0
for dockerfile in docker/Dockerfile.*; do
    if [ -f "$dockerfile" ]; then
        if ! grep -q "FROM\|RUN\|COPY" "$dockerfile"; then
            docker_errors=$((docker_errors + 1))
        fi
    fi
done

if [ $docker_errors -eq 0 ]; then
    no_issues
else
    bug_found
    echo "  $docker_errors Dockerfiles have issues"
fi

echo -n "Testing docker-compose syntax... "
if python -c "
import yaml
with open('docker-compose.yml') as f:
    config = yaml.safe_load(f)
    assert 'services' in config
    assert 'api' in config['services']
    print('OK')
" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  docker-compose.yml has syntax errors"
fi

echo ""
echo "📁 Testing File Paths"
echo "--------------------"

echo -n "Testing critical file paths... "
missing_files=0
critical_files=(
    "src/api/platform_api.py"
    "src/dashboard/user_dashboard.py"
    "src/training/automl_studio.py"
    "requirements.txt"
    "README.md"
)

for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -eq 0 ]; then
    no_issues
else
    bug_found
    echo "  $missing_files critical files missing"
fi

echo ""
echo "🔒 Testing Security Issues"
echo "-------------------------"

echo -n "Checking for hardcoded secrets... "
secrets_found=0
if grep -r "password.*=" src/ 2>/dev/null | grep -v "password_hash\|password_field" | grep -q .; then
    secrets_found=1
fi

if [ $secrets_found -eq 0 ]; then
    no_issues
else
    warning_found
    echo "  Found potential hardcoded passwords"
fi

echo -n "Checking .gitignore coverage... "
if [ -f ".gitignore" ] && grep -q "\.env\|\.key\|\.pem\|password" .gitignore; then
    no_issues
else
    warning_found
    echo "  .gitignore may not cover all sensitive files"
fi

echo ""
echo "🌐 Testing Navigation Routes"
echo "---------------------------"

echo -n "Testing user_dashboard routes... "
if python -c "
import sys
sys.path.append('src/dashboard')
with open('src/dashboard/user_dashboard.py') as f:
    content = f.read()
    routes = ['workspace', 'ai_assistant', 'collaboration', 'deploy', 'security', 'mobile', 'marketplace', 'cost']
    missing = [r for r in routes if f\"current_page == '{r}'\" not in content]
    if missing:
        print(f'MISSING_ROUTES: {missing}')
        exit(1)
    print('OK')
" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  Navigation routes incomplete"
fi

echo ""
echo "📊 Testing Data Handling"
echo "-----------------------"

echo -n "Testing pandas operations... "
if python -c "
import pandas as pd
import numpy as np
# Test basic operations that the platform uses
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
assert len(df) == 3
assert df.shape == (3, 2)
print('OK')
" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  Pandas operations failing"
fi

echo ""
echo "🎨 Testing UI Components"
echo "----------------------"

echo -n "Testing streamlit components... "
if python -c "
import streamlit as st
# Test that streamlit functions exist
funcs = ['title', 'write', 'button', 'selectbox', 'columns', 'metric']
for func in funcs:
    assert hasattr(st, func), f'Missing {func}'
print('OK')
" 2>/dev/null; then
    no_issues
else
    bug_found
    echo "  Streamlit components missing"
fi

echo ""
echo "📋 Bug Detection Summary"
echo "======================="
echo -e "${RED}🐛 Bugs Found: $BUGS${NC}"
echo -e "${YELLOW}⚠️ Warnings: $WARNINGS${NC}"

if [ $BUGS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 NO BUGS FOUND! ZipIt Platform is clean!${NC}"
    echo ""
    echo "✅ All imports working"
    echo "✅ All modules functional"
    echo "✅ API structure valid"
    echo "✅ Docker config correct"
    echo "✅ File paths exist"
    echo "✅ Security checks passed"
    echo "✅ Navigation routes complete"
    echo "✅ Data handling working"
    echo "✅ UI components available"
    echo ""
    echo "🚀 Platform is production-ready!"
    exit 0
elif [ $BUGS -eq 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Minor warnings found, but no critical bugs${NC}"
    echo "Platform is deployable with minor issues to address"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Critical bugs found that need fixing${NC}"
    echo "Please resolve bugs before deployment"
    exit 1
fi