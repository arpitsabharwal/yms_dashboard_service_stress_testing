import click
import json
from generators.payload_generators import get_generator
from utils.tenant_manager import TenantManager
from utils.logger import stress_logger
from utils.report_generator import ReportGenerator
from validators.response_validators import ResponseValidator

@click.group()
def cli():
    """YMS Dashboard Stress Testing CLI"""
    pass

@cli.command()
@click.option('--tenant', required=True, help='Tenant name')
@click.option('--endpoint', required=True, help='API endpoint name')
@click.option('--count', default=1, help='Number of payloads to generate')
@click.option('--output-file', help='Output file for payloads')
def generate(tenant, endpoint, count, output_file):
    """Generate test payloads for specified endpoint"""
    try:
        stress_logger.info(f"Generating {count} payloads for tenant: {tenant}, endpoint: {endpoint}")
        
        manager = TenantManager()
        tenant_config = manager.get_tenant_config(tenant)
        
        generator = get_generator(endpoint, tenant_config)
        
        payloads = []
        for i in range(count):
            payload = generator.generate()
            payloads.append(payload)
            
            if not output_file:
                click.echo(json.dumps(payload, indent=2))
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(payloads, f, indent=2)
            stress_logger.info(f"Saved {count} payloads to {output_file}")
            
    except Exception as e:
        stress_logger.error(f"Failed to generate payloads: {str(e)}", exc_info=e)
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
@click.option('--response-file', required=True, type=click.File('r'), help='Response file to validate')
@click.option('--endpoint', required=True, help='API endpoint name')
def validate(response_file, endpoint):
    """Validate API response"""
    try:
        validator = ResponseValidator()
        
        response_data = json.load(response_file)
        
        valid, results = validator.validate_response(
            endpoint=endpoint,
            response_code=response_data.get('status_code', 200),
            response_body=json.dumps(response_data.get('body', {})),
            response_time=response_data.get('response_time', 0)
        )
        
        click.echo(json.dumps(results, indent=2))
        
        if not valid:
            stress_logger.warning(f"Validation failed for {endpoint}")
            click.echo("Validation FAILED", err=True)
            exit(1)
        else:
            stress_logger.info(f"Validation passed for {endpoint}")
            click.echo("Validation PASSED")
            
    except Exception as e:
        stress_logger.error(f"Validation error: {str(e)}", exc_info=e)
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
@click.option('--jtl-file', required=True, help='JMeter JTL results file')
@click.option('--tenant', required=True, help='Tenant name')
@click.option('--test-name', default='stress-test', help='Test name for report')
def report(jtl_file, tenant, test_name):
    """Generate reports from JMeter results"""
    try:
        stress_logger.info(f"Generating reports for {test_name} - {tenant}")
        
        generator = ReportGenerator()
        report_files = generator.generate_all_reports(jtl_file, tenant, test_name)
        
        click.echo("Reports generated successfully:")
        click.echo(f"  - Summary: {report_files['summary']}")
        click.echo(f"  - HTML: {report_files['html']}")
        click.echo(f"  - CSV: {report_files['csv']}")
        
        # Display summary stats
        with open(report_files['summary'], 'r') as f:
            summary = json.load(f)
            click.echo(f"\nTest Summary:")
            click.echo(f"  Total Requests: {summary['total_requests']:,}")
            click.echo(f"  Failed Requests: {summary['failed_requests']:,}")
            click.echo(f"  Error Rate: {summary['error_rate']:.2f}%")
            
    except Exception as e:
        stress_logger.error(f"Report generation failed: {str(e)}", exc_info=e)
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

if __name__ == '__main__':
    cli()