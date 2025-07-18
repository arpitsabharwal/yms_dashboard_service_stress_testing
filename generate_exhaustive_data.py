import csv
import itertools
import requests
import sys

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


TENANTS_AUTH_TOKEN = {
    "yms": 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIzTjJrV25CVWpqTkFQRDZBSHRlWTNGa2c0eTlHTDI0M0FQUG1VSDBvMS1NIn0.eyJleHAiOjE3NTI4NzM0NzUsImlhdCI6MTc1MjgzNzUxNiwiYXV0aF90aW1lIjoxNzUyODM3NDc1LCJqdGkiOiI1MTYwNGRlMC00NWRkLTQyNGEtYmU3MC1iZDgwNTVjZjFhMmYiLCJpc3MiOiJodHRwOi8vaG9zdC5kb2NrZXIuaW50ZXJuYWw6ODA4MC9hdXRoL3JlYWxtcy9ZTVMiLCJzdWIiOiIxMDk3MmE0OS02ZjU3LTQ4MzEtYTJjMS00MTE3MDAyOTcxYTMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiOTIzOWJiMGItYTBiYi00NjQ4LTg5N2QtNjY4NDIxMGU1YTg4Iiwic2Vzc2lvbl9zdGF0ZSI6IjhmMzc3MTJlLTVjNDktNDY4OS04ZjMxLTA4ZGI5MmQxODkxZSIsImFjciI6IjAiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoieW1zIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwZXJtaXNzaW9ucyI6WyJyZWFkX2xvYWRzX2FwaSIsIm1vZGlmeV90bXNfYXBpIiwicmVhZF9zd2l0Y2hlcl92ZWhpY2xlc19hcGkiLCJyZWFkX2NhcnJpZXJzX2FwaSIsIm1vZGlmeV9zd2l0Y2hlcl92ZWhpY2xlc19hcGkiLCJyZWFkX2dhdGVfcGFzc2VzX2FwaSIsIm1vZGlmeV95YXJkX3Byb3BlcnRpZXNfYXBpIiwibW9kaWZ5X2FwcG9pbnRtZW50c19hcGkiLCJtb2RpZnlfd21zX2FwaSIsIm1vZGlmeV91c2Vyc19hcGkiLCJtb2RpZnlfcnVsZXNfYXBpIiwibW9kaWZ5X3RyYWlsZXJzX2FwaSIsInJlYWRfZ2F0ZV9ndWFyZHNfYXBpIiwicmVhZF9kZWxpdmVyaWVzX2FwaSIsInJlYWRfbW92ZV9yZXF1ZXN0c19hcGkiLCJtb2RpZnlfdHJhaWxlcl90YWdzX2FwaSIsInVtYV9hdXRob3JpemF0aW9uIiwicmVhZF9jdHBhdF9zZXR0aW5ncyIsInJlYWRfd2ViaG9va3NfYXBpIiwicmVhZF9nYXRlc19hcGkiLCJyZWFkX2NhcnJpZXJfc2l0ZXNfZWxpZ2liaWxpdHkiLCJyZWFkX3NpdGVfbGV2ZWxfY29udHJvbCIsInJlYWRfY3VzdG9tX2ZpZWxkc19hcGkiLCJtb2RpZnlfY2FycmllcnNfYXBpIiwibW9kaWZ5X3NpdGVzX2FwaSIsIm1vZGlmeV9jdHBhdF9zZXR0aW5ncyIsIm1vZGlmeV9jdXN0b21fZmllbGRzX2FwaSIsInN1cGVyX2FkbWluX2FwaSIsIm1vZGlmeV9kZWxpdmVyaWVzX2FwaSIsIm1vZGlmeV9hZGRyZXNzZXNfYXBpIiwibW9kaWZ5X2VtZXJnZW5jeV9tZXNzYWdlX2FwaSIsIm1vZGlmeV9zd2l0Y2hlcnNfYXBpIiwicmVhZF90cmFpbGVyX2NoZWNrc19hcGkiLCJtb2RpZnlfYWxsX3VzZXJzX2FwaSIsInJlYWRfdHJhaWxlcnNfYXBpIiwibW9kaWZ5X2F1dGhfY2xpZW50c19hcGkiLCJtb2RpZnlfY3VzdG9tZXJzX2FwaSIsInNoYXJlZF9yZXBvcnRfY3JlYXRlX2FwaSIsInJlYWRfYWxsX3VzZXJzX2FwaSIsIm1vZGlmeV93ZWJob29rc19hcGkiLCJtb2RpZnlfb2NjdXBhbmN5X3NlbnNvcnNfYXBpIiwibW9kaWZ5X2xvYWRzX2FwaSIsIm1vZGlmeV9jYXJyaWVyX3NpdGVzX2VsaWdpYmlsaXR5IiwibW9kaWZ5X3JlcG9ydHNfYXBpIiwibW9kaWZ5X2dhdGVfcGFzc2VzX2FwaSIsIm1vZGlmeV9zaXRlX2xpY2Vuc2VzX2FwaSIsInJlYWRfY3VzdG9tZXJzX2FwaSIsInJlYWRfa2lvc2tfaGVscGNvZGVfYXBpIiwicmVhZF9yZWN1cnJpbmdfZGVsaXZlcmllc19hcGkiLCJyZWFkX2FkZHJlc3Nlc19hcGkiLCJyZWFkX3VzZXJzX2FwaSIsInJlYWRfcnVsZXNfYXBpIiwibW9kaWZ5X2dhdGVzX2FwaSIsIm1vZGlmeV9tb3ZlX3JlcXVlc3RzX2FwaSIsIm9mZmxpbmVfYWNjZXNzIiwibW9kaWZ5X2ZyZWlnaHRfYXBpIiwicmVhZF95YXJkX3Byb3BlcnRpZXNfYXBpIiwibWlncmF0aW9ucy12ZXJzaW9uLXltcy1hcGkiLCJmb3Vya2l0ZXNfaW50ZXJuYWxfYXBpIiwicmVhZF9zaXRlc19hcGkiLCJtb2RpZnlfZ2F0ZV9ndWFyZHNfYXBpIiwicmVhZF90cmFpbGVyX3RhZ3NfYXBpIiwibW9kaWZ5X3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsIm1vZGlmeV9nYXRlX2FwaSIsInJlYWRfbG9jYXRpb25zX2FwaSIsInJlYWRfYXBwb2ludG1lbnRzX2FwaSIsInJlYWRfZnJlaWdodF9hcGkiLCJyZWFkX3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X3NjaGVkdWxlc19hcGkiLCJzaGFyZWRfcmVwb3J0X2FkbWluX2FwaSIsIm1vZGlmeV9sb2NhdGlvbnNfYXBpIiwicmVhZF9yZXBvcnRzX2FwaSIsInJlYWRfZXJwX3N1Ym1pc3Npb25zX2FwaSIsIm1vZGlmeV9lcnBfc3VibWlzc2lvbnNfYXBpIiwibW9kaWZ5X3NpdGVfbGV2ZWxfY29udHJvbCIsInJlYWRfc2NoZWR1bGVzX2FwaSIsIm1vZGlmeV9zYXZlZF9maWx0ZXJzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2NoZWNrc19hcGkiLCJyZWFkX29jY3VwYW5jeV9zZW5zb3JzX2FwaSIsInRlbmFudF92YWxpZGF0aW9uX25vdF9yZXF1aXJlZCJdLCJuYW1lIjoiSW5zaWdodCBuZXd0IiwiZ3JvdXBzIjpbIk9PUyBDb250cm9sIiwiU3VwZXIgQWRtaW4iLCJTdXBlcnVzZXIiXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiaW5zaWdodEBibHVlLW5ld3QuY29tIiwiZ2l2ZW5fbmFtZSI6Ikluc2lnaHQiLCJmYW1pbHlfbmFtZSI6Im5ld3QiLCJlbWFpbCI6Imluc2lnaHRAYmx1ZS1uZXd0LmNvbSJ9.lpfk06hU2g-1IHpJyxH5phUveQoniK4QGAqwhrIkMWo7BSwl2gtViVVsI6WlxOrGYmZm0hFMrnR7gtI2yb960cfy-NsOkQ5yQhZjQ7b8FmcKCmkgtO64mcYOmzcZ8VyY39XA4LKP-_nz618Wws47VgXo5bKT6s0a9tT9PXwFilyuXgARfIgiDipY4i72O4lSTbj4-mLuKoRuDwptZXp7LWareOWVRW4II_QB51I6DszUqWRPnZQFIrMIks0g9GbVHpKep5cdrivKuh8K-Gf2yaYWjfo4r8JHD4_BRYlvi8fQJSD7yCbRLyRCqzaYRiNLBXbLSUAdpHHzGPJRTrFQCQ'}

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
    "rampUpSeconds", "carrierIds", "trailerState", "lastDetectionTimeThresholdHours",
    "inboundLoadedThresholdHours", "shipmentDirection"
]


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
            "auth_token": '"' + f'{bearer_token}' + '"'
        }

    return TENANT_DATA


