#!/usr/bin/env python3
"""
Bearer Token Generator for YMS Dashboard Service
Generates authentication tokens for stress testing by handling the SAML-based login flow.
"""

import requests
import re
import sys
import uuid
import secrets
from typing import Optional, Dict
import json


class BearerTokenGenerator:
    """Handles bearer token generation for YMS authentication."""
    
    # Environment URLs
    ENVIRONMENTS = {
        "local": "http://api-proxy:8000",
        "dev": "https://dy-dev.fourkites.com",
        "qat": "https://dy-qat.fourkites.com",
        "stress": "https://dy-stress.fourkites.com",
        "staging": "https://dy-staging.fourkites.com",
        "prod": "https://dy.fourkites.com"
    }
    
    def __init__(self, environment: str = "stress"):
        """
        Initialize the token generator with the specified environment.
        
        Args:
            environment: Target environment (local, dev, qat, stress, staging, prod)
        """
        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {environment}. Must be one of {list(self.ENVIRONMENTS.keys())}")
        
        self.base_url = self.ENVIRONMENTS[environment]
        self.session = requests.Session()
        
        # Configure URLs
        self.auth_url = f"{self.base_url}/keycloak/realms/YMS/protocol/openid-connect/auth"
        self.saml_endpoint_url = f"{self.base_url}/keycloak/realms/YMS/broker/fk-saml/endpoint"
        self.token_url = f"{self.base_url}/keycloak/realms/YMS/protocol/openid-connect/token"
        self.login_url = f"{self.base_url}/idp/login"
        
        # Configure headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.base_url.rstrip('/'),
            "Connection": "keep-alive",
            "Referer": f"{self.base_url}/idp/login/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        
    def get_bearer_token(self, username: str, password: str, debug: bool = False) -> Optional[str]:
        """
        Generate a bearer token for the given credentials.
        
        Args:
            username: User email address
            password: User password
            
        Returns:
            Bearer token string if successful, None otherwise
        """
        try:
            # Step 1: Get the login form
            print(f"Step 1: Fetching login form...")
            response = self.session.get(self.login_url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch login form. Status: {response.status_code}")
                return None
            
            # Step 2: Get the Keycloak auth URL
            print(f"Step 2: Initializing Keycloak authentication...")
            auth_params = {
                "client_id": "ymsui",
                "redirect_uri": self.base_url.rstrip('/'),
                "state": "9782f5be-c72a-49ff-b023-463b6ee1ab27",
                "response_mode": "fragment",
                "response_type": "code",
                "scope": "openid",
                "nonce": "2e0833d1-05d2-4d5c-82cd-02f9f0a74f77"
            }
            auth_response = self.session.get(self.auth_url, params=auth_params, headers=self.headers)
            if auth_response.status_code != 200:
                print(f"Failed to initialize Keycloak auth. Status: {auth_response.status_code}")
                return None
            
            # Step 3: Login with credentials
            print(f"Step 3: Logging in with credentials...")
            login_data = {
                "username": username,
                "password": password,
                "login": "Sign In",
                "credentialId": ""
            }
            login_response = self.session.post(
                self.login_url,
                data=login_data,
                headers=self.headers,
                allow_redirects=True  # Allow redirects for staging
            )
            
            if login_response.status_code not in [200, 201]:
                print(f"Failed to login. Status: {login_response.status_code}")
                if login_response.status_code in [302, 303, 307, 308]:
                    # Try following redirect manually
                    if 'Location' in login_response.headers:
                        redirect_url = login_response.headers['Location']
                        if not redirect_url.startswith('http'):
                            redirect_url = f"{self.base_url}{redirect_url}"
                        login_response = self.session.get(redirect_url, headers=self.headers)
                
                if login_response.status_code not in [200, 201]:
                    print(f"Still failed after redirect. Status: {login_response.status_code}")
                    return None
            
            # Extract cookies from JavaScript if present
            if 'document.cookie' in login_response.text:
                cookie_matches = re.findall(r'document\.cookie\s*=\s*"([^"]+)"', login_response.text)
                for cookie_str in cookie_matches:
                    key_value = cookie_str.split('=', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        value = value.split(';')[0]
                        if key.startswith('tfonboarding-'):
                            self.session.cookies.set(key, value, domain='.fourkites.com')
            
            # Step 4: Extract SAML data
            print(f"Step 4: Processing SAML response...")
            relay_state_match = re.search(r'name="RelayState"\s+value="([^"]+)"', login_response.text)
            saml_response_match = re.search(r'name="SAMLResponse"\s+value="([^"]+)"', login_response.text)
            
            if not relay_state_match or not saml_response_match:
                print("Failed to extract SAML data from login response")
                return None
            
            relay_state = relay_state_match.group(1)
            saml_response = saml_response_match.group(1)
            
            # Step 5: Submit SAML response
            print(f"Step 5: Submitting SAML response...")
            saml_data = {
                "RelayState": relay_state,
                "SAMLResponse": saml_response
            }
            saml_result = self.session.post(
                self.saml_endpoint_url,
                data=saml_data,
                headers=self.headers,
                allow_redirects=False
            )
            
            if saml_result.status_code not in [200, 302, 303]:
                print(f"Failed to process SAML response. Status: {saml_result.status_code}")
                return None
            
            # Step 6: Extract authorization code from redirect
            location_header = saml_result.headers.get('Location', '')
            if not location_header:
                # Try to find it in the response body
                location_match = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', saml_result.text)
                if location_match:
                    location_header = location_match.group(1)
            
            if not location_header:
                print("Failed to get redirect location from SAML response")
                return None
            
            # Extract code from the URL fragment
            code_match = re.search(r'[#&]code=([^&]+)', location_header)
            if not code_match:
                print("Failed to extract authorization code from redirect URL")
                return None
            
            code = code_match.group(1).strip()
            
            # Step 7: Exchange code for token
            print(f"Step 6: Exchanging authorization code for token...")
            token_data = {
                "code": code,
                "grant_type": "authorization_code",
                "client_id": "ymsui",
                "redirect_uri": self.base_url.rstrip('/')
            }
            token_response = self.session.post(
                self.token_url,
                data=token_data,
                headers=self.headers
            )
            
            if token_response.status_code != 200:
                print(f"Failed to get token. Status: {token_response.status_code}")
                print(f"Response: {token_response.text}")
                return None
            
            # Extract access token
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            
            if debug and access_token:
                print("\n" + "=" * 60)
                print("DEBUG: Token Response Analysis")
                print("=" * 60)
                
                # Decode the JWT to check tenant assignment
                import base64
                parts = access_token.split('.')
                if len(parts) == 3:
                    try:
                        payload_encoded = parts[1]
                        payload_padding = payload_encoded + '=' * (4 - len(payload_encoded) % 4)
                        payload = json.loads(base64.urlsafe_b64decode(payload_padding))
                        
                        print(f"Tenant ID in token: {payload.get('tenant_id', 'NOT FOUND')}")
                        print(f"User: {payload.get('preferred_username', 'N/A')}")
                        print(f"Subject ID: {payload.get('sub', 'N/A')}")
                        print(f"Client: {payload.get('azp', 'N/A')}")
                        
                        # Check if tenant was in any response headers
                        print("\nResponse Headers:")
                        for key, value in token_response.headers.items():
                            if 'tenant' in key.lower():
                                print(f"  {key}: {value}")
                    except Exception as e:
                        print(f"Failed to decode token for debug: {e}")
            
            if access_token:
                print("Successfully obtained bearer token!")
                return access_token
            else:
                print("No access token found in response")
                return None
                
        except Exception as e:
            print(f"Error generating token: {str(e)}")
            return None
    
    def generate_and_save_tokens(self, credentials: Dict[str, Dict[str, str]], output_file: str = "bearer_tokens.json"):
        """
        Generate tokens for multiple users and save to file.
        
        Args:
            credentials: Dictionary mapping role names to {username, password}
            output_file: Path to save the tokens JSON file
            
        Returns:
            Dictionary of role -> token mappings
        """
        tokens = {}
        
        for role, creds in credentials.items():
            print(f"\nGenerating token for role: {role}")
            token = self.get_bearer_token(creds['username'], creds['password'])
            
            if token:
                tokens[role] = f"Bearer {token}"
                print(f"✓ Token generated successfully for {role}")
            else:
                tokens[role] = None
                print(f"✗ Failed to generate token for {role}")
        
        # Save tokens to file
        with open(output_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"\nTokens saved to: {output_file}")
        return tokens


def main():
    """
    Main function for command-line usage.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate bearer tokens for YMS Dashboard Service')
    parser.add_argument('environment', choices=['local', 'dev', 'qat', 'stress', 'staging', 'prod'],
                        help='Target environment')
    parser.add_argument('username', help='User email address')
    parser.add_argument('password', help='User password')
    parser.add_argument('--output', '-o', help='Output file for token (optional)')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = BearerTokenGenerator(args.environment)
    
    # Generate token
    token = generator.get_bearer_token(args.username, args.password)
    
    if token:
        bearer_token = f"Bearer {token}"
        print(f"\n{'='*60}")
        print(f"Bearer Token Generated Successfully!")
        print(f"{'='*60}")
        print(f"Environment: {args.environment}")
        print(f"User: {args.username}")
        print(f"{'='*60}")
        print(f"Token:\n{bearer_token}")
        print(f"{'='*60}")
        
        # Save to file if specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({"token": bearer_token, "environment": args.environment, "user": args.username}, f, indent=2)
            print(f"\nToken saved to: {args.output}")
        
        return 0
    else:
        print(f"\nFailed to generate token for {args.username} in {args.environment} environment")
        return 1


if __name__ == "__main__":
    sys.exit(main())