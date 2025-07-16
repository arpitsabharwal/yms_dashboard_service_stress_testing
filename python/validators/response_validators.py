import json
from typing import Dict, Any, List, Tuple
from datetime import datetime

class ResponseValidator:
    """Validates API responses"""
    
    def __init__(self):
        self.validation_results = []
    
    def validate_response(self, 
                         endpoint: str,
                         response_code: int,
                         response_body: str,
                         response_time: float) -> Tuple[bool, Dict[str, Any]]:
        """Validate complete response"""
        
        results = {
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "response_code": response_code,
            "response_time": response_time,
            "validations": {}
        }
        
        # Status code validation
        status_valid = self.validate_status_code(response_code)
        results["validations"]["status_code"] = {
            "valid": status_valid,
            "expected": 200,
            "actual": response_code
        }
        
        # Response time validation (SLA: 2 seconds)
        time_valid = self.validate_response_time(response_time, sla=2000)
        results["validations"]["response_time"] = {
            "valid": time_valid,
            "sla_ms": 2000,
            "actual_ms": response_time
        }
        
        # Response body validation
        if response_body:
            body_valid, body_errors = self.validate_response_body(endpoint, response_body)
            results["validations"]["response_body"] = {
                "valid": body_valid,
                "errors": body_errors
            }
        else:
            body_valid = False
            results["validations"]["response_body"] = {
                "valid": False,
                "errors": ["Empty response body"]
            }
        
        # Overall validation
        overall_valid = status_valid and time_valid and body_valid
        results["overall_valid"] = overall_valid
        
        return overall_valid, results
    
    def validate_status_code(self, status_code: int) -> bool:
        """Validate HTTP status code"""
        return status_code == 200
    
    def validate_response_time(self, response_time: float, sla: float) -> bool:
        """Validate response time against SLA"""
        return response_time <= sla
    
    def validate_response_body(self, endpoint: str, response_body: str) -> Tuple[bool, List[str]]:
        """Validate response body structure"""
        errors = []
        
        try:
            data = json.loads(response_body)
        except json.JSONDecodeError:
            return False, ["Invalid JSON response"]
        
        # Endpoint-specific validations
        if endpoint == "yard-availability":
            errors.extend(self._validate_yard_availability(data))
        elif endpoint == "trailer-overview":
            errors.extend(self._validate_trailer_overview(data))
        # Add more endpoint-specific validations...
        
        return len(errors) == 0, errors
    
    def _validate_yard_availability(self, data: Dict[str, Any]) -> List[str]:
        """Validate yard availability response"""
        errors = []
        
        if "docks" not in data:
            errors.append("Missing 'docks' field")
        if "parkingSpots" not in data:
            errors.append("Missing 'parkingSpots' field")
        
        for field in ["docks", "parkingSpots"]:
            if field in data:
                errors.extend(self._validate_availability_metrics(data[field], field))
        
        return errors
    
    def _validate_trailer_overview(self, data: Dict[str, Any]) -> List[str]:
        """Validate trailer overview response"""
        errors = []
        
        if "totalTrailersCount" not in data:
            errors.append("Missing 'totalTrailersCount' field")
        elif not isinstance(data["totalTrailersCount"], int) or data["totalTrailersCount"] < 0:
            errors.append("Invalid 'totalTrailersCount' value")
        
        if "trailerOverviewMetrics" not in data:
            errors.append("Missing 'trailerOverviewMetrics' field")
        else:
            metrics = data["trailerOverviewMetrics"]
            required_fields = ["loadedInbound", "loadedOutbound", "empty", "partial"]
            for field in required_fields:
                if field not in metrics:
                    errors.append(f"Missing '{field}' in trailerOverviewMetrics")
        
        return errors
    
    def _validate_availability_metrics(self, metrics: Dict[str, Any], metric_name: str) -> List[str]:
        """Validate availability metrics structure"""
        errors = []
        
        if "total" not in metrics:
            errors.append(f"Missing 'total' in {metric_name}")
        
        for status in ["active", "inactive"]:
            if status not in metrics:
                errors.append(f"Missing '{status}' in {metric_name}")
            elif not self._validate_percentage_breakdown(metrics[status]):
                errors.append(f"Invalid percentage breakdown for {status} in {metric_name}")
        
        return errors
    
    def _validate_percentage_breakdown(self, breakdown: Dict[str, Any]) -> bool:
        """Validate percentage breakdown structure"""
        if not isinstance(breakdown, dict):
            return False
        
        required_fields = ["count", "percentage"]
        for field in required_fields:
            if field not in breakdown:
                return False
            if not isinstance(breakdown[field], int) or breakdown[field] < 0:
                return False
        
        return breakdown["percentage"] <= 100
