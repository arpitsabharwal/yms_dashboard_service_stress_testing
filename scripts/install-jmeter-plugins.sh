#!/bin/bash

# Script to install JMeter Plugins Manager and required plugins

echo "JMeter Plugins Installation"
echo "==========================="

# Find JMeter installation
if command -v jmeter &> /dev/null; then
    JMETER_BIN=$(which jmeter)
    if [ -L "$JMETER_BIN" ]; then
        JMETER_BIN=$(readlink "$JMETER_BIN")
    fi
    JMETER_HOME=$(dirname $(dirname "$JMETER_BIN"))
else
    echo "Error: JMeter not found in PATH"
    exit 1
fi

echo "JMeter home: $JMETER_HOME"
PLUGINS_DIR="$JMETER_HOME/lib/ext"

# Check if plugins directory exists
if [ ! -d "$PLUGINS_DIR" ]; then
    echo "Error: Plugins directory not found: $PLUGINS_DIR"
    exit 1
fi

# Download Plugins Manager if not present
PLUGINS_MANAGER="$PLUGINS_DIR/jmeter-plugins-manager-1.9.jar"
if [ ! -f "$PLUGINS_MANAGER" ]; then
    echo "Downloading JMeter Plugins Manager..."
    DOWNLOAD_URL="https://jmeter-plugins.org/get/"
    
    # Download with curl or wget
    if command -v curl &> /dev/null; then
        curl -L -o "$PLUGINS_MANAGER" "$DOWNLOAD_URL"
    elif command -v wget &> /dev/null; then
        wget -O "$PLUGINS_MANAGER" "$DOWNLOAD_URL"
    else
        echo "Error: Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    if [ -f "$PLUGINS_MANAGER" ]; then
        echo "✓ Plugins Manager downloaded successfully"
    else
        echo "✗ Failed to download Plugins Manager"
        echo "Please download manually from: https://jmeter-plugins.org/install/Install/"
        exit 1
    fi
else
    echo "✓ Plugins Manager already installed"
fi

# Install Command Line Tool
echo ""
echo "Installing JMeter Plugins Command Line Tool..."
CMDRUNNER_URL="http://search.maven.org/remotecontent?filepath=kg/apc/cmdrunner/2.3/cmdrunner-2.3.jar"
CMDRUNNER_JAR="$JMETER_HOME/lib/cmdrunner-2.3.jar"

if [ ! -f "$CMDRUNNER_JAR" ]; then
    if command -v curl &> /dev/null; then
        curl -L -o "$CMDRUNNER_JAR" "$CMDRUNNER_URL"
    elif command -v wget &> /dev/null; then
        wget -O "$CMDRUNNER_JAR" "$CMDRUNNER_URL"
    fi
fi

# Generate PluginsManagerCMD script
if [ -f "$CMDRUNNER_JAR" ]; then
    cd "$JMETER_HOME/lib"
    java -cp "$CMDRUNNER_JAR" kg.apc.cmd.UniversalRunner --tool org.jmeterplugins.repository.PluginManagerCMD --generate-cmd-line-tool
    cd - > /dev/null
    echo "✓ Command line tool installed"
fi

# Install required plugins
echo ""
echo "Installing required plugins..."

REQUIRED_PLUGINS=(
    "jpgc-casutg"     # Ultimate Thread Group
    "jpgc-graphs-basic"
    "jpgc-graphs-additional"
    "jpgc-perfmon"
)

if [ -f "$JMETER_HOME/lib/PluginsManagerCMD.sh" ]; then
    for plugin in "${REQUIRED_PLUGINS[@]}"; do
        echo "Installing $plugin..."
        "$JMETER_HOME/lib/PluginsManagerCMD.sh" install "$plugin"
    done
else
    echo "Warning: Could not install plugins automatically"
    echo "Please install manually using JMeter GUI:"
    echo "1. Open JMeter"
    echo "2. Go to Options > Plugins Manager"
    echo "3. Install: jpgc-casutg (Ultimate Thread Group)"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Note: If you want to use the advanced test plan with Ultimate Thread Groups,"
echo "update the TEST_PLAN variable in run-test.sh to use yms-dashboard-main.jmx"
echo "instead of yms-dashboard-main-simple.jmx"