def generate_exhaustive_csv(filename="test_data_combined1.csv"):
    """Generates an exhaustive CSV for all API payload combinations."""
    
    all_rows = []


    tenant_data = prepare_tenant_data()
    if not tenant_data:
        print("No tenant data available. Please check your tenant configurations.")
        return
    
    
    for tenant, data in tenant_data.items():
        print(f"Generating data for tenant: {tenant}...")
        
        # Define common parameter sets
        tenant_carriers = str(data["carrier_ids"]).replace(" ", "")
        auth_token = str(data["auth_token"])
        
        # --- Endpoints requiring only facilityId ---
        simple_endpoints = [
            "yard-availability", 
            "task-workload-summary", 
            "task-attention-summary", 
            "door-breakdown-summary"
        ]
        for endpoint in simple_endpoints:
            for facility_id in data["facility_ids"]:
                all_rows.append({
                    "api_endpoint": endpoint, "tenantName": tenant, "facilityId": facility_id, "authToken": auth_token
                })

        # --- Endpoints requiring facilityId and carrierIds ---
        carrier_endpoints = [
            "site-occupancy",
            "dwell-time-summary",
            "detention-summary"
        ]
        for endpoint in carrier_endpoints:
            for facility_id in data["facility_ids"]:
                 all_rows.append({
                    "api_endpoint": endpoint, "tenantName": tenant, "facilityId": facility_id, 
                    "authToken": auth_token, "carrierIds": tenant_carriers
                })

        # --- Trailer Overview Combinations ---
        params = list(itertools.product(data["facility_ids"], [tenant_carriers], TRAILER_STATES))
        for p in params:
            all_rows.append({
                "api_endpoint": "trailer-overview", "tenantName": tenant, "facilityId": p[0],
                "authToken": auth_token, "carrierIds": p[1], "trailerState": p[2]
            })

        # --- Trailer Exception Summary Combinations ---
        params = list(itertools.product(data["facility_ids"], [tenant_carriers], THRESHOLD_HOURS, THRESHOLD_HOURS))
        for p in params:
            all_rows.append({
                "api_endpoint": "trailer-exception-summary", "tenantName": tenant, "facilityId": p[0],
                "authToken": auth_token, "carrierIds": p[1], 
                "lastDetectionTimeThresholdHours": p[2], "inboundLoadedThresholdHours": p[3]
            })

        # --- Shipment Volume Forecast Combinations ---
        params = list(itertools.product(data["facility_ids"], [tenant_carriers], SHIPMENT_DIRECTIONS))
        for p in params:
            all_rows.append({
                "api_endpoint": "shipment-volume-forecast", "tenantName": tenant, "facilityId": p[0],
                "authToken": auth_token, "carrierIds": p[1], "shipmentDirection": p[2]
            })

    # Write all generated rows to the CSV file
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        
        for row_dict in all_rows:
            # Fill in default values for JMeter script compatibility
            row_dict.setdefault("activeUsers", 10)
            row_dict.setdefault("rpmPerUser", 60)
            row_dict.setdefault("rampUpSeconds", 1)
            # Write the row by getting values from the dictionary, ensuring correct order
            writer.writerow([row_dict.get(h, "") for h in HEADER])

    print(f"\nSuccessfully generated {len(all_rows)} exhaustive test cases in '{filename}'")

# Run the generator
generate_exhaustive_csv()