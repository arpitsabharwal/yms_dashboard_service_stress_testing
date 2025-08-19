#!/usr/bin/env python3
"""
Multi-User Token Generator for YMS Dashboard Service
Generates tokens for multiple users across different tenants
"""

import json
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Import existing token generators
from keycloak_admin_token_generator import KeycloakAdminTokenGenerator
from generate_bearer_token import BearerTokenGenerator


class MultiUserTokenGenerator:
    """Generate tokens for multiple users with their respective tenant access"""
    
    def __init__(self, config_file: str = None, environment: str = None):
        """
        Initialize multi-user token generator
        
        Args:
            config_file: Path to multi-user configuration JSON
            environment: Override environment from config
        """
        self.config_file = config_file or "config/multi_user.json"
        self.config = self._load_config()
        self.environment = environment or self.config.get("environment", "staging")
        self.results = {
            "generated_at": datetime.now().isoformat(),
            "environment": self.environment,
            "users": {}
        }
        
    def _load_config(self) -> Dict:
        """Load multi-user configuration from JSON file"""
        if not os.path.exists(self.config_file):
            print(f"Configuration file not found: {self.config_file}")
            print("Please create a configuration file based on config/multi_user_example.json")
            sys.exit(1)
            
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def generate_tokens_for_all_users(self) -> Dict:
        """Generate tokens for all users in the configuration"""
        
        print("=" * 70)
        print("Multi-User Token Generation")
        print("=" * 70)
        print(f"Environment: {self.environment}")
        print(f"Total users: {len(self.config.get('users', []))}")
        print("=" * 70)
        
        # Get admin credentials
        admin_username = self.config.get("keycloak_admin", "admin")
        admin_password = self.config.get("keycloak_password", "")
        
        if not admin_password:
            print("Error: Keycloak admin password not configured")
            return self.results
        
        # Initialize Keycloak admin generator for tenant switching
        keycloak_gen = KeycloakAdminTokenGenerator(self.environment)
        
        # Process each user
        for user_config in self.config.get("users", []):
            user_email = user_config.get("email")
            user_password = user_config.get("password")
            user_tenants = user_config.get("tenants", [])
            description = user_config.get("description", "")
            
            print(f"\n{'─' * 70}")
            print(f"Processing user: {user_email}")
            if description:
                print(f"Description: {description}")
            print(f"Tenants: {', '.join(user_tenants)}")
            print("─" * 70)
            
            # Initialize user result structure
            self.results["users"][user_email] = {
                "description": description,
                "tenants": {},
                "success_count": 0,
                "failure_count": 0
            }
            
            # Generate tokens for each tenant this user has access to
            if user_tenants:
                # Use Keycloak admin API to switch tenants
                user_tokens = self._generate_user_tenant_tokens(
                    keycloak_gen,
                    admin_username,
                    admin_password,
                    user_email,
                    user_password,
                    user_tenants
                )
                
                # Store results
                for tenant, token in user_tokens.items():
                    if token:
                        self.results["users"][user_email]["tenants"][tenant] = {
                            "token": token,
                            "status": "success"
                        }
                        self.results["users"][user_email]["success_count"] += 1
                        print(f"  ✓ {tenant}: Token generated")
                    else:
                        self.results["users"][user_email]["tenants"][tenant] = {
                            "token": None,
                            "status": "failed",
                            "error": "Failed to generate token"
                        }
                        self.results["users"][user_email]["failure_count"] += 1
                        print(f"  ✗ {tenant}: Failed to generate token")
            else:
                # No specific tenants - generate default token
                print("  Generating token with default tenant...")
                token = self._generate_default_token(user_email, user_password)
                
                if token:
                    self.results["users"][user_email]["tenants"]["default"] = {
                        "token": token,
                        "status": "success"
                    }
                    self.results["users"][user_email]["success_count"] = 1
                    print(f"  ✓ Default token generated")
                else:
                    self.results["users"][user_email]["tenants"]["default"] = {
                        "token": None,
                        "status": "failed",
                        "error": "Failed to generate token"
                    }
                    self.results["users"][user_email]["failure_count"] = 1
                    print(f"  ✗ Failed to generate default token")
        
        return self.results
    
    def _generate_user_tenant_tokens(
        self,
        keycloak_gen: KeycloakAdminTokenGenerator,
        admin_username: str,
        admin_password: str,
        user_email: str,
        user_password: str,
        tenants: List[str]
    ) -> Dict[str, str]:
        """Generate tokens for a user across multiple tenants"""
        
        tokens = {}
        
        # Get admin token
        admin_token = keycloak_gen.get_admin_token(admin_username, admin_password)
        if not admin_token:
            print(f"  ✗ Failed to authenticate as admin")
            return tokens
        
        # Find user
        user = keycloak_gen.find_user(admin_token, user_email)
        if not user:
            print(f"  ✗ User not found: {user_email}")
            # Try to generate tokens without tenant switching
            for tenant in tenants:
                token = self._generate_default_token(user_email, user_password)
                if token:
                    tokens[tenant] = token
            return tokens
        
        user_id = user.get("id")
        
        # Generate token for each tenant
        for tenant in tenants:
            # Check if admin token needs refresh (every 10 tenants or on failure)
            if len(tokens) % 10 == 0 and len(tokens) > 0:
                admin_token = keycloak_gen.get_admin_token(admin_username, admin_password)
                if not admin_token:
                    print(f"  ✗ Failed to refresh admin token")
                    break
            
            # Update user tenant
            success = keycloak_gen.update_user_tenant(admin_token, user_id, tenant)
            
            # If failed, try refreshing admin token
            if not success:
                admin_token = keycloak_gen.get_admin_token(admin_username, admin_password)
                if admin_token:
                    success = keycloak_gen.update_user_tenant(admin_token, user_id, tenant)
            
            if success:
                # Generate token for this tenant
                token = keycloak_gen.get_user_token_direct(user_email, user_password, tenant)
                if token:
                    tokens[tenant] = f"Bearer {token}"
                else:
                    tokens[tenant] = None
            else:
                tokens[tenant] = None
        
        return tokens
    
    def _generate_default_token(self, user_email: str, user_password: str) -> Optional[str]:
        """Generate a token without tenant switching"""
        try:
            bearer_gen = BearerTokenGenerator(self.environment)
            token = bearer_gen.get_bearer_token(user_email, user_password)
            if token:
                return f"Bearer {token}"
        except Exception as e:
            print(f"  Error generating default token: {e}")
        return None
    
    def save_results(self, output_file: str = None):
        """Save generated tokens to JSON file"""
        if not output_file:
            # Create output filename based on environment and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tokens/multi_user_{self.environment}_{timestamp}.json"
        
        # Ensure tokens directory exists
        os.makedirs("tokens", exist_ok=True)
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        # Also save a latest version for easy access
        latest_file = f"tokens/multi_user_{self.environment}_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✓ Latest version saved to: {latest_file}")
        
        return output_file
    
    def print_summary(self):
        """Print summary of token generation results"""
        print("\n" + "=" * 70)
        print("Token Generation Summary")
        print("=" * 70)
        
        total_success = 0
        total_failure = 0
        
        for user_email, user_data in self.results["users"].items():
            success = user_data["success_count"]
            failure = user_data["failure_count"]
            total = success + failure
            
            print(f"\n{user_email}:")
            print(f"  Total tenants: {total}")
            print(f"  Successful: {success}")
            print(f"  Failed: {failure}")
            
            if success > 0:
                print(f"  Success rate: {(success/total)*100:.1f}%")
            
            total_success += success
            total_failure += failure
        
        print("\n" + "─" * 70)
        print(f"Overall Results:")
        print(f"  Total tokens attempted: {total_success + total_failure}")
        print(f"  Total successful: {total_success}")
        print(f"  Total failed: {total_failure}")
        
        if total_success + total_failure > 0:
            print(f"  Overall success rate: {(total_success/(total_success + total_failure))*100:.1f}%")
        
        print("=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate tokens for multiple users across different tenants"
    )
    parser.add_argument(
        "--config", "-c",
        default="config/multi_user.json",
        help="Path to multi-user configuration file (default: config/multi_user.json)"
    )
    parser.add_argument(
        "--env", "-e",
        choices=["local", "dev", "qat", "stress", "staging", "prod"],
        help="Override environment from config file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path for tokens"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing tokens without regenerating"
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        print("\nTo get started:")
        print("1. Copy the example configuration:")
        print("   cp config/multi_user_example.json config/multi_user.json")
        print("2. Edit config/multi_user.json with your users and credentials")
        print("3. Run this script again")
        sys.exit(1)
    
    # Initialize generator
    generator = MultiUserTokenGenerator(
        config_file=args.config,
        environment=args.env
    )
    
    # Generate tokens
    print("\nStarting multi-user token generation...")
    generator.generate_tokens_for_all_users()
    
    # Save results
    output_file = generator.save_results(args.output)
    
    # Print summary
    generator.print_summary()
    
    print(f"\n✓ Token generation complete!")
    print(f"Use the generated tokens in your test data or API calls.")


if __name__ == "__main__":
    main()