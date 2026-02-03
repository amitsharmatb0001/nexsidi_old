import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """
    Test complete authentication flow:
    1. Signup
    2. Login
    3. Get user info
    """
    print("=" * 50)
    print("TESTING AUTHENTICATION FLOW")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "test@nexsidi.com",
        "password": "testpass123",
        "full_name": "Test User",
        "phone": "+91-9876543210"
    }
    
    # 1. SIGNUP
    print("\n1. Testing Signup...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json=test_user
        )
        
        if response.status_code == 201:
            print("✅ Signup successful!")
            pprint(response.json())
        elif response.status_code == 400:
            print("⚠️  User already exists, continuing to login...")
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"❌ Error during signup: {e}")
        return
    
    # 2. LOGIN
    print("\n2. Testing Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        
        if response.status_code == 200:
            print("✅ Login successful!")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"Token: {access_token[:50]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # 3. GET USER INFO
    print("\n3. Testing Get Current User...")
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Got user info successfully!")
            pprint(response.json())
        else:
            print(f"❌ Get user info failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
    
    print("\n" + "=" * 50)
    print("Authentication flow test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_flow()