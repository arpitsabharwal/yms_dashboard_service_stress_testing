#!/bin/bash

# Simple script to check JMeter installation on macOS

echo "Checking JMeter installation..."
echo "================================"

# Check if JMeter is installed
if command -v jmeter &> /dev/null; then
    echo "✓ JMeter found at: $(which jmeter)"
    
    # Get version info
    echo ""
    echo "JMeter version info:"
    jmeter --version 2>&1 | head -20
    
    # Extract just the version number
    VERSION=$(jmeter --version 2>&1 | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+" | head -1)
    echo ""
    echo "Detected version: $VERSION"
    
    # Check Java
    echo ""
    echo "Java version:"
    java -version 2>&1 | head -3
    
    # Check JMeter home
    JMETER_BIN=$(which jmeter)
    if [ -L "$JMETER_BIN" ]; then
        JMETER_BIN=$(readlink "$JMETER_BIN")
    fi
    JMETER_HOME=$(dirname $(dirname "$JMETER_BIN"))
    echo ""
    echo "JMeter home: $JMETER_HOME"
    
    # Check for plugins directory
    if [ -d "$JMETER_HOME/lib/ext" ]; then
        echo "✓ Plugins directory exists: $JMETER_HOME/lib/ext"
        echo ""
        echo "Installed plugins:"
        ls -la "$JMETER_HOME/lib/ext"/*.jar 2>/dev/null | tail -5
    fi
    
else
    echo "✗ JMeter not found in PATH"
    echo ""
    echo "To install JMeter on macOS:"
    echo "1. Using Homebrew: brew install jmeter"
    echo "2. Manual download from: https://jmeter.apache.org/download_jmeter.cgi"
fi

echo ""
echo "================================"