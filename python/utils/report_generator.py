import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import statistics
from collections import defaultdict

class ReportGenerator:
    """Generate HTML and CSV reports from test results"""
    
    def __init__(self, results_dir: str = "reports"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        os.makedirs(os.path.join(results_dir, "html"), exist_ok=True)
        os.makedirs(os.path.join(results_dir, "csv"), exist_ok=True)
        os.makedirs(os.path.join(results_dir, "summary"), exist_ok=True)
    
    def generate_summary_report(self, jtl_file: str, tenant: str) -> Dict[str, Any]:
        """Generate summary statistics from JTL file"""
        
        results = {
            "tenant": tenant,
            "test_date": datetime.now().isoformat(),
            "total_requests": 0,
            "failed_requests": 0,
            "error_rate": 0.0,
            "endpoints": defaultdict(lambda: {
                "count": 0,
                "errors": 0,
                "response_times": [],
                "min_rt": 0,
                "max_rt": 0,
                "avg_rt": 0,
                "p90_rt": 0,
                "p95_rt": 0,
                "p99_rt": 0
            })
        }
        
        # Parse JTL file
        with open(jtl_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                endpoint = row.get('label', '')
                success = row.get('success', 'true') == 'true'
                response_time = int(row.get('elapsed', 0))
                
                results["total_requests"] += 1
                if not success:
                    results["failed_requests"] += 1
                
                # Endpoint specific stats
                ep_stats = results["endpoints"][endpoint]
                ep_stats["count"] += 1
                ep_stats["response_times"].append(response_time)
                if not success:
                    ep_stats["errors"] += 1
        
        # Calculate statistics
        results["error_rate"] = (results["failed_requests"] / results["total_requests"] * 100) if results["total_requests"] > 0 else 0
        
        for endpoint, stats in results["endpoints"].items():
            if stats["response_times"]:
                stats["min_rt"] = min(stats["response_times"])
                stats["max_rt"] = max(stats["response_times"])
                stats["avg_rt"] = statistics.mean(stats["response_times"])
                stats["p90_rt"] = statistics.quantiles(stats["response_times"], n=10)[8] if len(stats["response_times"]) > 10 else stats["max_rt"]
                stats["p95_rt"] = statistics.quantiles(stats["response_times"], n=20)[18] if len(stats["response_times"]) > 20 else stats["max_rt"]
                stats["p99_rt"] = statistics.quantiles(stats["response_times"], n=100)[98] if len(stats["response_times"]) > 100 else stats["max_rt"]
                stats["error_rate"] = (stats["errors"] / stats["count"] * 100) if stats["count"] > 0 else 0
                # Remove raw response times from final report
                del stats["response_times"]
        
        return results
    
    def generate_html_report(self, summary: Dict[str, Any], output_file: str):
        """Generate HTML report from summary data"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>YMS Dashboard Stress Test Report - {summary['tenant']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; }}
        .metric-value {{ font-size: 1.2em; }}
        .error {{ color: #d9534f; }}
        .success {{ color: #5cb85c; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .warning {{ background-color: #fff3cd; }}
        .danger {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <h1>YMS Dashboard Stress Test Report</h1>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <div class="metric">
            <span class="metric-label">Tenant:</span>
            <span class="metric-value">{summary['tenant']}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Test Date:</span>
            <span class="metric-value">{datetime.fromisoformat(summary['test_date']).strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Total Requests:</span>
            <span class="metric-value">{summary['total_requests']:,}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Failed Requests:</span>
            <span class="metric-value {'' if summary['failed_requests'] == 0 else 'error'}">{summary['failed_requests']:,}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Error Rate:</span>
            <span class="metric-value {'' if summary['error_rate'] < 1 else 'error'}">{summary['error_rate']:.2f}%</span>
        </div>
    </div>
    
    <h2>Endpoint Performance</h2>
    <table>
        <tr>
            <th>Endpoint</th>
            <th>Requests</th>
            <th>Errors</th>
            <th>Error Rate</th>
            <th>Min RT (ms)</th>
            <th>Avg RT (ms)</th>
            <th>P90 RT (ms)</th>
            <th>P95 RT (ms)</th>
            <th>P99 RT (ms)</th>
            <th>Max RT (ms)</th>
        </tr>
"""
        
        for endpoint, stats in summary['endpoints'].items():
            row_class = ''
            if stats['error_rate'] > 5:
                row_class = 'danger'
            elif stats['error_rate'] > 1:
                row_class = 'warning'
            
            html_content += f"""
        <tr class="{row_class}">
            <td>{endpoint}</td>
            <td>{stats['count']:,}</td>
            <td>{stats['errors']:,}</td>
            <td>{stats['error_rate']:.2f}%</td>
            <td>{stats['min_rt']:.0f}</td>
            <td>{stats['avg_rt']:.0f}</td>
            <td>{stats['p90_rt']:.0f}</td>
            <td>{stats['p95_rt']:.0f}</td>
            <td>{stats['p99_rt']:.0f}</td>
            <td>{stats['max_rt']:.0f}</td>
        </tr>
"""
        
        html_content += """
    </table>
    
    <div class="summary">
        <h3>SLA Compliance</h3>
        <p>✓ Response Time SLA (P95 < 2000ms): <span class="metric-value">""" + (
            "PASS" if all(stats['p95_rt'] < 2000 for stats in summary['endpoints'].values()) else "FAIL"
        ) + """</span></p>
        <p>✓ Error Rate SLA (< 1%): <span class="metric-value">""" + (
            "PASS" if summary['error_rate'] < 1 else "FAIL"
        ) + """</span></p>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)
    
    def generate_csv_report(self, summary: Dict[str, Any], output_file: str):
        """Generate CSV report from summary data"""
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Endpoint', 'Total Requests', 'Failed Requests', 'Error Rate (%)', 
                           'Min RT (ms)', 'Avg RT (ms)', 'P90 RT (ms)', 'P95 RT (ms)', 
                           'P99 RT (ms)', 'Max RT (ms)'])
            
            # Data rows
            for endpoint, stats in summary['endpoints'].items():
                writer.writerow([
                    endpoint,
                    stats['count'],
                    stats['errors'],
                    f"{stats['error_rate']:.2f}",
                    stats['min_rt'],
                    f"{stats['avg_rt']:.0f}",
                    f"{stats['p90_rt']:.0f}",
                    f"{stats['p95_rt']:.0f}",
                    f"{stats['p99_rt']:.0f}",
                    stats['max_rt']
                ])
            
            # Summary row
            writer.writerow([])
            writer.writerow(['TOTAL', summary['total_requests'], summary['failed_requests'], 
                           f"{summary['error_rate']:.2f}"])
    
    def generate_all_reports(self, jtl_file: str, tenant: str, test_name: str):
        """Generate all report formats"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate summary
        summary = self.generate_summary_report(jtl_file, tenant)
        
        # Save summary JSON
        summary_file = os.path.join(self.results_dir, "summary", f"{test_name}_{tenant}_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate HTML report
        html_file = os.path.join(self.results_dir, "html", f"{test_name}_{tenant}_{timestamp}.html")
        self.generate_html_report(summary, html_file)
        
        # Generate CSV report
        csv_file = os.path.join(self.results_dir, "csv", f"{test_name}_{tenant}_{timestamp}.csv")
        self.generate_csv_report(summary, csv_file)
        
        return {
            "summary": summary_file,
            "html": html_file,
            "csv": csv_file
        }