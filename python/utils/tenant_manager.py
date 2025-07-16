import yaml
from typing import Dict, Any, List
import os

class TenantManager:
    """Manages tenant configurations and data"""
    
    def __init__(self, config_path: str = "config/tenant_config.yaml"):
        self.config_path = config_path
        self.tenants = self._load_tenant_config()
    
    def _load_tenant_config(self) -> Dict[str, Any]:
        """Load tenant configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('tenants', {})
    
    def get_tenant_config(self, tenant_name: str) -> Dict[str, Any]:
        """Get configuration for specific tenant"""
        if tenant_name not in self.tenants:
            raise ValueError(f"Tenant '{tenant_name}' not found in configuration")
        return self.tenants[tenant_name]
    
    def get_all_tenants(self) -> List[str]:
        """Get list of all configured tenants"""
        return list(self.tenants.keys())
    
    def get_tenant_rpm_config(self, tenant_name: str) -> Dict[str, int]:
        """Get RPM configuration for tenant"""
        tenant_config = self.get_tenant_config(tenant_name)
        return tenant_config.get('rpm_config', {})
    
    def get_tenant_auth_token(self, tenant_name: str) -> str:
        """Get authentication token for tenant"""
        tenant_config = self.get_tenant_config(tenant_name)
        return tenant_config.get('auth', {}).get('token', '')
