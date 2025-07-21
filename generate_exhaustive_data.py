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
    "carrierapi": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJNQUN5NDl5QkQwbDJPNV9YUUVFQ05WUmd2ZkhpTmYydENYTVdQYTN4RWRBIn0.eyJleHAiOjE3NTI4NDUyNzEsImlhdCI6MTc1Mjg0MzQ3MSwiYXV0aF90aW1lIjoxNzUyODQzNDY5LCJqdGkiOiIwM2MwNDdjYi1mNDUzLTRjMDYtYjg2Yi02Njg1NmEyYTczNzEiLCJpc3MiOiJodHRwczovL2R5LWRldi5mb3Vya2l0ZXMuY29tL2tleWNsb2FrL3JlYWxtcy9ZTVMiLCJzdWIiOiIxMGJlM2Q4OS1lODU0LTRlY2EtYmQyOS0wYzI0NzllNGJhMjQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiNDA1MDA5NTYtZmQ1NS00ZmUyLTlkZmUtZDU3Y2IxODM3YzczIiwic2Vzc2lvbl9zdGF0ZSI6ImRiZjI3ODE0LTU5ZTQtNGFlYi1hZmUwLTUyMzRiOTZmZGRlNCIsImFjciI6IjEiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoiY2FycmllcmFwaSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicGVybWlzc2lvbnMiOlsicmVhZF9sb2Fkc19hcGkiLCJtb2RpZnlfdG1zX2FwaSIsInJlYWRfc3dpdGNoZXJfdmVoaWNsZXNfYXBpIiwiZm9yY2Vfc3dpdGNoZXJfbG9nb3V0X2FwaSIsInJlYWRfY2FycmllcnNfYXBpIiwibW9kaWZ5X3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfZ2F0ZV9wYXNzZXNfYXBpIiwibW9kaWZ5X3lhcmRfcHJvcGVydGllc19hcGkiLCJtb2RpZnlfYXBwb2ludG1lbnRzX2FwaSIsIm1vZGlmeV93bXNfYXBpIiwibW9kaWZ5X3VzZXJzX2FwaSIsIm1vZGlmeV9ydWxlc19hcGkiLCJtb2RpZnlfdHJhaWxlcnNfYXBpIiwicmVhZF9nYXRlX2d1YXJkc19hcGkiLCJyZWFkX2RlbGl2ZXJpZXNfYXBpIiwicmVhZF9tb3ZlX3JlcXVlc3RzX2FwaSIsIm1vZGlmeV90cmFpbGVyX3RhZ3NfYXBpIiwidW1hX2F1dGhvcml6YXRpb24iLCJyZWFkX2N0cGF0X3NldHRpbmdzIiwicmVhZF93ZWJob29rc19hcGkiLCJyZWFkX2dhdGVzX2FwaSIsInJlYWRfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsInJlYWRfc2l0ZV9sZXZlbF9jb250cm9sIiwicmVhZF9jdXN0b21fZmllbGRzX2FwaSIsIm1vZGlmeV9jYXJyaWVyc19hcGkiLCJtb2RpZnlfc2l0ZXNfYXBpIiwibW9kaWZ5X2N0cGF0X3NldHRpbmdzIiwibW9kaWZ5X2N1c3RvbV9maWVsZHNfYXBpIiwic3VwZXJfYWRtaW5fYXBpIiwibW9kaWZ5X2RlbGl2ZXJpZXNfYXBpIiwibW9kaWZ5X2FkZHJlc3Nlc19hcGkiLCJyZWFkX3RyYWlsZXJfbGlzdF9hcGkiLCJtb2RpZnlfZW1lcmdlbmN5X21lc3NhZ2VfYXBpIiwibW9kaWZ5X3N3aXRjaGVyc19hcGkiLCJyZWFkX3RyYWlsZXJfY2hlY2tzX2FwaSIsIm1vZGlmeV9hbGxfdXNlcnNfYXBpIiwicmVhZF90cmFpbGVyc19hcGkiLCJtb2RpZnlfYXV0aF9jbGllbnRzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2xpc3RfYXVkaXRfYXBpIiwibW9kaWZ5X2N1c3RvbWVyc19hcGkiLCJzaGFyZWRfcmVwb3J0X2NyZWF0ZV9hcGkiLCJyZWFkX2FsbF91c2Vyc19hcGkiLCJtb2RpZnlfd2ViaG9va3NfYXBpIiwibW9kaWZ5X29jY3VwYW5jeV9zZW5zb3JzX2FwaSIsIm1vZGlmeV9jYXJyaWVyX3NpdGVzX2VsaWdpYmlsaXR5IiwibW9kaWZ5X2xvYWRzX2FwaSIsIm1vZGlmeV9yZXBvcnRzX2FwaSIsIm1vZGlmeV9nYXRlX3Bhc3Nlc19hcGkiLCJtb2RpZnlfdHJhaWxlcl9saXN0X2FwaSIsInJlYWRfZ2VvZmVuY2VzX2FwaSIsIm1vZGlmeV9zaXRlX2xpY2Vuc2VzX2FwaSIsInJlYWRfY3VzdG9tZXJzX2FwaSIsInJlYWRfa2lvc2tfaGVscGNvZGVfYXBpIiwicmVhZF9yZWN1cnJpbmdfZGVsaXZlcmllc19hcGkiLCJyZWFkX3VzZXJzX2FwaSIsInJlYWRfYWRkcmVzc2VzX2FwaSIsInJlYWRfcnVsZXNfYXBpIiwibW9kaWZ5X2dhdGVzX2FwaSIsIm1vZGlmeV9tb3ZlX3JlcXVlc3RzX2FwaSIsIm9mZmxpbmVfYWNjZXNzIiwibW9kaWZ5X2ZyZWlnaHRfYXBpIiwicmVhZF95YXJkX3Byb3BlcnRpZXNfYXBpIiwibWlncmF0aW9ucy12ZXJzaW9uLXltcy1hcGkiLCJmb3Vya2l0ZXNfaW50ZXJuYWxfYXBpIiwicmVhZF9zaXRlc19hcGkiLCJtb2RpZnlfZ2F0ZV9ndWFyZHNfYXBpIiwicmVhZF90cmFpbGVyX3RhZ3NfYXBpIiwibW9kaWZ5X3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsIm1vZGlmeV9nYXRlX2FwaSIsInJlYWRfbG9jYXRpb25zX2FwaSIsInJlYWRfYXBwb2ludG1lbnRzX2FwaSIsInJlYWRfZnJlaWdodF9hcGkiLCJyZWFkX3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X3NjaGVkdWxlc19hcGkiLCJzaGFyZWRfcmVwb3J0X2FkbWluX2FwaSIsIm1vZGlmeV9sb2NhdGlvbnNfYXBpIiwicmVhZF9yZXBvcnRzX2FwaSIsInJlYWRfZXJwX3N1Ym1pc3Npb25zX2FwaSIsIm1vZGlmeV9lcnBfc3VibWlzc2lvbnNfYXBpIiwibW9kaWZ5X3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X3NpdGVfbGV2ZWxfY29udHJvbCIsInJlYWRfc2NoZWR1bGVzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2NoZWNrc19hcGkiLCJ0ZW5hbnRfdmFsaWRhdGlvbl9ub3RfcmVxdWlyZWQiLCJyZWFkX29jY3VwYW5jeV9zZW5zb3JzX2FwaSJdLCJuYW1lIjoiQXJwaXQgUyIsImdyb3VwcyI6WyJPT1MgQ29udHJvbCIsIlN1cGVyIEFkbWluIiwiU3dpdGNoZXIgVGVhbXMgU2V0dGluZ3MiXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYXJwaXQuc2FiaGFyd2FsQGZvdXJraXRlcy5jb20iLCJnaXZlbl9uYW1lIjoiQXJwaXQiLCJmYW1pbHlfbmFtZSI6IlMiLCJlbWFpbCI6ImFycGl0LnNhYmhhcndhbEBmb3Vya2l0ZXMuY29tIn0.cJq3RhikbXUdxIi7eq6-JFZ6jL2rTO1KgnGSyltO5ieCvM4OU8UeBeSIRUIXeygbQlENhwBZUJYCg63hKE8DRhz1ilml8_G9cnPZuuKeanHi1rK9Mk5QWL9_lmHWWjNgT7AAYcP8rfCSHSw3KMos3m2PJ8J91_spU6f48SJ6P3eGAH8M3EA6ysobK6LLxM5XH2_yVabOzQukUVb-7asDVp4nxkTnTtOyeeEw7CPlzvzjl5WRSOX2GJgNfQo1dnsO_e66PxNkCYfe4k8AMk0RA-RfoGkSASk7pp9PIjJFqmWzXHA1r2N33QwqdC9IGKyAbKEnZXgjK-4cGE5-mf_knQ"
}
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
        tenant_carriers = str(data["carrier_ids"]).replace(" ", "")
        auth_token = f'"{data["auth_token"]}"'

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