import json
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import yaml
from datetime import datetime, timedelta

class BaseGenerator(ABC):
    """Base class for all payload generators"""
    
    def __init__(self, tenant_config: Dict[str, Any]):
        self.tenant_config = tenant_config
        self.tenant_name = tenant_config.get('name')
        self.data_pool = tenant_config.get('data_pool', {})
        
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """Generate payload specific to the endpoint"""
        pass
    
    def get_random_facility_id(self) -> int:
        """Get random facility ID from tenant's pool"""
        facility_ids = self.data_pool.get('facility_ids', [1001, 1002, 1003])
        return random.choice(facility_ids)
    
    def get_random_carrier_ids(self, count: int = None) -> List[int]:
        """Get random carrier IDs from tenant's pool"""
        carrier_ids = self.data_pool.get('carrier_ids', [2001, 2002, 2003, 2004])
        if count is None:
            count = random.randint(1, len(carrier_ids))
        return random.sample(carrier_ids, min(count, len(carrier_ids)))
    
    def to_json(self) -> str:
        """Convert generated payload to JSON string"""
        return json.dumps(self.generate())
