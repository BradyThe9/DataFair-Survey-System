"""
DataFair API Test Script
Teste die wichtigsten API-Endpoints
"""
import requests
import json
from datetime import datetime

# Basis-URL der API
BASE_URL = 'http://localhost:5000/api'

# Farben für Terminal-Output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'


def print_response(response, endpoint):
    """Schöne Ausgabe der API-Response"""
    print(f"\n{Colors.BLUE}=== {endpoint} ==={Colors.END}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"{Colors.GREEN}✓ Erfolg{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Fehler{Colors.END}")
    
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health():
    """Test Health Check Endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200


def test_register():
    """Test User Registration"""
    test_user = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "birth_date": "1990-01-01",
        "country": "DE"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        return response.json()
    return None


def test_login(email, password):
    """Test User Login"""
    credentials = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        return response.json()
    return None


def test_protected_endpoint(access_token):
    """Test geschützten Endpoint"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response(response, "Protected Endpoint (Get Current User)")
    return response.status_code == 200


def run_tests():
    """Alle Tests ausführen"""
    print(f"{Colors.YELLOW}=== DataFair API Tests ==={Colors.END}")
    print(f"API URL: {BASE_URL}\n")
    
    # 1. Health Check
    if not test_health():
        print(f"{Colors.RED}Health Check fehlgeschlagen! Ist der Server gestartet?{Colors.END}")
        return
    
    # 2. User Registration
    registration_result = test_register()
    if not registration_result:
        print(f"{Colors.RED}Registration fehlgeschlagen!{Colors.END}")
        return
    
    # Speichere Tokens
    access_token = registration_result.get('access_token')
    email = registration_result['user']['email']
    
    # 3. User Login
    login_result = test_login(email, "TestPassword123!")
    if not login_result:
        print(f"{Colors.RED}Login fehlgeschlagen!{Colors.END}")
        return
    
    # 4. Protected Endpoint
    if not test_protected_endpoint(access_token):
        print(f"{Colors.RED}Protected Endpoint Test fehlgeschlagen!{Colors.END}")
        return
    
    print(f"\n{Colors.GREEN}=== Alle Tests erfolgreich! ==={Colors.END}")
    print(f"\n{Colors.YELLOW}Tipp: Du kannst jetzt mit diesem Access Token weitere Requests machen:{Colors.END}")
    print(f"Bearer {access_token}")


if __name__ == "__main__":
    run_tests()