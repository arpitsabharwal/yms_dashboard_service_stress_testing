from .base_generator import BaseGenerator
from typing import Dict, Any
import random

class FacilityRequestGenerator(BaseGenerator):
    """Generator for FacilityRequestPayloadDTO"""
    
    def generate(self) -> Dict[str, Any]:
        return {
            "facilityId": self.get_random_facility_id()
        }

class TrailerOverviewRequestGenerator(BaseGenerator):
    """Generator for TrailerOverviewRequestPayloadDTO"""
    
    TRAILER_STATES = ["all", "noFlags", "audit", "damaged", "outOfService"]
    
    def generate(self) -> Dict[str, Any]:
        return {
            "facilityId": self.get_random_facility_id(),
            "carrierIds": self.get_random_carrier_ids(),
            "trailerState": random.choice(self.TRAILER_STATES)
        }

class TrailerExceptionsRequestGenerator(BaseGenerator):
    """Generator for TrailerExceptionsRequestPayloadDTO"""
    
    def generate(self) -> Dict[str, Any]:
        return {
            "facilityId": self.get_random_facility_id(),
            "carrierIds": self.get_random_carrier_ids(),
            "lastDetectionTimeThresholdHours": random.randint(1, 24),
            "inboundLoadedThresholdHours": random.randint(4, 48)
        }

class FacilityCarrierRequestGenerator(BaseGenerator):
    """Generator for FacilityCarrierRequestPayloadDTO"""
    
    def generate(self) -> Dict[str, Any]:
        return {
            "facilityId": self.get_random_facility_id(),
            "carrierIds": self.get_random_carrier_ids()
        }

class ShipmentVolumeForecastRequestGenerator(BaseGenerator):
    """Generator for ShipmentVolumeForecastRequestPayloadDTO"""
    
    SHIPMENT_DIRECTIONS = ["Inbound", "Outbound"]
    
    def generate(self) -> Dict[str, Any]:
        return {
            "facilityId": self.get_random_facility_id(),
            "carrierIds": self.get_random_carrier_ids(),
            "shipmentDirection": random.choice(self.SHIPMENT_DIRECTIONS)
        }

class SavedFilterTrailerCountRequestGenerator(BaseGenerator):
    """Generator for SavedFilterTrailerCountRequestPayloadDTO"""
    
    def generate(self) -> Dict[str, Any]:
        user_ids = self.data_pool.get('user_ids', [3001, 3002, 3003])
        saved_filter_ids = self.data_pool.get('saved_filter_ids', [4001, 4002, 4003])
        
        return {
            "facilityId": self.get_random_facility_id(),
            "savedFilterId": random.choice(saved_filter_ids),
            "userId": random.choice(user_ids)
        }

# Generator factory
GENERATORS = {
    "yard-availability": FacilityRequestGenerator,
    "trailer-overview": TrailerOverviewRequestGenerator,
    "trailer-exception-summary": TrailerExceptionsRequestGenerator,
    "task-workload-summary": FacilityRequestGenerator,
    "task-attention-summary": FacilityRequestGenerator,
    "site-occupancy": FacilityCarrierRequestGenerator,
    "shipment-volume-forecast": ShipmentVolumeForecastRequestGenerator,
    "dwell-time-summary": FacilityCarrierRequestGenerator,
    "door-breakdown-summary": FacilityRequestGenerator,
    "detention-summary": FacilityCarrierRequestGenerator,
    "saved-filter-trailer-count": SavedFilterTrailerCountRequestGenerator
}

def get_generator(endpoint: str, tenant_config: Dict[str, Any]) -> BaseGenerator:
    """Factory method to get appropriate generator"""
    generator_class = GENERATORS.get(endpoint)
    if not generator_class:
        raise ValueError(f"No generator found for endpoint: {endpoint}")
    return generator_class(tenant_config)
