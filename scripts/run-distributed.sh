#!/bin/bash

# YMS Dashboard Distributed JMeter Test Runner
# Script for running JMeter tests in distributed mode

set -e

# Configuration
MASTER_HOST="localhost"
SLAVE_HOSTS=""
SLAVE_PORT=1099
TEST_SCRIPT="./scripts/run-test.sh"
JMETER_HOME="${JMETER_HOME:-$(dirname $(dirname $(which jmeter)))}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

YMS Dashboard Distributed JMeter Test Runner

OPTIONS:
    -m, --master HOST           Master host (default: localhost)
    -s, --slaves HOSTS          Comma-separated list of slave hosts
    -p, --port PORT             RMI port for slaves (default: 1099)
    --start-slaves              Start JMeter server on slave machines
    --stop-slaves               Stop JMeter server on slave machines
    --check-slaves              Check status of slave machines
    --setup-slaves              Setup slaves with required files
    All other options are passed to run-test.sh

EXAMPLES:
    # Setup slave machines
    $0 --slaves slave1,slave2,slave3 --setup-slaves

    # Start slave servers
    $0 --slaves slave1,slave2,slave3 --start-slaves

    # Run distributed test
    $0 --slaves slave1,slave2,slave3 --base-url https://api.example.com --duration 3600

    # Check slave status
    $0 --slaves slave1,slave2,slave3 --check-slaves

    # Stop slave servers
    $0 --slaves slave1,slave2,slave3 --stop-slaves

EOF
}

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "OK")
            echo -e "${GREEN}[OK]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
    esac
}

# Function to validate prerequisites
validate_prerequisites() {
    if [ -z "$SLAVE_HOSTS" ]; then
        print_status "ERROR" "No slave hosts specified"
        usage
        exit 1
    fi
    
    if ! command -v jmeter &> /dev/null; then
        print_status "ERROR" "JMeter not found in PATH"
        exit 1
    fi
    
    # Check SSH access to slaves
    IFS=',' read -ra SLAVES <<< "$SLAVE_HOSTS"
    for slave in "${SLAVES[@]}"; do
        if [ "$slave" != "localhost" ] && [ "$slave" != "127.0.0.1" ]; then
            if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$slave" "echo 'SSH OK'" &>/dev/null; then
                print_status "WARNING" "Cannot SSH to $slave - please check SSH key authentication"
            fi
        fi
    done
}

# Function to setup slave machines
setup_slaves() {
    print_status "INFO" "Setting up slave machines..."
    
    # Create archive of required files
    local temp_dir=$(mktemp -d)
    local archive_name="jmeter-yms-test-files.tar.gz"
    
    print_status "INFO" "Creating archive of test files..."
    tar -czf "$temp_dir/$archive_name" \
        --exclude='results/*' \
        --exclude='reports/*' \
        --exclude='logs/*' \
        --exclude='*.jtl' \
        --exclude='*.log' \
        data/ scripts/payload-generators/ test-plans/ config/
    
    IFS=',' read -ra SLAVES <<< "$SLAVE_HOSTS"
    for slave in "${SLAVES[@]}"; do
        if [ "$slave" = "localhost" ] || [ "$slave" = "127.0.0.1" ]; then
            print_status "OK" "Skipping localhost setup"
            continue
        fi
        
        print_status "INFO" "Setting up $slave..."
        
        # Create test directory on slave
        ssh "$slave" "mkdir -p ~/jmeter-yms-test" || {
            print_status "ERROR" "Failed to create directory on $slave"
            continue
        }
        
        # Copy archive to slave
        scp "$temp_dir/$archive_name" "$slave:~/jmeter-yms-test/" || {
            print_status "ERROR" "Failed to copy files to $slave"
            continue
        }
        
        # Extract archive on slave
        ssh "$slave" "cd ~/jmeter-yms-test && tar -xzf $archive_name && rm $archive_name" || {
            print_status "ERROR" "Failed to extract files on $slave"
            continue
        }
        
        # Verify Python installation
        ssh "$slave" "python3 --version" &>/dev/null || {
            print_status "WARNING" "Python3 not found on $slave - payload generators may fail"
        }
        
        print_status "OK" "Setup completed for $slave"
    done
    
    rm -rf "$temp_dir"
}

