import requests
import json

# Test registration data
test_data = {
    "username": "testuser456",
    "fullName": "Test User 456", 
    "email": "testuser456@example.com",
    "password": "TestPass123!"
}

# Test the registration endpoint
try:
    response = requests.post(
        "http://127.0.0.1:5000/api/auth/register",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Registration successful!")
    else:
        print("❌ Registration failed!")
        
except Exception as e:
    print(f"Error: {e}") 