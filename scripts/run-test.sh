#!/bin/bash

# YMS Dashboard JMeter Test Runner
# Main script to execute load tests with various configurations

set -e

# Default values
BASE_URL="http://localhost:5003"
TEST_DURATION=3600
RPM_MULTIPLIER=1.0
TEST_PLAN="test-plans/yms-dashboard-main.jmx"
REPORT_NAME="yms-test-$(date +%Y%m%d_%H%M%S)"
TENANTS=""
TEST_PROFILE=""
DRY_RUN=false
GUI_MODE=false
DISTRIBUTED=false
EXCLUDED_APIS=""

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

YMS Dashboard JMeter Test Runner

OPTIONS:
    -b, --base-url URL          Base URL for the API (default: $BASE_URL)
    -d, --duration SECONDS      Test duration in seconds (default: $TEST_DURATION)
    -r, --rpm-multiplier FLOAT  RPM multiplier (default: $RPM_MULTIPLIER)
    -t, --tenants TENANT_LIST   Comma-separated list of tenant IDs to test
    -p, --profile PROFILE       Test profile to use (smoke-test|load-test|stress-test)
    -n, --report-name NAME      Report name (default: auto-generated)
    -e, --exclude-apis APIS     Comma-separated list of APIs to exclude
    --test-plan FILE            JMeter test plan file to use
    --dry-run                   Validate configuration without running tests
    --gui                       Run JMeter in GUI mode
    --distributed               Run in distributed mode
    -h, --help                  Display this help message

EXAMPLES:
    # Run a basic load test
    $0 --base-url https://api.example.com --duration 3600

    # Run smoke test for specific tenants
    $0 --profile smoke-test --tenants TENANT_A,TENANT_B

    # Run stress test with increased load
    $0 --profile stress-test --rpm-multiplier 1.5

    # Exclude specific APIs from test
    $0 --exclude-apis "yard-availability,trailer-overview"

    # Dry run to validate configuration
    $0 --dry-run --tenants TENANT_A

EOF
}

# Function to parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--base-url)
                BASE_URL="$2"
                shift 2
                ;;
            -d|--duration)
                TEST_DURATION="$2"
                shift 2
                ;;
            -r|--rpm-multiplier)
                RPM_MULTIPLIER="$2"
                shift 2
                ;;
            -t|--tenants)
                TENANTS="$2"
                shift 2
                ;;
            -p|--profile)
                TEST_PROFILE="$2"
                shift 2
                ;;
            -n|--report-name)
                REPORT_NAME="$2"
                shift 2
                ;;
            -e|--exclude-apis)
                EXCLUDED_APIS="$2"
                shift 2
                ;;
            --test-plan)
                TEST_PLAN="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --gui)
                GUI_MODE=true
                shift
                ;;
            --distributed)
                DISTRIBUTED=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
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
    print_status "INFO" "Validating prerequisites..."
    
    # Check if JMeter is available
    if ! command -v jmeter &> /dev/null; then
        print_status "ERROR" "JMeter not found in PATH"
        exit 1
    fi
    
    # Check if test plan exists
    if [ ! -f "$TEST_PLAN" ]; then
        print_status "ERROR" "Test plan not found: $TEST_PLAN"
        exit 1
    fi
    
    # Check data files
    local required_files=("data/tenants.csv" "data/facilities.csv" "data/carriers.csv")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_status "ERROR" "Required data file not found: $file"
            exit 1
        fi
    done
    
    print_status "OK" "Prerequisites validated"
}

