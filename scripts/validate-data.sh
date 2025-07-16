#!/bin/bash

# YMS Dashboard Test Data Validation Script
# Validates CSV data files and configuration

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
ERRORS=0
WARNINGS=0

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "OK")
            echo -e "${GREEN}[✓]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[✗]${NC} $message"
            ERRORS=$((ERRORS + 1))
            ;;
        "WARNING")
            echo -e "${YELLOW}[⚠]${NC} $message"
            WARNINGS=$((WARNINGS + 1))
            ;;
    esac
}

# Function to check file exists
check_file_exists() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        print_status "OK" "$description exists: $file"
        return 0
    else
        print_status "ERROR" "$description missing: $file"
        return 1
    fi
}

# Function to validate CSV headers
validate_csv_headers() {
    local file=$1
    local expected_headers=$2
    local description=$3
    
    if [ ! -f "$file" ]; then
        return 1
    fi
    
    local actual_headers=$(head -n 1 "$file")
    
    if [ "$actual_headers" = "$expected_headers" ]; then
        print_status "OK" "$description headers valid"
        return 0
    else
        print_status "ERROR" "$description headers invalid"
        echo "  Expected: $expected_headers"
        echo "  Actual:   $actual_headers"
        return 1
    fi
}

# Function to validate tenant configuration
validate_tenants() {
    echo ""
    echo "Validating Tenant Configuration..."
    echo "=================================="
    
    local tenant_file="data/tenants.csv"
    local expected_headers="tenant_id,tenant_name,target_rpm,auth_token,ramp_up_seconds"
    
    if ! check_file_exists "$tenant_file" "Tenant configuration"; then
        return
    fi
    
    validate_csv_headers "$tenant_file" "$expected_headers" "Tenant CSV"
    
    # Check for actual tenant data
    local tenant_count=$(tail -n +2 "$tenant_file" | grep -v "^$" | wc -l | tr -d ' ')
    if [ "$tenant_count" -eq 0 ]; then
        print_status "ERROR" "No tenant data found in $tenant_file"
    else
        print_status "OK" "Found $tenant_count tenant(s)"
        
        # Validate each tenant
        local line_num=1
        while IFS=',' read -r tenant_id tenant_name target_rpm auth_token ramp_up_seconds; do
            line_num=$((line_num + 1))
            
            # Skip header
            if [ $line_num -eq 2 ] && [ "$tenant_id" = "tenant_id" ]; then
                continue
            fi
            
            # Validate tenant_id format
            if ! echo "$tenant_id" | grep -qE '^TENANT_[A-Z]$'; then
                print_status "WARNING" "Line $line_num: Invalid tenant_id format: $tenant_id (expected TENANT_X)"
            fi
            
            # Validate target_rpm is numeric
            if ! echo "$target_rpm" | grep -qE '^[0-9]+$'; then
                print_status "ERROR" "Line $line_num: Invalid target_rpm: $target_rpm (must be numeric)"
            fi
            
            # Check for missing auth token
            if [ "$auth_token" = "Bearer token_here" ] || [ -z "$auth_token" ]; then
                print_status "WARNING" "Line $line_num: Auth token not configured for $tenant_id"
            fi
            
            # Validate ramp_up_seconds
            if ! echo "$ramp_up_seconds" | grep -qE '^[0-9]+$'; then
                print_status "ERROR" "Line $line_num: Invalid ramp_up_seconds: $ramp_up_seconds"
            fi
            
        done < "$tenant_file"
    fi
}

