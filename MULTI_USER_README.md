# Multi-User Token Generation

This feature allows you to generate tokens for multiple users across different tenants, enabling more realistic stress testing with different user personas.

## Features

- Generate tokens for multiple users in a single run
- Support for multiple tenants per user
- Automatic admin token refresh for large batches
- Detailed logging and summary reports
- Integration with test data generation

## Quick Start

### 1. Create Configuration

Copy the example configuration and customize it:

```bash
cp config/multi_user_example.json config/multi_user.json
```

Edit `config/multi_user.json`:

```json
{
  "environment": "staging",
  "keycloak_admin": "admin",
  "keycloak_password": "your_admin_password",
  "users": [
    {
      "email": "user1@company.com",
      "password": "Password1!",
      "tenants": ["tenant1", "tenant2"],
      "description": "User 1 description"
    },
    {
      "email": "user2@company.com",
      "password": "Password2!",
      "tenants": ["tenant3"],
      "description": "User 2 description"
    }
  ]
}
```

### 2. Generate Tokens

Run the multi-user token generator:

```bash
# Using default config (config/multi_user.json)
python3 generate_multi_user_tokens.py

# Using specific config file
python3 generate_multi_user_tokens.py --config config/multi_user_staging.json

# Override environment
python3 generate_multi_user_tokens.py --env prod

# Specify output file
python3 generate_multi_user_tokens.py --output tokens/my_tokens.json
```

### 3. Generate Test Data

Use the generated tokens to create test data:

```bash
# Generate test data from multi-user tokens
python3 generate_multi_user_test_data.py \
  --tokens tokens/multi_user_staging_latest.json \
  --output multi_user_test.csv
```

## Configuration Structure

### User Configuration

Each user in the configuration has:
- `email`: User's email address
- `password`: User's password
- `tenants`: List of tenants the user should be tested with
- `description`: Optional description of the user's role/purpose

### Environment Settings

- `environment`: Target environment (staging, prod, qat, etc.)
- `keycloak_admin`: Admin username for Keycloak
- `keycloak_password`: Admin password for Keycloak

## Output Format

The generated tokens are saved in JSON format:

```json
{
  "generated_at": "2025-08-19T12:49:46",
  "environment": "staging",
  "users": {
    "user1@company.com": {
      "description": "User 1 description",
      "tenants": {
        "tenant1": {
          "token": "Bearer eyJ...",
          "status": "success"
        },
        "tenant2": {
          "token": "Bearer eyJ...",
          "status": "success"
        }
      },
      "success_count": 2,
      "failure_count": 0
    }
  }
}
```

## Use Cases

### 1. Testing Different User Permissions

Create users with different tenant access to test authorization:

```json
{
  "users": [
    {
      "email": "admin@company.com",
      "tenants": ["tenant1", "tenant2", "tenant3"],
      "description": "Admin with full access"
    },
    {
      "email": "viewer@company.com",
      "tenants": ["tenant1"],
      "description": "Read-only user"
    }
  ]
}
```

### 2. Load Distribution Testing

Test with users from different organizations:

```json
{
  "users": [
    {
      "email": "user@customer1.com",
      "tenants": ["customer1"],
      "description": "Customer 1 user"
    },
    {
      "email": "user@customer2.com",
      "tenants": ["customer2"],
      "description": "Customer 2 user"
    }
  ]
}
```

### 3. Multi-Tenant Testing

Test users with access to multiple tenants:

```json
{
  "users": [
    {
      "email": "multi@company.com",
      "tenants": ["shipperapi", "carrierapi", "ge-appliances"],
      "description": "Multi-tenant user"
    }
  ]
}
```

## Troubleshooting

### Token Generation Fails

1. **Check credentials**: Ensure Keycloak admin credentials are correct
2. **User exists**: Verify users exist in Keycloak for the environment
3. **Tenant access**: Confirm users have access to specified tenants
4. **Token expiry**: Admin tokens expire quickly; the script auto-refreshes

### Missing Configuration

If you see "Configuration file not found":
1. Create config from example: `cp config/multi_user_example.json config/multi_user.json`
2. Edit with your credentials and users
3. Ensure JSON is valid

### Performance Tips

- Process users in batches if you have many
- Admin token refreshes automatically every 10 tenants
- Use `--output` to save tokens for reuse
- Latest tokens are always saved to `tokens/multi_user_{env}_latest.json`

## Security Notes

- Never commit `config/multi_user*.json` files (except examples)
- Token files are automatically gitignored
- Use environment-specific configs for different stages
- Rotate passwords regularly
- Store production credentials securely

## Examples

### Staging Environment Setup

```bash
# 1. Create staging config
cat > config/multi_user_staging.json << EOF
{
  "environment": "staging",
  "keycloak_admin": "admin",
  "keycloak_password": "staging_password",
  "users": [
    {
      "email": "test1@fourkites.com",
      "password": "Test@1234",
      "tenants": ["shipperapi", "ge-appliances"]
    }
  ]
}
EOF

# 2. Generate tokens
python3 generate_multi_user_tokens.py --config config/multi_user_staging.json

```

### Production Multi-Tenant Test

```bash
# Generate tokens for production users
python3 generate_multi_user_tokens.py \
  --config config/multi_user_prod.json \
  --env prod
```