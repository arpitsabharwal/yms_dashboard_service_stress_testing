#!/usr/bin/env python3
"""
Configuration loader for environment-specific settings.
Loads credentials and settings from config/{env}.env files.
"""

import os
from typing import Dict, List, Optional
from pathlib import Path


class ConfigLoader:
    """Load environment-specific configuration from .env files."""
    
    def __init__(self, environment: str):
        """Initialize configuration loader for specific environment."""
        self.environment = environment.lower()
        self.config = {}
        self.config_file = Path(__file__).parent / "config" / f"{self.environment}.env"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from .env file."""
        if not self.config_file.exists():
            print(f"Warning: Configuration file not found: {self.config_file}")
            return
        
        with open(self.config_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    self.config[key.strip()] = value.strip()
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_base_url(self) -> str:
        """Get base URL for the environment."""
        return self.config.get("BASE_URL", "")
    
    def get_keycloak_admin(self) -> str:
        """Get Keycloak admin username."""
        return self.config.get("KEYCLOAK_ADMIN", "")
    
    def get_keycloak_password(self) -> str:
        """Get Keycloak admin password."""
        return self.config.get("KEYCLOAK_PASSWORD", "")
    
    def get_user_email(self) -> str:
        """Get test user email."""
        return self.config.get("USER_EMAIL", "")
    
    def get_user_password(self) -> str:
        """Get test user password."""
        return self.config.get("USER_PASSWORD", "")
    
    def get_tenants(self) -> List[str]:
        """Get list of tenants to test."""
        tenants_str = self.config.get("TENANTS", "")
        if not tenants_str:
            return []
        return [t.strip() for t in tenants_str.split(',')]
    
    def is_configured(self) -> bool:
        """Check if environment is properly configured."""
        required = ["BASE_URL", "KEYCLOAK_ADMIN", "KEYCLOAK_PASSWORD", 
                   "USER_EMAIL", "USER_PASSWORD", "TENANTS"]
        return all(self.config.get(key) for key in required)
    
    def print_config(self, hide_passwords: bool = True):
        """Print current configuration (with optional password hiding)."""
        print(f"\nConfiguration for {self.environment} environment:")
        print(f"Config file: {self.config_file}")
        print("-" * 50)
        
        for key, value in self.config.items():
            if hide_passwords and "PASSWORD" in key and value:
                value = "*" * 8
            print(f"{key}: {value}")
        
        if not self.is_configured():
            print("\n⚠ Warning: Some required configuration values are missing!")
            print("Please update the config file with appropriate values.")


def get_env_config(environment: str) -> Dict[str, any]:
    """
    Get environment configuration as a dictionary.
    Compatible with the existing ENV_CONFIG structure.
    """
    loader = ConfigLoader(environment)
    
    return {
        "base_url": loader.get_base_url(),
        "keycloak_admin": loader.get_keycloak_admin(),
        "keycloak_password": loader.get_keycloak_password(),
        "user_email": loader.get_user_email(),
        "user_password": loader.get_user_password(),
        "tenants": loader.get_tenants()
    }


def list_environments() -> List[str]:
    """List all available environment configurations."""
    config_dir = Path(__file__).parent / "config"
    if not config_dir.exists():
        return []
    
    env_files = config_dir.glob("*.env")
    return [f.stem for f in env_files]


if __name__ == "__main__":
    """Test configuration loading."""
    import sys
    
    if len(sys.argv) > 1:
        env = sys.argv[1]
        loader = ConfigLoader(env)
        loader.print_config()
        
        if loader.is_configured():
            print(f"\n✓ Environment {env} is properly configured")
        else:
            print(f"\n✗ Environment {env} needs configuration updates")
    else:
        print("Available environments:")
        for env in list_environments():
            print(f"  - {env}")
        print("\nUsage: python config_loader.py <environment>")