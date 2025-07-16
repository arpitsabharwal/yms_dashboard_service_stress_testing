#!/usr/bin/env python3

import sys
import json
import csv
from datetime import datetime
from pathlib import Path

def analyze_results(results_dir):
    """Analyze all test results and generate comparison report"""
    
    results_path = Path(results_dir)
    summary_files = list(results_path.glob("summary/*.json"))
    
    if not summary_files:
        print("No summary files found")
        return
    
    # Load all summaries
    summaries = []
    for file in summary_files:
        with open(file, 'r') as f:
            summaries.append(json.load(f))
    
    # Sort by date
    summaries.sort(key=lambda x: x['test_date'])
    
    # Generate comparison report
    print("\n=== YMS Dashboard Stress Test Analysis ===\n")
    print(f"Total tests analyzed: {len(summaries)}")
    print(f"Date range: {summaries[0]['test_date']} to {summaries[-1]['test_date']}\n")
    
    # Tenant summary
    tenants = {}
    for summary in summaries:
        tenant = summary['tenant']
        if tenant not in tenants:
            tenants[tenant] = {
                'tests': 0,
                'total_requests': 0,
                'total_errors': 0,
                'avg_error_rate': []
            }
        
        tenants[tenant]['tests'] += 1
        tenants[tenant]['total_requests'] += summary['total_requests']
        tenants[tenant]['total_errors'] += summary['failed_requests']
        tenants[tenant]['avg_error_rate'].append(summary['error_rate'])
    
    print("=== Tenant Summary ===")
    for tenant, stats in tenants.items():
        avg_error = sum(stats['avg_error_rate']) / len(stats['avg_error_rate'])
        print(f"\n{tenant}:")
        print(f"  Tests run: {stats['tests']}")
        print(f"  Total requests: {stats['total_requests']:,}")
        print(f"  Total errors: {stats['total_errors']:,}")
        print(f"  Average error rate: {avg_error:.2f}%")
    
    # Endpoint performance trends
    print("\n=== Endpoint Performance Trends ===")
    endpoint_stats = {}
    
    for summary in summaries:
        for endpoint, stats in summary['endpoints'].items():
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'p95_times': [],
                    'error_rates': []
                }
            endpoint_stats[endpoint]['p95_times'].append(stats['p95_rt'])
            endpoint_stats[endpoint]['error_rates'].append(stats['error_rate'])
    
    for endpoint, stats in endpoint_stats.items():
        avg_p95 = sum(stats['p95_times']) / len(stats['p95_times'])
        avg_error = sum(stats['error_rates']) / len(stats['error_rates'])
        print(f"\n{endpoint}:")
        print(f"  Average P95 response time: {avg_p95:.0f}ms")
        print(f"  Average error rate: {avg_error:.2f}%")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze-results.py <results_directory>")
        sys.exit(1)
    
    analyze_results(sys.argv[1])
