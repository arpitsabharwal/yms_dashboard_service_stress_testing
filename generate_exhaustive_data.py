import csv
import itertools
import requests
import sys
import json
import os
from typing import Dict

from config_loader import get_env_config

# ==============================================================================
# 1. DEFINE YOUR TENANT-SPECIFIC DATA
# ==============================================================================
# Customize this section with your actual tenant data.

# how to get facility_ids and carrier_ids:
# - Use the API to fetch facility and carrier data for each tenant.
# - Replace the placeholder values with actual IDs and tokens.


LOCAL = "http://api-proxy:8000"
DEV = "https://dy-dev.fourkites.com"
QAT = "https://dy-qat.fourkites.com"
STRESS = "https://dy-stress.fourkites.com"
STAGING = "https://dy-staging.fourkites.com"
PROD = "https://dy.fourkites.com"


# Tokens will be populated dynamically based on environment
TENANTS_AUTH_TOKEN = {}
# ==============================================================================
# 2. DEFINE THE PARAMETERS FOR EACH API PAYLOAD
# ==============================================================================
# These are the pools of values to be combined for different API requests.
TRAILER_STATES = ["all", "noFlags", "audit", "damaged", "outOfService"]
SHIPMENT_DIRECTIONS = ["Inbound", "Outbound"]
THRESHOLD_HOURS = [12, 24, 48, 72]

# ==============================================================================
# 3. SCRIPT TO GENERATE THE EXHAUSTIVE CSV
# ==============================================================================
HEADER = [
    "api_endpoint", "tenantName", "facilityId", "authToken", "activeUsers", "rpmPerUser",
    "rampUpSeconds", "payload"
]

COUNTER = 1

def get_host_details():
    # accept a argument env which can be dev, local, qat, stress, staging, prod
    if len(sys.argv) < 2:
        print("Usage: python generate_exhaustive_data.py <env>")
        sys.exit(1)
    env = sys.argv[1].lower()
    if env == "local":
        return LOCAL
    elif env == "dev":
        return DEV
    elif env == "qat":
        return QAT
    elif env == "stress":
        return STRESS
    elif env == "staging":
        return STAGING
    elif env == "prod":
        return PROD
    """
    Add logic to fetch the host details based on the environment.
    This could involve reading from a configuration file or environment variables.
    """
    return LOCAL  # Default to local if no valid environment is provided

HOST = get_host_details()

# Import configuration loader
try:
    USE_ENV_FILES = True
except ImportError:
    USE_ENV_FILES = False
    print("Warning: config_loader not found. Using legacy configuration.")


def get_config_for_env(env: str) -> dict:
    """Get configuration for environment, preferring .env files over hardcoded."""
    # Try to load from .env file first
    if USE_ENV_FILES:
        try:
            env_config = get_env_config(env)
            if env_config and env_config.get("keycloak_admin"):
                print(f"✓ Loaded configuration from config/{env}.env")
                return env_config
        except Exception as e:
            print(f"Could not load config/{env}.env: {e}")
    
    print(f"No configuration found for environment: {env}")
    return {}

def refresh_tokens_for_environment(env: str, force_refresh: bool = False) -> Dict[str, str]:
    """
    Refresh tokens for all tenants in the given environment using Keycloak Admin API.
    
    Args:
        env: Environment name (qat, staging, dev, etc.)
        force_refresh: If True, always generate new tokens. If False, only generate if needed.
    
    Returns:
        Dictionary mapping tenant_id to bearer token
    """
    global TENANTS_AUTH_TOKEN
    
    # Check if we already have tokens and force_refresh is False
    if not force_refresh and TENANTS_AUTH_TOKEN:
        print(f"Using existing tokens for {env}. Use force_refresh=True to generate new tokens.")
        return TENANTS_AUTH_TOKEN
    
    config = get_config_for_env(env)
    if not config:
        print(f"No configuration found for environment: {env}")
        return {}
    
    if not config.get("keycloak_admin") or not config.get("keycloak_password"):
        print(f"Keycloak credentials not configured for environment: {env}")
        print("Please update ENV_CONFIG with appropriate credentials.")
        return {}
    
    try:
        # Import the Keycloak token generator
        from keycloak_admin_token_generator import KeycloakAdminTokenGenerator
        
        print(f"\nGenerating fresh tokens for {env} environment...")
        generator = KeycloakAdminTokenGenerator(env)
        
        tokens = generator.generate_tokens_for_all_tenants(
            config["keycloak_admin"],
            config["keycloak_password"],
            config["user_email"],
            config["user_password"],
            config["tenants"]
        )
        
        # Update global TENANTS_AUTH_TOKEN
        TENANTS_AUTH_TOKEN = tokens
        
        # Save tokens to tokens directory with simple naming
        os.makedirs("tokens", exist_ok=True)
        token_file = f"tokens/{env}.json"
        generator.save_tokens(tokens, token_file)
        
        print(f"✓ Tokens refreshed successfully for {env}")
        return tokens
        
    except ImportError:
        print("keycloak_admin_token_generator.py not found.")
        print("Using empty tokens. Please ensure the token generator is available.")
        return {}
    except Exception as e:
        print(f"Error refreshing tokens: {e}")
        return {}

