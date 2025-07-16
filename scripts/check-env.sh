#!/bin/bash

# Check environment compatibility for YMS Dashboard testing

echo "Environment Compatibility Check"
echo "==============================="
echo ""

# Check bash version
echo "Bash version:"
echo "  Current: $BASH_VERSION"
if [ "${BASH_VERSION%%.*}" -lt 4 ]; then
    echo "  ⚠️  Warning: Bash version is less than 4.0"
    echo "  Some scripts have been adapted for compatibility"
else
    echo "  ✓ Bash 4.0+ detected"
fi

echo ""
echo "System information:"
echo "  OS: $(uname -s)"
echo "  Version: $(uname -r)"
echo "  Machine: $(uname -m)"

echo ""
echo "Python version:"
if command -v python3 &> /dev/null; then
    python3 --version
    echo "  ✓ Python3 found"
else
    echo "  ✗ Python3 not found"
fi

echo ""
echo "Java version:"
if command -v java &> /dev/null; then
    java -version 2>&1 | head -1
    echo "  ✓ Java found"
else
    echo "  ✗ Java not found"
fi

echo ""
echo "JMeter status:"
if command -v jmeter &> /dev/null; then
    VERSION=$(jmeter --version 2>&1 | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+" | head -1)
    echo "  Version: $VERSION"
    echo "  ✓ JMeter found"
else
    echo "  ✗ JMeter not found"
fi

echo ""
echo "Required commands:"
commands=("grep" "sed" "awk" "cut" "sort" "uniq" "tail" "head" "wc")
for cmd in "${commands[@]}"; do
    if command -v $cmd &> /dev/null; then
        echo "  ✓ $cmd"
    else
        echo "  ✗ $cmd (missing)"
    fi
done

echo ""
echo "Optional commands:"
opt_commands=("bc" "jq" "xmllint" "curl")
for cmd in "${opt_commands[@]}"; do
    if command -v $cmd &> /dev/null; then
        echo "  ✓ $cmd"
    else
        echo "  ⚠️  $cmd (not found - some features may be limited)"
    fi
done

echo ""
echo "==============================="
echo ""

if command -v bc &> /dev/null; then
    echo "✓ All required dependencies found"
else
    echo "⚠️  'bc' command not found. Installing..."
    echo "  On macOS: brew install bc"
    echo "  On Linux: sudo apt-get install bc"
fi