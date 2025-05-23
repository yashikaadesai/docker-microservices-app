import hashlib
import hmac
import base64
import json
import os


SECRET_KEY_FILE = "key.txt"

def get_secret_key():
    """Reads the secret key from key.txt."""
    with open(SECRET_KEY_FILE, "r") as f:
        return f.readline()

SECRET_KEY = get_secret_key()


def hash_password(password, salt):
    """Hashes the password using SHA-256 with the provided salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_jwt(username):
    """Generates a JWT for authentication."""

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"username": username}
    
    # Encode header and payload to base64
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode()
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), f"{header_encoded}.{payload_encoded}".encode(), hashlib.sha256).hexdigest()
    return f"{header_encoded}.{payload_encoded}.{signature}"


def verify_token(token):

    try:
        header_encoded, payload_encoded, signature = token.split('.')
        with open('key.txt', 'r') as f:
            key = f.read().strip()
        
        message = f"{header_encoded}.{payload_encoded}"
        expected_signature = hmac.new(
            key.encode(), 
            message.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_signature:
            return None
        
        padding = '=' * (4 - len(payload_encoded) % 4)
        payload_json = base64.urlsafe_b64decode((payload_encoded + padding).encode()).decode()
        payload = json.loads(payload_json)
        
        username = payload.get("username")
        
        return username
        
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
    
    
    