def load_tokens_from_file(env: str) -> bool:
    """
    Try to load tokens from a previously saved file.
    
    Returns:
        True if tokens were loaded successfully, False otherwise
    """
    global TENANTS_AUTH_TOKEN
    
    # Primary location: tokens directory with simple naming
    token_file = f"tokens/{env}.json"
    
    # Check primary location first
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                data = json.load(f)
                
            # Extract tokens from the JSON structure
            if "tokens" in data:
                tokens = {}
                for tenant, token_data in data["tokens"].items():
                    if isinstance(token_data, dict) and "token" in token_data:
                        tokens[tenant] = token_data["token"]
                
                if tokens:
                    TENANTS_AUTH_TOKEN = tokens
                    print(f"✓ Loaded tokens from {token_file}")
                    return True
        except Exception as e:
            print(f"Error loading tokens from {token_file}: {e}")
    
    # Fallback: Try legacy token file locations for backward compatibility
    legacy_files = [
        f"keycloak_{env}_tokens.json",
        f"tokens_{env}_{os.environ.get('USER', 'unknown')}.json",
        f"{env}_tokens.json"
    ]
    
    for legacy_file in legacy_files:
        if os.path.exists(legacy_file):
            try:
                with open(legacy_file, 'r') as f:
                    data = json.load(f)
                    
                # Extract tokens from the JSON structure
                if "tokens" in data:
                    tokens = {}
                    for tenant, token_data in data["tokens"].items():
                        if isinstance(token_data, dict) and "token" in token_data:
                            tokens[tenant] = token_data["token"]
                    
                    if tokens:
                        TENANTS_AUTH_TOKEN = tokens
                        print(f"✓ Loaded tokens from legacy file: {legacy_file}")
                        
                        # Migrate to new location
                        os.makedirs("tokens", exist_ok=True)
                        import shutil
                        shutil.copy2(legacy_file, token_file)
                        print(f"✓ Migrated tokens to {token_file}")
                        return True
            except Exception as e:
                print(f"Error loading tokens from {legacy_file}: {e}")
                continue
    
    return False


def get_carrier_data_for_tenant(tenant_name, bearer_token):
    """
    Fetches the carrier data for a given tenant using the provided bearer token.
    This function should make an API call to retrieve the carrier IDs.
    """ 
    url = f"{HOST}/api/v1/carriers/"
    # call the api and get the data
    # This is a placeholder for the actual API call logic.
    # You would typically use requests or another HTTP library to make the call.
    # For example:
    response = requests.get(url, headers={"Authorization": bearer_token})
    if response.status_code == 200:
        print(f"Successfully fetched carrier IDs for tenant: {tenant_name}")
        carrier_ids = [carrier['id'] for carrier in response.json() if (carrier and carrier.get('id'))]
        return carrier_ids
    else:
        raise Exception(f"Failed to fetch carrier data for tenant {tenant_name}: {response.status_code}")


def get_licensed_facility_ids_for_tenant(tenant_name, bearer_token):
    """
    Fetches the licensed facility IDs for a given tenant using the provided bearer token.
    This function should make an API call to retrieve the facility IDs.
    """
    url = f"{HOST}/api/v1/sites/"
    # call the api and get the data
    # This is a placeholder for the actual API call logic.
    response = requests.get(url, headers={"Authorization": bearer_token})
    if response.status_code == 200:
        print(f"Successfully fetched facility IDs for tenant: {tenant_name}")
        site_ids = [site['id'] for site in response.json() if (site and site.get('id') and site.get('licensed'))]
        return site_ids
    else:
        raise Exception(f"Failed to fetch facility IDs for tenant {tenant_name}: {response.status_code}")



def prepare_tenant_data():
    """
    Prepares the tenant data by fetching facility and carrier IDs.
    This function should be called before generating the exhaustive CSV.
    """
    TENANT_DATA = {}
    for tenant in TENANTS_AUTH_TOKEN:
        bearer_token = TENANTS_AUTH_TOKEN[tenant]
        facility_ids = get_licensed_facility_ids_for_tenant(tenant, bearer_token)
        if not facility_ids:
            print(f"No licensed facilities found for tenant: {tenant}. Skipping...")
            continue

        carrier_ids = get_carrier_data_for_tenant(tenant, bearer_token)
        if not carrier_ids:
            print(f"No carriers found for tenant: {tenant}. Skipping...")

        TENANT_DATA[tenant] = {
            "facility_ids": facility_ids,
            "carrier_ids": carrier_ids,
            "auth_token": bearer_token
        }

    return TENANT_DATA