# Function to validate facilities
validate_facilities() {
    echo ""
    echo "Validating Facility Configuration..."
    echo "===================================="
    
    local facility_file="data/facilities.csv"
    local expected_headers="tenant_id,facility_id,facility_name,load_weight,carrier_ids"
    
    if ! check_file_exists "$facility_file" "Facility configuration"; then
        return
    fi
    
    validate_csv_headers "$facility_file" "$expected_headers" "Facility CSV"
    
    # Get unique tenants from facilities
    local facility_tenants=$(tail -n +2 "$facility_file" | cut -d',' -f1 | sort -u)
    
    # Track load weights per tenant using a temp file
    local temp_weights="/tmp/tenant_weights_$$"
    > "$temp_weights"
    
    local line_num=1
    while IFS=',' read -r tenant_id facility_id facility_name load_weight carrier_ids; do
        line_num=$((line_num + 1))
        
        # Skip header
        if [ $line_num -eq 2 ] && [ "$tenant_id" = "tenant_id" ]; then
            continue
        fi
        
        # Validate facility_id is numeric
        if ! echo "$facility_id" | grep -qE '^[0-9]+$'; then
            print_status "ERROR" "Line $line_num: Invalid facility_id: $facility_id"
        fi
        
        # Validate load_weight
        if ! echo "$load_weight" | grep -qE '^0?\.[0-9]+$' && ! echo "$load_weight" | grep -qE '^1\.0$'; then
            print_status "ERROR" "Line $line_num: Invalid load_weight: $load_weight (must be 0.0-1.0)"
        else
            # Store weight for tenant
            echo "${tenant_id}:${load_weight}" >> "$temp_weights"
        fi
        
        # Validate carrier_ids format
        if ! echo "$carrier_ids" | grep -qE '^"[0-9,]+"$' && ! echo "$carrier_ids" | grep -qE '^[0-9,]+$'; then
            print_status "WARNING" "Line $line_num: Invalid carrier_ids format: $carrier_ids"
        fi
        
    done < "$facility_file"
    
    # Validate total weights per tenant equal 1.0
    echo ""
    echo "Checking facility load weight totals..."
    
    # Get unique tenants from weights file
    local unique_tenants=$(cut -d: -f1 "$temp_weights" | sort -u)
    
    for tenant in $unique_tenants; do
        # Sum weights for this tenant
        local total_weight=$(grep "^${tenant}:" "$temp_weights" | cut -d: -f2 | awk '{sum+=$1} END {printf "%.2f", sum}')
        
        # Check if total equals 1.0 (with some tolerance)
        if [ "$total_weight" = "1.00" ] || [ "$total_weight" = "1.0" ]; then
            print_status "OK" "Tenant $tenant: Total load weight = $total_weight ✓"
        else
            print_status "ERROR" "Tenant $tenant: Total load weight = $total_weight (must equal 1.0)"
        fi
    done
    
    # Clean up temp file
    rm -f "$temp_weights"
    
    # Check if all tenants from tenants.csv have facilities
    if [ -f "data/tenants.csv" ]; then
        while IFS=',' read -r tenant_id _; do
            if [ "$tenant_id" != "tenant_id" ] && [ -n "$tenant_id" ]; then
                if ! echo "$facility_tenants" | grep -q "^$tenant_id$"; then
                    print_status "WARNING" "Tenant $tenant_id has no facilities defined"
                fi
            fi
        done < "data/tenants.csv"
    fi
}

# Function to validate carriers
validate_carriers() {
    echo ""
    echo "Validating Carrier Configuration..."
    echo "==================================="
    
    local carrier_file="data/carriers.csv"
    local expected_headers="carrier_id,carrier_name,carrier_code"
    
    if ! check_file_exists "$carrier_file" "Carrier configuration"; then
        return
    fi
    
    validate_csv_headers "$carrier_file" "$expected_headers" "Carrier CSV"
    
    # Get all carrier IDs
    local valid_carrier_ids=$(tail -n +2 "$carrier_file" | cut -d',' -f1 | sort -u)
    
    # Check carrier references in facilities
    if [ -f "data/facilities.csv" ]; then
        echo ""
        echo "Validating carrier references in facilities..."
        
        while IFS=',' read -r _ _ _ _ carrier_ids; do
            # Skip header
            if [ "$carrier_ids" = "carrier_ids" ]; then
                continue
            fi
            
            # Remove quotes and split carrier IDs
            carrier_ids=$(echo "$carrier_ids" | tr -d '"' | tr ',' ' ')
            
            for carrier_id in $carrier_ids; do
                if ! echo "$valid_carrier_ids" | grep -q "^$carrier_id$"; then
                    print_status "WARNING" "Carrier ID $carrier_id referenced in facilities but not defined in carriers.csv"
                fi
            done
        done < "data/facilities.csv"
    fi
}

# Function to validate test data files
validate_test_data() {
    echo ""
    echo "Validating Test Data Files..."
    echo "============================="
    
    # Check trailer states
    local trailer_states_file="data/test-data/trailer-states.csv"
    if check_file_exists "$trailer_states_file" "Trailer states data"; then
        validate_csv_headers "$trailer_states_file" "state_value,state_name,description" "Trailer states CSV"
    fi
    
    # Check shipment directions
    local directions_file="data/test-data/shipment-directions.csv"
    if check_file_exists "$directions_file" "Shipment directions data"; then
        validate_csv_headers "$directions_file" "direction_value,direction_name" "Shipment directions CSV"
    fi
}

# Function to validate Python payload generators
validate_python_generators() {
    echo ""
    echo "Validating Python Payload Generators..."
    echo "======================================="
    
    local generators_dir="scripts/payload-generators"
    
    if [ ! -d "$generators_dir" ]; then
        print_status "ERROR" "Payload generators directory not found: $generators_dir"
        return
    fi
    
    # Check Python availability
    if ! command -v python3 &> /dev/null; then
        print_status "ERROR" "Python3 not found in PATH - payload generators will fail"
        return
    else
        local python_version=$(python3 --version 2>&1)
        print_status "OK" "Python available: $python_version"
    fi
    
    # List of required generators
    local required_generators="base_payload_generator.py
facility_request_generator.py
trailer_overview_generator.py
trailer_exceptions_generator.py
task_workload_generator.py
task_attention_generator.py
site_occupancy_generator.py
shipment_forecast_generator.py
dwell_time_generator.py
door_breakdown_generator.py
detention_summary_generator.py"
    
    echo "$required_generators" | while read generator; do
        if [ -f "$generators_dir/$generator" ]; then
            print_status "OK" "Found: $generator"
            
            # Check if it's executable
            if [ -x "$generators_dir/$generator" ]; then
                print_status "OK" "  - Executable"
            else
                print_status "WARNING" "  - Not executable (chmod +x recommended)"
            fi
            
            # Test Python syntax
            if python3 -m py_compile "$generators_dir/$generator" 2>/dev/null; then
                print_status "OK" "  - Valid Python syntax"
            else
                print_status "ERROR" "  - Python syntax error in $generator"
            fi
        else
            print_status "ERROR" "Missing generator: $generator"
        fi
    done
}

