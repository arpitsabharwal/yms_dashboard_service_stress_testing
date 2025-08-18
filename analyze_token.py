#!/usr/bin/env python3
"""
JWT Token Analyzer - Decodes and displays JWT token contents
"""

import json
import base64
import sys

def decode_jwt(token):
    """Decode a JWT token and display its contents."""
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    # JWT has 3 parts separated by dots: header.payload.signature
    parts = token.split('.')
    
    if len(parts) != 3:
        print("Invalid JWT format. Expected 3 parts separated by dots.")
        return None
    
    header_encoded, payload_encoded, signature = parts
    
    # Decode header
    try:
        # Add padding if needed (JWT uses base64url without padding)
        header_padding = header_encoded + '=' * (4 - len(header_encoded) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_padding))
        print("=" * 60)
        print("JWT HEADER:")
        print("=" * 60)
        print(json.dumps(header, indent=2))
    except Exception as e:
        print(f"Failed to decode header: {e}")
        return None
    
    # Decode payload
    try:
        # Add padding if needed
        payload_padding = payload_encoded + '=' * (4 - len(payload_encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padding))
        print("\n" + "=" * 60)
        print("JWT PAYLOAD:")
        print("=" * 60)
        print(json.dumps(payload, indent=2))
        
        # Highlight tenant information
        if 'tenant_id' in payload:
            print("\n" + "=" * 60)
            print("TENANT INFORMATION:")
            print("=" * 60)
            print(f"Tenant ID: {payload['tenant_id']}")
            print(f"User: {payload.get('preferred_username', 'N/A')}")
            print(f"Email: {payload.get('email', 'N/A')}")
            print(f"Name: {payload.get('name', 'N/A')}")
            print(f"Groups: {', '.join(payload.get('groups', []))}")
        
        # Check token validity
        import time
        if 'exp' in payload:
            exp_time = payload['exp']
            current_time = int(time.time())
            if exp_time > current_time:
                remaining = exp_time - current_time
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                print(f"\nToken valid for: {hours}h {minutes}m")
            else:
                print("\nToken has EXPIRED!")
                
    except Exception as e:
        print(f"Failed to decode payload: {e}")
        return None
    
    return {'header': header, 'payload': payload}

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_token.py <jwt_token>")
        print("       python analyze_token.py 'Bearer eyJhbG...'")
        sys.exit(1)
    
    token = sys.argv[1]
    decode_jwt(token)

if __name__ == "__main__":
    main()