# Function to load test profile
load_test_profile() {
    if [ -n "$TEST_PROFILE" ]; then
        local profile_file="config/test-profiles/${TEST_PROFILE}.properties"
        
        if [ -f "$profile_file" ]; then
            print_status "INFO" "Loading test profile: $TEST_PROFILE"
            
            # Source the profile file and override variables
            while IFS='=' read -r key value; do
                # Skip comments and empty lines
                [[ $key =~ ^#.*$ ]] && continue
                [[ -z $key ]] && continue
                
                # Remove any surrounding whitespace
                key=$(echo "$key" | xargs)
                value=$(echo "$value" | xargs)
                
                case $key in
                    "test.duration")
                        TEST_DURATION=$value
                        ;;
                    "rpm.multiplier")
                        RPM_MULTIPLIER=$value
                        ;;
                esac
            done < "$profile_file"
            
            print_status "OK" "Test profile loaded"
        else
            print_status "ERROR" "Test profile not found: $profile_file"
            exit 1
        fi
    fi
}

# Function to validate tenant configuration
validate_tenant_config() {
    if [ -n "$TENANTS" ]; then
        print_status "INFO" "Validating tenant configuration..."
        
        IFS=',' read -ra TENANT_ARRAY <<< "$TENANTS"
        for tenant in "${TENANT_ARRAY[@]}"; do
            if ! grep -q "^$tenant," data/tenants.csv; then
                print_status "ERROR" "Tenant not found in configuration: $tenant"
                exit 1
            fi
        done
        
        print_status "OK" "Tenant configuration validated"
    fi
}

# Function to create results directory
create_results_dir() {
    local results_dir="results/$REPORT_NAME"
    local reports_dir="reports/$REPORT_NAME"
    
    mkdir -p "$results_dir"
    mkdir -p "$reports_dir"
    mkdir -p "logs"
    
    print_status "OK" "Created results directory: $results_dir"
    print_status "OK" "Created reports directory: $reports_dir"
}

# Function to build JMeter command
build_jmeter_command() {
    local cmd="jmeter"
    
    # Add non-GUI flag unless GUI mode is requested
    if [ "$GUI_MODE" = false ]; then
        cmd+=" -n"
    fi
    
    # Add test plan
    cmd+=" -t $TEST_PLAN"
    
    # Add log file
    cmd+=" -j logs/jmeter_${REPORT_NAME}.log"
    
    # Add results file
    cmd+=" -l results/${REPORT_NAME}/results.jtl"
    
    # Add HTML report generation
    if [ "$GUI_MODE" = false ]; then
        cmd+=" -e -o reports/${REPORT_NAME}"
    fi
    
    # Add properties
    cmd+=" -Jbase.url=$BASE_URL"
    cmd+=" -Jtest.duration=$TEST_DURATION"
    cmd+=" -Jrpm.multiplier=$RPM_MULTIPLIER"
    
    # Add tenant filter if specified
    if [ -n "$TENANTS" ]; then
        cmd+=" -Jtenants.filter=$TENANTS"
    fi
    
    # Add excluded APIs if specified
    if [ -n "$EXCLUDED_APIS" ]; then
        cmd+=" -Jexcluded.apis=$EXCLUDED_APIS"
    fi
    
    # Add user properties file
    if [ -f "config/user.properties" ]; then
        cmd+=" -q config/user.properties"
    fi
    
    # Add JMeter properties file
    if [ -f "config/jmeter.properties" ]; then
        cmd+=" -p config/jmeter.properties"
    fi
    
    echo "$cmd"
}

# Function to display test configuration
display_test_config() {
    echo ""
    echo "================================================"
    echo "YMS Dashboard Load Test Configuration"
    echo "================================================"
    echo "Base URL:        $BASE_URL"
    echo "Duration:        $TEST_DURATION seconds"
    echo "RPM Multiplier:  $RPM_MULTIPLIER"
    echo "Test Plan:       $TEST_PLAN"
    echo "Report Name:     $REPORT_NAME"
    
    if [ -n "$TENANTS" ]; then
        echo "Tenants:         $TENANTS"
    else
        echo "Tenants:         ALL"
    fi
    
    if [ -n "$TEST_PROFILE" ]; then
        echo "Test Profile:    $TEST_PROFILE"
    fi
    
    if [ -n "$EXCLUDED_APIS" ]; then
        echo "Excluded APIs:   $EXCLUDED_APIS"
    fi
    
    if [ "$DISTRIBUTED" = true ]; then
        echo "Mode:            Distributed"
    elif [ "$GUI_MODE" = true ]; then
        echo "Mode:            GUI"
    else
        echo "Mode:            Non-GUI"
    fi
    
    echo "================================================"
    echo ""
}