# Function to start slave servers
start_slaves() {
    print_status "INFO" "Starting JMeter servers on slave machines..."
    
    IFS=',' read -ra SLAVES <<< "$SLAVE_HOSTS"
    for slave in "${SLAVES[@]}"; do
        print_status "INFO" "Starting server on $slave..."
        
        if [ "$slave" = "localhost" ] || [ "$slave" = "127.0.0.1" ]; then
            # Start local server
            nohup "$JMETER_HOME/bin/jmeter-server" \
                -Dserver.rmi.localport=$SLAVE_PORT \
                -Dserver_port=$SLAVE_PORT \
                -Djava.rmi.server.hostname=$MASTER_HOST \
                > "logs/jmeter-server-localhost.log" 2>&1 &
            
            local pid=$!
            sleep 2
            
            if kill -0 $pid 2>/dev/null; then
                print_status "OK" "Started local JMeter server (PID: $pid)"
                echo $pid > "logs/jmeter-server-localhost.pid"
            else
                print_status "ERROR" "Failed to start local JMeter server"
                cat "logs/jmeter-server-localhost.log"
            fi
        else
            # Start remote server via SSH
            ssh "$slave" "cd ~/jmeter-yms-test && nohup $JMETER_HOME/bin/jmeter-server \
                -Dserver.rmi.localport=$SLAVE_PORT \
                -Dserver_port=$SLAVE_PORT \
                -Djava.rmi.server.hostname=$slave \
                > jmeter-server.log 2>&1 & echo \$! > jmeter-server.pid" || {
                print_status "ERROR" "Failed to start server on $slave"
                continue
            }
            
            sleep 2
            
            # Verify server started
            if ssh "$slave" "kill -0 \$(cat ~/jmeter-yms-test/jmeter-server.pid) 2>/dev/null"; then
                print_status "OK" "Started JMeter server on $slave"
            else
                print_status "ERROR" "JMeter server failed to start on $slave"
                ssh "$slave" "tail -20 ~/jmeter-yms-test/jmeter-server.log"
            fi
        fi
    done
}

# Function to stop slave servers
stop_slaves() {
    print_status "INFO" "Stopping JMeter servers on slave machines..."
    
    IFS=',' read -ra SLAVES <<< "$SLAVE_HOSTS"
    for slave in "${SLAVES[@]}"; do
        print_status "INFO" "Stopping server on $slave..."
        
        if [ "$slave" = "localhost" ] || [ "$slave" = "127.0.0.1" ]; then
            # Stop local server
            if [ -f "logs/jmeter-server-localhost.pid" ]; then
                local pid=$(cat "logs/jmeter-server-localhost.pid")
                if kill $pid 2>/dev/null; then
                    print_status "OK" "Stopped local JMeter server (PID: $pid)"
                    rm -f "logs/jmeter-server-localhost.pid"
                else
                    print_status "WARNING" "Local JMeter server already stopped"
                fi
            else
                pkill -f "jmeter-server" || true
                print_status "OK" "Stopped all local JMeter servers"
            fi
        else
            # Stop remote server via SSH
            ssh "$slave" "if [ -f ~/jmeter-yms-test/jmeter-server.pid ]; then \
                kill \$(cat ~/jmeter-yms-test/jmeter-server.pid) 2>/dev/null && \
                rm -f ~/jmeter-yms-test/jmeter-server.pid && \
                echo 'Server stopped' || echo 'Server already stopped'; \
            else \
                pkill -f jmeter-server || echo 'No server running'; \
            fi" || print_status "WARNING" "Could not stop server on $slave"
        fi
    done
}

# Function to check slave status
check_slaves() {
    print_status "INFO" "Checking JMeter servers on slave machines..."
    echo ""
    printf "%-20s %-10s %-15s %-10s\n" "SLAVE HOST" "STATUS" "RMI PORT" "PID"
    printf "%-20s %-10s %-15s %-10s\n" "----------" "------" "--------" "---"
    
    IFS=',' read -ra SLAVES <<< "$SLAVE_HOSTS"
    for slave in "${SLAVES[@]}"; do
        local status="OFFLINE"
        local pid="-"
        
        # Check if port is open
        if timeout 2 bash -c "echo >/dev/tcp/$slave/$SLAVE_PORT" 2>/dev/null; then
            status="ONLINE"
            
            # Get PID
            if [ "$slave" = "localhost" ] || [ "$slave" = "127.0.0.1" ]; then
                if [ -f "logs/jmeter-server-localhost.pid" ]; then
                    pid=$(cat "logs/jmeter-server-localhost.pid")
                fi
            else
                pid=$(ssh "$slave" "cat ~/jmeter-yms-test/jmeter-server.pid 2>/dev/null" || echo "-")
            fi
        fi
        
        if [ "$status" = "ONLINE" ]; then
            printf "%-20s ${GREEN}%-10s${NC} %-15s %-10s\n" "$slave" "$status" "$SLAVE_PORT" "$pid"
        else
            printf "%-20s ${RED}%-10s${NC} %-15s %-10s\n" "$slave" "$status" "$SLAVE_PORT" "$pid"
        fi
    done
    echo ""
}

