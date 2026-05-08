#!/bin/bash

# ZipIt Platform - Feature Validation Script
# Validates new features before deployment

echo "⚡ ZipIt Feature Validation"
echo "=========================="

FEATURE_DIR="src/dashboard"
ERRORS=0

validate_feature() {
    local feature_file=$1
    local feature_name=$(basename "$feature_file" .py)
    
    echo -n "Validating $feature_name... "
    
    # Check Python syntax
    if ! python -m py_compile "$feature_file" 2>/dev/null; then
        echo "❌ Syntax Error"
        ((ERRORS++))
        return 1
    fi
    
    # Check imports
    if ! python -c "import sys; sys.path.append('$FEATURE_DIR'); import $feature_name" 2>/dev/null; then
        echo "❌ Import Error"
        ((ERRORS++))
        return 1
    fi
    
    # Check required functions
    if ! grep -q "def show_" "$feature_file"; then
        echo "❌ Missing show_ function"
        ((ERRORS++))
        return 1
    fi
    
    echo "✅ Valid"
    return 0
}

echo "🔍 Validating Feature Modules:"
echo "-----------------------------"

# Validate all feature files
for feature_file in "$FEATURE_DIR"/*.py; do
    if [[ -f "$feature_file" && $(basename "$feature_file") != "__init__.py" ]]; then
        validate_feature "$feature_file"
    fi
done

echo ""
echo "🧪 Running Integration Tests:"
echo "----------------------------"

# Test feature integration
python -c "
import sys
sys.path.append('$FEATURE_DIR')

features = [
    'ai_assistant', 'collaboration', 'advanced_deployment',
    'security_compliance', 'mobile_edge', 'marketplace',
    'cost_optimization', 'data_management', 'responsive_ui'
]

for feature in features:
    try:
        module = __import__(feature)
        print(f'✅ {feature} - OK')
    except Exception as e:
        print(f'❌ {feature} - {str(e)}')
        exit(1)
"

if [ $? -ne 0 ]; then
    ((ERRORS++))
fi

echo ""
echo "📊 Validation Summary:"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "✅ All features validated successfully!"
    echo "🚀 Ready for deployment"
    exit 0
else
    echo "❌ $ERRORS validation errors found"
    echo "🔧 Please fix issues before deployment"
    exit 1
fi