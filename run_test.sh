#!/bin/bash

# Script to run JMeter test with different configurations

# Default values
THREADS=10
RAMPUP=1
DURATION=10
TEST_FILE="test_plan.jmx"
RESULTS_FILE="results_$(date +%Y%m%d_%H%M%S).jtl"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--threads)
      THREADS="$2"
      shift 2
      ;;
    -r|--rampup)
      RAMPUP="$2"
      shift 2
      ;;
    -d|--duration)
      DURATION="$2"
      shift 2
      ;;
    -f|--file)
      TEST_FILE="$2"
      shift 2
      ;;
    -o|--output)
      RESULTS_FILE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  -t, --threads    Number of threads (default: 30)"
      echo "  -r, --rampup     Ramp-up time in seconds (default: 60)"
      echo "  -d, --duration   Test duration in seconds (default: 300)"
      echo "  -f, --file       JMeter test file (default: test_plan.jmx)"
      echo "  -o, --output     Results file name (default: results_timestamp.jtl)"
      echo "  -h, --help       Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0 -t 50 -r 30 -d 600  # 50 threads, 30s ramp-up, 10 min duration"
      echo "  $0 -t 10 -d 60         # 10 threads, 60s ramp-up, 1 min duration"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use -h or --help for usage information"
      exit 1
      ;;
  esac
done

echo "Running JMeter test with:"
echo "  Threads: $THREADS"
echo "  Ramp-up: $RAMPUP seconds"
echo "  Duration: $DURATION seconds"
echo "  Test file: $TEST_FILE"
echo "  Results file: $RESULTS_FILE"
echo ""

# Run JMeter test
jmeter -n -t "$TEST_FILE" -l "$RESULTS_FILE" \
  -Jthreads=$THREADS \
  -Jrampup=$RAMPUP \
  -Jduration=$DURATION

# Check if test completed successfully
if [ $? -eq 0 ]; then
  echo ""
  echo "Test completed successfully!"
  echo "Results saved to: $RESULTS_FILE"
  
  # Generate summary report
  echo ""
  echo "Generating summary report..."
  jmeter -g "$RESULTS_FILE" -o "report_$(date +%Y%m%d_%H%M%S)"
else
  echo ""
  echo "Test failed! Check the logs for errors."
  exit 1
fi