# Function to run distributed test
run_distributed_test() {
    print_status "INFO" "Preparing distributed test..."
    
    # Check that all slaves are online
    local all_online=true
    IFS=',' read -ra SLAVES <<< "$SLAVE_HOSTS"
    for slave in "${SLAVES[@]}"; do
        if ! timeout 2 bash -c "echo >/dev/tcp/$slave/$SLAVE_PORT" 2>/dev/null; then
            print_status "ERROR" "Slave $slave is not online"
            all_online=false
        fi
    done
    
    if [ "$all_online" = false ]; then
        print_status "ERROR" "Not all slaves are online. Run --check-slaves for details"
        exit 1
    fi
    
    print_status "INFO" "All slaves online. Starting distributed test..."
    
    # Create results directory
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local results_dir="results/distributed_${timestamp}"
    mkdir -p "$results_dir"
    
    # Build JMeter command
    local jmeter_cmd="jmeter -n"
    jmeter_cmd+=" -t test-plans/yms-dashboard-main.jmx"
    jmeter_cmd+=" -R $SLAVE_HOSTS"
    jmeter_cmd+=" -l $results_dir/results.jtl"
    jmeter_cmd+=" -j logs/jmeter_distributed_${timestamp}.log"
    jmeter_cmd+=" -e -o reports/distributed_${timestamp}"
    
    # Add all passed parameters
    for arg in "$@"; do
        if [[ $arg == -J* ]]; then
            jmeter_cmd+=" $arg"
        fi
    done
    
    # Add properties from command line
    jmeter_cmd+=" -Gbase.url=${BASE_URL:-http://localhost:5003}"
    jmeter_cmd+=" -Gtest.duration=${TEST_DURATION:-3600}"
    jmeter_cmd+=" -Grpm.multiplier=${RPM_MULTIPLIER:-1.0}"
    
    print_status "INFO" "Executing: $jmeter_cmd"
    
    # Run test
    if eval "$jmeter_cmd"; then
        print_status "OK" "Distributed test completed successfully"
        print_status "INFO" "Results: $results_dir/results.jtl"
        print_status "INFO" "Report: reports/distributed_${timestamp}/index.html"
    else
        print_status "ERROR" "Distributed test failed"
        exit 1
    fi
}

# Main execution
main() {
    local ACTION=""
    local TEST_ARGS=()
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--master)
                MASTER_HOST="$2"
                shift 2
                ;;
            -s|--slaves)
                SLAVE_HOSTS="$2"
                shift 2
                ;;
            -p|--port)
                SLAVE_PORT="$2"
                shift 2
                ;;
            --setup-slaves)
                ACTION="setup"
                shift
                ;;
            --start-slaves)
                ACTION="start"
                shift
                ;;
            --stop-slaves)
                ACTION="stop"
                shift
                ;;
            --check-slaves)
                ACTION="check"
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                # Collect other arguments for test execution
                TEST_ARGS+=("$1")
                shift
                ;;
        esac
    done
    
    # Validate prerequisites
    validate_prerequisites
    
    # Execute requested action
    case $ACTION in
        setup)
            setup_slaves
            ;;
        start)
            start_slaves
            ;;
        stop)
            stop_slaves
            ;;
        check)
            check_slaves
            ;;
        *)
            # Run distributed test
            if [ ${#TEST_ARGS[@]} -eq 0 ]; then
                print_status "ERROR" "No test arguments provided"
                usage
                exit 1
            fi
            
            # Parse test arguments
            BASE_URL="http://localhost:5003"
            TEST_DURATION="3600"
            RPM_MULTIPLIER="1.0"
            
            for ((i=0; i<${#TEST_ARGS[@]}; i++)); do
                case ${TEST_ARGS[i]} in
                    --base-url|-b)
                        BASE_URL="${TEST_ARGS[i+1]}"
                        ;;
                    --duration|-d)
                        TEST_DURATION="${TEST_ARGS[i+1]}"
                        ;;
                    --rpm-multiplier|-r)
                        RPM_MULTIPLIER="${TEST_ARGS[i+1]}"
                        ;;
                esac
            done
            
            run_distributed_test "${TEST_ARGS[@]}"
            ;;
    esac
}

# Execute main function
main "$@"