def generate_exhaustive_csv(filename="test_data.csv"):
    """Generates an exhaustive CSV for all API payload combinations."""
    
    all_rows = []


    tenant_data = prepare_tenant_data()
    if not tenant_data:
        print("No tenant data available. Please check your tenant configurations.")
        return
    
    
    for tenant, data in tenant_data.items():
        print(f"Generating data for tenant: {tenant}...")
        
        # Define common parameter sets
        auth_token = data["auth_token"]

        # --- Endpoints requiring only facilityId ---
        simple_endpoints = [
            "yard-availability", 
            # "task-workload-summary", 
            "task-attention-summary", 
            "door-breakdown-summary"
        ]
        for endpoint in simple_endpoints:
            for facility_id in data["facility_ids"]:
                payload = json.dumps({"facilityId": facility_id})
                # add this COUNTER times
                for _ in range(COUNTER):
                    all_rows.append({
                        "api_endpoint": endpoint, "tenantName": tenant, "facilityId": facility_id, 
                        "authToken": auth_token, "payload": payload
                    })
                

        # --- Endpoints requiring facilityId and carrierIds ---
        carrier_endpoints = [
            "site-occupancy",
            "dwell-time-summary",
            "detention-summary"
        ]
        for endpoint in carrier_endpoints:
            for facility_id in data["facility_ids"]:
                payload = json.dumps({"facilityId": facility_id, "carrierIds": data["carrier_ids"]})
                for _ in range(COUNTER):
                    all_rows.append({
                        "api_endpoint": endpoint, "tenantName": tenant, "facilityId": facility_id, 
                        "authToken": auth_token, "payload": payload
                    })

        # --- Trailer Overview Combinations ---
        params = list(itertools.product(data["facility_ids"], TRAILER_STATES))
        for p in params:
            payload = json.dumps({"facilityId": p[0], "carrierIds": data["carrier_ids"], "trailerState": p[1]})
            all_rows.append({
                "api_endpoint": "trailer-overview", "tenantName": tenant, "facilityId": p[0],
                "authToken": auth_token, "payload": payload
            })

        # --- Trailer Exception Summary Combinations ---
        # Use only one threshold combination per facility for equal distribution
        for facility_id in data["facility_ids"]:
            payload = json.dumps({
                "facilityId": facility_id, 
                "carrierIds": data["carrier_ids"], 
                "lastDetectionTimeThresholdHours": 24,  # Use default threshold
                "inboundLoadedThresholdHours": 48       # Use default threshold
            })
            for _ in range(COUNTER):
                all_rows.append({
                    "api_endpoint": "trailer-exception-summary", "tenantName": tenant, "facilityId": facility_id,
                    "authToken": auth_token, "payload": payload
                })

        # --- Shipment Volume Forecast Combinations ---
        params = list(itertools.product(data["facility_ids"], SHIPMENT_DIRECTIONS))
        for p in params:
            payload = json.dumps({
                "facilityId": p[0],
                "carrierIds": data["carrier_ids"],
                "shipmentDirection": p[1],
                "timeZone": "GMT",
                "numDays": 7,
                "startDate": "2025-07-30",
                "includeShipmentsWithoutCarrier": True
            })
            # for _ in range(2):
            all_rows.append({
                "api_endpoint": "shipment-volume-forecast", "tenantName": tenant, "facilityId": p[0],
                "authToken": auth_token, "payload": payload
            })

    # Write all generated rows to the CSV file
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(HEADER)
        
        for row_dict in all_rows:
            # Fill in default values for JMeter script compatibility
            row_dict.setdefault("activeUsers", 10)
            row_dict.setdefault("rpmPerUser", 60)
            row_dict.setdefault("rampUpSeconds", 1)
            # Write the row by getting values from the dictionary, ensuring correct order
            writer.writerow([row_dict.get(h, "") for h in HEADER])

    print(f"\nSuccessfully generated {len(all_rows)} exhaustive test cases in '{filename}'")

# Main execution
if __name__ == "__main__":
    # Get the environment from command line
    if len(sys.argv) < 2:
        print("Usage: python generate_exhaustive_data.py <env>")
        sys.exit(1)
    
    env = sys.argv[1].lower()
    
    # Initialize tokens for the environment
    print(f"Initializing for {env} environment...")
    
    # First try to load from file
    if not load_tokens_from_file(env):
        # If no file found, generate fresh tokens
        print(f"No cached tokens found. Generating fresh tokens for {env}...")
        refresh_tokens_for_environment(env, force_refresh=True)
    
    # Check if we have tokens now
    if not TENANTS_AUTH_TOKEN:
        print("\nWarning: No tokens available. The test data will be generated without auth tokens.")
        print("To generate tokens, ensure:")
        print("1. keycloak_admin_token_generator.py is available")
        print("2. Credentials are configured in ENV_CONFIG")
        print("")
    else:
        print(f"\n✓ Loaded tokens for {len(TENANTS_AUTH_TOKEN)} tenants")
    
    # Run the generator
    generate_exhaustive_csv()