# Function to run the test
run_test() {
    if [ "$DRY_RUN" = true ]; then
        print_status "INFO" "DRY RUN - Test would execute with the following command:"
        echo "$(build_jmeter_command)"
        return 0
    fi
    
    print_status "INFO" "Starting load test..."
    
    # Create results directories
    create_results_dir
    
    # Build and execute JMeter command
    local jmeter_cmd=$(build_jmeter_command)
    
    print_status "INFO" "Executing: $jmeter_cmd"
    echo ""
    
    # Run JMeter
    if eval "$jmeter_cmd"; then
        print_status "OK" "Test completed successfully"
        
        if [ "$GUI_MODE" = false ]; then
            print_status "INFO" "Results saved to: results/${REPORT_NAME}/results.jtl"
            print_status "INFO" "HTML report available at: reports/${REPORT_NAME}/index.html"
        fi
    else
        print_status "ERROR" "Test execution failed"
        exit 1
    fi
}

# Function to generate summary report
generate_summary() {
    if [ "$GUI_MODE" = false ] && [ "$DRY_RUN" = false ]; then
        local results_file="results/${REPORT_NAME}/results.jtl"
        
        if [ -f "$results_file" ]; then
            print_status "INFO" "Generating summary report..."
            
            # Create summary file
            local summary_file="reports/${REPORT_NAME}/summary.txt"
            
            {
                echo "YMS Dashboard Load Test Summary"
                echo "==============================="
                echo "Test Name: $REPORT_NAME"
                echo "Start Time: $(head -n 2 "$results_file" | tail -n 1 | cut -d',' -f1)"
                echo "Base URL: $BASE_URL"
                echo "Duration: $TEST_DURATION seconds"
                echo "RPM Multiplier: $RPM_MULTIPLIER"
                echo ""
                echo "Results Summary:"
                echo "---------------"
                
                # Calculate basic statistics using awk
                awk -F',' '
                    NR>1 {
                        total++
                        sum+=$2
                        if ($4=="true") success++
                        if ($2>max || NR==2) max=$2
                        if ($2<min || NR==2) min=$2
                    }
                    END {
                        print "Total Samples: " total
                        print "Success Rate: " (success/total*100) "%"
                        print "Average Response Time: " (sum/total) " ms"
                        print "Min Response Time: " min " ms"
                        print "Max Response Time: " max " ms"
                    }
                ' "$results_file"
                
            } > "$summary_file"
            
            print_status "OK" "Summary report saved to: $summary_file"
            
            # Display summary
            echo ""
            cat "$summary_file"
        fi
    fi
}

# Main execution
main() {
    # Parse command line arguments
    parse_args "$@"
    
    # Display header
    echo "================================================"
    echo "YMS Dashboard JMeter Test Runner"
    echo "================================================"
    
    # Validate prerequisites
    validate_prerequisites
    
    # Load test profile if specified
    load_test_profile
    
    # Validate tenant configuration
    validate_tenant_config
    
    # Display test configuration
    display_test_config
    
    # Ask for confirmation unless in dry-run mode
    if [ "$DRY_RUN" = false ] && [ "$GUI_MODE" = false ]; then
        read -p "Do you want to proceed with the test? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "INFO" "Test cancelled by user"
            exit 0
        fi
    fi
    
    # Run the test
    run_test
    
    # Generate summary report
    generate_summary
    
    echo ""
    echo "================================================"
    echo "Test execution completed!"
    echo "================================================"
}

# Execute main function
main "$@" 