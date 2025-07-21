# YMS Dashboard Service - Stress Testing

This repository contains a set of scripts and configurations for running stress tests on the YMS Dashboard Service. It provides tools to generate exhaustive test payloads and execute high-load scenarios against various service environments.

-----

## Prerequisites

To run these tests, you will need the following software installed:

  * **Bash:** For executing the `run_test.sh` script.
  * **JMeter (version 5.6.3 or compatible):** For running the stress test plan.
  * **Python 3:** For running the `generate_exhaustive_data.py` script.
  * **Python Libraries:**
      * `csv`
      * `itertools`
      * `requests`
      * `sys`

-----

## Setup and Configuration

### Step 1: Configure Tenant Data

Before generating test data, you must configure the `generate_exhaustive_data.py` script with the appropriate tenant information.

Open `generate_exhaustive_data.py` and update the `TENANTS_AUTH_TOKEN` dictionary. Add each tenant you want to test along with a valid bearer token for authentication.

**Example:**

```python
TENANTS_AUTH_TOKEN = {
    "yms": "Bearer eyJhbGciOiJSUzI1Ni...",
    "another_tenant": "Bearer eyJhbGciOiJSUzI1Ni..."
}
```

### Step 2: Define API Parameters

The `generate_exhaustive_data.py` script uses predefined lists to create a wide range of test case combinations. You can modify these lists to suit your testing needs:

  * `TRAILER_STATES`: A list of possible trailer states to be used in the "trailer-overview" API endpoint tests (e.g., "all", "noFlags", "audit").
  * `SHIPMENT_DIRECTIONS`: A list of shipment directions for the "shipment-volume-forecast" endpoint (e.g., "Inbound", "Outbound").
  * `THRESHOLD_HOURS`: A list of time thresholds in hours for the "trailer-exception-summary" endpoint.

### Step 3: JMeter Test Plan

The `test_plan.jmx` file is the core JMeter test plan. It is pre-configured to read the generated `test_data.csv` file and will randomly select and execute API requests based on the data in the file.

-----

## Generating Test Data

The `generate_exhaustive_data.py` script is used to create a CSV file containing all possible combinations of test data based on the configured tenants and API parameters.

To run the script, use the following command, specifying the target environment:

```bash
python generate_exhaustive_data.py <env>
```

The `<env>` argument can be one of the following: `local`, `dev`, `qat`, `stress`, `staging`, or `prod`.

**Example:**

```bash
python generate_exhaustive_data.py dev
```

This will create a `test_data.csv` file in the same directory, which will be used by the JMeter test plan. The columns in the CSV file include `api_endpoint`, `tenantName`, `facilityId`, `authToken`, and other parameters required for the various API requests.

-----

## Running the Stress Test

The `run_test.sh` script is used to execute the JMeter stress test. It offers several command-line options to control the test parameters:

  * `--threads` or `-t`: The number of concurrent users (threads). **Default: 10.**
  * `--rampup` or `-r`: The time in seconds to ramp up to the full number of threads. **Default: 1.**
  * `--duration` or `-d`: The total duration of the test in seconds. **Default: 10.**
  * `--file` or `-f`: The path to the JMeter test plan file. **Default: "test\_plan.jmx".**
  * `--output` or `-o`: The name of the output file for the test results. **Default: a timestamped `.jtl` file.**

**Example Commands:**

  * To run a quick test with 10 users for 1 minute:

    ```bash
    ./run_test.sh -t 10 -d 60
    ```

  * To run a longer test with 50 users, a 30-second ramp-up time, and a 10-minute duration:

    ```bash
    ./run_test.sh -t 50 -r 30 -d 600
    ```

-----

## Customization and Extension

### How to Add/Modify Environments

To add a new environment, open `generate_exhaustive_data.py` and modify the `get_host_details` function. Add a new `elif` condition for your environment and return the corresponding base URL.

**Example:**

```python
def get_host_details():
    # ... existing code ...
    elif env == "new_env":
        return "https://your-new-env.fourkites.com"
    # ... existing code ...
```

### How to Add a New Tenant

1.  Open `generate_exhaustive_data.py`.
2.  Add a new entry to the `TENANTS_AUTH_TOKEN` dictionary with the tenant name and a valid bearer token.
3.  Run the `generate_exhaustive_data.py` script again to include the new tenant's data in the test file.

### How to Add a New API Endpoint to the Test

1.  **Payload Generation:**

      * Open `generate_exhaustive_data.py`.
      * Add the new API endpoint to the appropriate list (`simple_endpoints`, `carrier_endpoints`, etc.) based on its required parameters.
      * If the new API requires a unique combination of parameters, create a new `itertools.product` loop to generate the corresponding test data rows.

2.  **JMeter Test Plan:**

      * Open the `test_plan.jmx` file in JMeter.
      * Under the "Random API Selector", add a new `HTTPSamplerProxy` for the new API endpoint.
      * Configure the sampler with the correct path, method, and request body, using variables from the CSV file (e.g., `${facilityId}`).

-----

## Viewing Reports

Upon successful completion of a test run, the `run_test.sh` script automatically generates a detailed HTML dashboard from the `.jtl` results file.

The report will be created in a new directory with a name like `report_YYYYMMDD_HHMMSS`. To view the report, open the `index.html` file in that directory in your web browser. This dashboard will provide comprehensive metrics on the performance of the tested APIs.