# Function to validate JMX files
validate_jmx_files() {
    echo ""
    echo "Validating JMeter Test Plans..."
    echo "==============================="
    
    # Check main test plan
    local main_plan="test-plans/yms-dashboard-main.jmx"
    if check_file_exists "$main_plan" "Main test plan"; then
        # Basic XML validation
        if command -v xmllint &> /dev/null && xmllint --noout "$main_plan" 2>/dev/null; then
            print_status "OK" "Main test plan XML is valid"
        else
            print_status "WARNING" "Cannot validate XML (xmllint not available)"
        fi
    fi
    
    # Check API fragments
    local fragments_dir="test-plans/api-fragments"
    local required_fragments="yard-availability.jmx
trailer-overview.jmx
trailer-exceptions.jmx
task-workload.jmx
task-attention.jmx
site-occupancy.jmx
shipment-forecast.jmx
dwell-time.jmx
door-breakdown.jmx
detention-summary.jmx"
    
    echo ""
    echo "Checking API fragment files..."
    echo "$required_fragments" | while read fragment; do
        if [ -f "$fragments_dir/$fragment" ]; then
            print_status "OK" "Found: $fragment"
        else
            print_status "ERROR" "Missing fragment: $fragment"
        fi
    done
}

# Function to validate configuration files
validate_config_files() {
    echo ""
    echo "Validating Configuration Files..."
    echo "================================="
    
    # Check test profiles
    local profiles="smoke-test load-test stress-test"
    for profile in $profiles; do
        local profile_file="config/test-profiles/${profile}.properties"
        if check_file_exists "$profile_file" "$profile profile"; then
            # Check if file is not empty
            if [ -s "$profile_file" ]; then
                print_status "OK" "  - Has content"
            else
                print_status "ERROR" "  - File is empty"
            fi
        fi
    done
    
    # Check JMeter properties
    if check_file_exists "config/jmeter.properties" "JMeter properties"; then
        print_status "OK" "JMeter properties file exists"
    fi
    
    if check_file_exists "config/user.properties" "User properties"; then
        print_status "OK" "User properties file exists"
    fi
}

# Function to test Python generator execution
test_generator_execution() {
    echo ""
    echo "Testing Python Generator Execution..."
    echo "===================================="
    
    local test_facility_id="101"
    local test_carrier_ids="201,202,203"
    
    # Test facility request generator
    echo ""
    echo "Testing facility_request_generator.py..."
    if python3 scripts/payload-generators/facility_request_generator.py "$test_facility_id" 2>/dev/null | python3 -m json.tool >/dev/null 2>&1; then
        print_status "OK" "facility_request_generator produces valid JSON"
    else
        print_status "ERROR" "facility_request_generator failed or produced invalid JSON"
    fi
    
    # Test trailer overview generator
    echo "Testing trailer_overview_generator.py..."
    if python3 scripts/payload-generators/trailer_overview_generator.py "$test_facility_id" "$test_carrier_ids" 2>/dev/null | python3 -m json.tool >/dev/null 2>&1; then
        print_status "OK" "trailer_overview_generator produces valid JSON"
    else
        print_status "ERROR" "trailer_overview_generator failed or produced invalid JSON"
    fi
}

# Function to generate summary
generate_summary() {
    echo ""
    echo "====================================="
    echo "Validation Summary"
    echo "====================================="
    echo -e "Total Errors:   ${RED}$ERRORS${NC}"
    echo -e "Total Warnings: ${YELLOW}$WARNINGS${NC}"
    
    if [ $ERRORS -eq 0 ]; then
        echo -e "\n${GREEN}✓ All critical validations passed!${NC}"
        return 0
    else
        echo -e "\n${RED}✗ Critical errors found. Please fix before running tests.${NC}"
        return 1
    fi
}

# Main validation flow
main() {
    echo "====================================="
    echo "YMS Dashboard Test Data Validator"
    echo "====================================="
    echo "Date: $(date)"
    echo "Working Directory: $(pwd)"
    echo ""
    
    # Run all validations
    validate_tenants
    validate_facilities
    validate_carriers
    validate_test_data
    validate_python_generators
    validate_jmx_files
    validate_config_files
    
    # Test generator execution
    test_generator_execution
    
    # Generate summary
    generate_summary
}

# Execute main function
main