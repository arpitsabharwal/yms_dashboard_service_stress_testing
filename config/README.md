# Environment Configuration

This directory contains environment-specific configuration files for the YMS Dashboard stress testing framework.

## Setup

1. Copy `example.env.template` to create environment-specific config files:
   ```bash
   cp example.env.template qat.env
   cp example.env.template staging.env
   cp example.env.template prod.env
   ```

2. Edit each `.env` file with the appropriate credentials and settings for that environment.

## Configuration Files

Each environment should have its own `.env` file:
- `qat.env` - QAT environment configuration
- `staging.env` - Staging environment configuration  
- `dev.env` - Development environment configuration
- `stress.env` - Stress testing environment configuration
- `prod.env` - Production environment configuration (use with caution!)
- `local.env` - Local development configuration

## Security

⚠️ **IMPORTANT**: Never commit `.env` files to version control! They contain sensitive credentials.

The `.gitignore` file is configured to exclude all `*.env` files from git tracking.

## Configuration Parameters

Each `.env` file should contain:

```bash
# Base URL for the environment
BASE_URL=https://dy-{environment}.fourkites.com

# Keycloak Admin Credentials
KEYCLOAK_ADMIN=admin
KEYCLOAK_PASSWORD=your_admin_password

# Test User Credentials  
USER_EMAIL=user@company.com
USER_PASSWORD=your_user_password

# Tenants to test (comma-separated)
TENANTS=shipperapi,carrierapi,ge-appliances,fritolay
```

## Usage

The configuration is automatically loaded when running:
```bash
python generate_exhaustive_data.py <env>
```

To verify configuration:
```bash
python config_loader.py <env>
```

## Fallback

If no `.env` file exists, the system will fall back to hardcoded configuration in `generate_exhaustive_data.py` (if available).