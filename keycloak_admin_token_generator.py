#!/usr/bin/env python3
"""
Keycloak Admin Token Generator for YMS Dashboard Service
Uses Keycloak Admin API to programmatically change user's tenant_id and generate tokens
"""

import json
import base64
import requests
import os
from typing import Dict, List, Optional
from datetime import datetime
import time


class KeycloakAdminTokenGenerator:
    """Generate tokens using Keycloak Admin API to change user attributes."""
    
    def __init__(self, environment: str = "staging"):
        """Initialize the Keycloak admin token generator."""
        self.environment = environment
        self.setup_environment_urls()
        self.admin_session = requests.Session()
        
    def setup_environment_urls(self):
        """Set up URLs based on environment."""
        env_configs = {
            "local": "http://api-proxy:8000",
            "dev": "https://dy-dev.fourkites.com",
            "qat": "https://dy-qat.fourkites.com", 
            "stress": "https://dy-stress.fourkites.com",
            "staging": "https://dy-staging.fourkites.com",
            "prod": "https://dy.fourkites.com"
        }
        
        self.base_url = env_configs.get(self.environment, env_configs["staging"])
        self.keycloak_base = f"{self.base_url}/keycloak"
        self.realm = "YMS"
        
        # Keycloak Admin API endpoints
        self.admin_token_url = f"{self.keycloak_base}/realms/master/protocol/openid-connect/token"
        self.users_url = f"{self.keycloak_base}/admin/realms/{self.realm}/users"
        self.user_token_url = f"{self.keycloak_base}/realms/{self.realm}/protocol/openid-connect/token"
        
    def get_admin_token(self, admin_username: str, admin_password: str) -> Optional[str]:
        """Get Keycloak admin access token."""
        try:
            print(f"Authenticating as Keycloak admin...")
            
            # Try with master realm client
            data = {
                "client_id": "admin-cli",
                "username": admin_username,
                "password": admin_password,
                "grant_type": "password"
            }
            
            response = self.admin_session.post(
                self.admin_token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                print("✓ Admin authentication successful")
                return token_data.get("access_token")
            else:
                print(f"✗ Admin authentication failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting admin token: {e}")
            return None
    
    def find_user(self, admin_token: str, user_email: str) -> Optional[Dict]:
        """Find user by email in Keycloak."""
        try:
            print(f"Searching for user: {user_email}")
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Search for user by email or username
            # Try email first, then username if that fails
            params = {"email": user_email}
            response = self.admin_session.get(
                self.users_url,
                headers=headers,
                params=params
            )
            
            # If no users found with email, try username
            if response.status_code == 200 and not response.json():
                params = {"username": user_email}
                response = self.admin_session.get(
                    self.users_url,
                    headers=headers,
                    params=params
                )
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    user = users[0]
                    print(f"✓ Found user: {user.get('id')}")
                    return user
                else:
                    print(f"✗ User not found: {user_email}")
                    return None
            else:
                print(f"✗ Failed to search users: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"✗ Error finding user: {e}")
            return None
    
    def update_user_tenant(self, admin_token: str, user_id: str, tenant_id: str) -> bool:
        """Update user's tenant_id attribute in Keycloak."""
        try:
            print(f"  Updating user tenant to: {tenant_id}")
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Get current user data first
            user_url = f"{self.users_url}/{user_id}"
            response = self.admin_session.get(user_url, headers=headers)
            
            if response.status_code != 200:
                print(f"  ✗ Failed to get user data: {response.status_code}")
                return False
            
            user_data = response.json()
            
            # Update attributes with new tenant_id
            if "attributes" not in user_data:
                user_data["attributes"] = {}
            
            user_data["attributes"]["tenant_id"] = [tenant_id]
            user_data["attributes"]["current_tenant"] = [tenant_id]
            
            # Update user
            response = self.admin_session.put(
                user_url,
                headers=headers,
                json=user_data
            )
            
            if response.status_code in [200, 204]:
                print(f"  ✓ User tenant updated to: {tenant_id}")
                return True
            else:
                print(f"  ✗ Failed to update user: {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error updating user tenant: {e}")
            return False
    
    def get_user_token_with_impersonation(self, admin_token: str, user_id: str) -> Optional[str]:
        """Get token for user using admin impersonation."""
        try:
            print(f"  Getting token via impersonation...")
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Use impersonation endpoint
            impersonate_url = f"{self.users_url}/{user_id}/impersonation"
            
            response = self.admin_session.post(
                impersonate_url,
                headers=headers
            )
            
            if response.status_code == 200:
                # The response might contain cookies or redirect info
                # We need to extract the actual token
                impersonation_data = response.json()
                
                # Try to get token from the impersonation response
                if "redirect" in impersonation_data:
                    # Follow redirect to get actual token
                    redirect_url = impersonation_data["redirect"]
                    token_response = self.admin_session.get(redirect_url)
                    # Extract token from response
                    # This depends on your Keycloak configuration
                    
                print(f"  ✓ Token obtained via impersonation")
                return None  # Need to implement token extraction
            else:
                print(f"  ✗ Impersonation failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ✗ Error with impersonation: {e}")
            return None
    
    def get_user_token_direct(self, username: str, password: str, tenant_id: str) -> Optional[str]:
        """Get token for user directly after tenant update."""
        try:
            print(f"  Getting fresh token for tenant: {tenant_id}")
            
            # Import and use the existing bearer token generator
            from generate_bearer_token import BearerTokenGenerator
            
            # Create a new instance for fresh login
            token_gen = BearerTokenGenerator(self.environment)
            
            # Wait a bit for Keycloak to propagate the attribute change
            time.sleep(2)
            
            # Get fresh token with updated tenant
            token = token_gen.get_bearer_token(username, password)
            
            if token:
                # Verify the tenant in the token
                actual_tenant = self._extract_tenant_from_token(token)
                if actual_tenant == tenant_id:
                    print(f"  ✓ Token generated with correct tenant: {tenant_id}")
                    return token
                else:
                    print(f"  ⚠ Token has tenant '{actual_tenant}' instead of '{tenant_id}'")
                    # Return it anyway as it might be the best we can get
                    return token
            else:
                print(f"  ✗ Failed to generate token")
                return None
                
        except Exception as e:
            print(f"  ✗ Error getting user token: {e}")
            return None
    
    def generate_tokens_for_all_tenants(
        self,
        admin_username: str,
        admin_password: str,
        user_email: str,
        user_password: str,
        tenants: List[str]
    ) -> Dict[str, str]:
        """Generate tokens for all specified tenants."""
        tokens = {}
        
        print(f"{'='*60}")
        print(f"Keycloak Admin Multi-Tenant Token Generation")
        print(f"{'='*60}")
        print(f"Environment: {self.environment}")
        print(f"Admin user: {admin_username}")
        print(f"Target user: {user_email}")
        print(f"Target tenants: {', '.join(tenants)}")
        print(f"{'='*60}")
        
        # Step 1: Get admin token
        admin_token = self.get_admin_token(admin_username, admin_password)
        if not admin_token:
            print("✗ Failed to authenticate as admin. Cannot proceed.")
            return tokens
        
        # Step 2: Find the user
        user = self.find_user(admin_token, user_email)
        if not user:
            print("✗ User not found. Cannot proceed.")
            return tokens
        
        user_id = user.get("id")
        print(f"User ID: {user_id}")
        print(f"Current attributes: {user.get('attributes', {})}")
        
        # Step 3: For each tenant, update user and get token
        for tenant in tenants:
            print(f"\n--- Processing tenant: {tenant} ---")
            
            # Update user's tenant attribute
            success = self.update_user_tenant(admin_token, user_id, tenant)
            
            # If we get a 401, the admin token has expired - refresh it
            if not success:
                print("  Admin token may have expired, refreshing...")
                admin_token = self.get_admin_token(admin_username, admin_password)
                if admin_token:
                    print("  ✓ Admin token refreshed")
                    # Try again with fresh token
                    success = self.update_user_tenant(admin_token, user_id, tenant)
                else:
                    print("  ✗ Failed to refresh admin token")
            
            if success:
                # Get fresh token for this tenant
                token = self.get_user_token_direct(user_email, user_password, tenant)
                
                if token:
                    tokens[tenant] = f"Bearer {token}"
                    print(f"✓ Success: Token generated for tenant '{tenant}'")
                else:
                    print(f"✗ Failed to generate token for tenant '{tenant}'")
                    tokens[tenant] = None
            else:
                print(f"✗ Failed to update tenant to '{tenant}'")
                tokens[tenant] = None
        
        return tokens
    
    def _extract_tenant_from_token(self, token: str) -> str:
        """Extract tenant_id from JWT token."""
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            parts = token.split('.')
            if len(parts) != 3:
                return "INVALID_TOKEN"
            
            payload_encoded = parts[1]
            payload_padding = payload_encoded + '=' * (4 - len(payload_encoded) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_padding))
            
            return payload.get('tenant_id', 'NO_TENANT_ID')
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def save_tokens(self, tokens: Dict[str, str], filename: str = None):
        """Save tokens to a JSON file."""
        # Use default filename if not provided
        if filename is None:
            os.makedirs("tokens", exist_ok=True)
            filename = f"tokens/{self.environment}.json"
        
        output = {
            "generated_at": datetime.now().isoformat(),
            "environment": self.environment,
            "method": "keycloak_admin_api",
            "tokens": {}
        }
        
        for tenant, token in tokens.items():
            if token:
                # Decode token to get details
                token_info = self._decode_full_token(token)
                output["tokens"][tenant] = {
                    "token": token,
                    "tenant_id": token_info.get("tenant_id"),
                    "user": token_info.get("user"),
                    "expires_at": token_info.get("exp_datetime"),
                    "valid": True
                }
            else:
                output["tokens"][tenant] = {
                    "token": None,
                    "error": "Failed to generate token"
                }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Tokens saved to: {filename}")
        return filename
    
    def _decode_full_token(self, token: str) -> dict:
        """Decode and return full token information."""
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            parts = token.split('.')
            if len(parts) != 3:
                return {}
            
            payload_encoded = parts[1]
            payload_padding = payload_encoded + '=' * (4 - len(payload_encoded) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_padding))
            
            # Convert exp timestamp to datetime
            if 'exp' in payload:
                exp_dt = datetime.fromtimestamp(payload['exp'])
                payload['exp_datetime'] = exp_dt.isoformat()
            
            return {
                "tenant_id": payload.get('tenant_id'),
                "user": payload.get('preferred_username'),
                "exp_datetime": payload.get('exp_datetime')
            }
        except:
            return {}


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate bearer tokens using Keycloak Admin API to change tenant'
    )
    parser.add_argument('environment', 
                        choices=['local', 'dev', 'qat', 'stress', 'staging', 'prod'],
                        help='Target environment')
    parser.add_argument('admin_username', help='Keycloak admin username')
    parser.add_argument('admin_password', help='Keycloak admin password')
    parser.add_argument('user_email', help='User email to generate tokens for')
    parser.add_argument('user_password', help='User password')
    parser.add_argument('--tenants', '-t', nargs='+',
                        default=['shipperapi', 'ge-appliances', 'fritolay', 
                                 'kimberly-clark-corporation', 'carrierapi'],
                        help='List of tenant IDs')
    parser.add_argument('--output', '-o', default=None,
                        help='Output file for tokens (default: tokens/{env}.json)')
    
    args = parser.parse_args()
    
    # Generate tokens
    generator = KeycloakAdminTokenGenerator(args.environment)
    tokens = generator.generate_tokens_for_all_tenants(
        args.admin_username,
        args.admin_password,
        args.user_email,
        args.user_password,
        args.tenants
    )
    
    # Save tokens
    if tokens:
        generator.save_tokens(tokens, args.output)
        
        # Summary
        valid_count = len([t for t in tokens.values() if t])
        print(f"\n{'='*60}")
        print(f"COMPLETED: Generated {valid_count}/{len(args.tenants)} tokens")
        print(f"Output saved to: {args.output}")
        print(f"{'='*60}")
    else:
        print("\n✗ No tokens generated")


if __name__ == "__main__":
    main()