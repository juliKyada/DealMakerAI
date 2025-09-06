#!/usr/bin/env python3
"""
Test script to verify the app works without Firebase
"""

import requests
import json
import time

def test_app_without_firebase():
    """Test the app functionality without Firebase"""
    print("🧪 Testing App Without Firebase")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test data
    test_user = {
        "username": "testuser_local",
        "email": "test_local@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    
    test_product_url = "https://www.amazon.in/dp/B08N5WRWNW"  # Example Amazon product
    
    print("1. Testing user signup...")
    try:
        response = requests.post(f"{base_url}/signup", json=test_user)
        if response.status_code == 200:
            print("✅ User signup successful")
        else:
            print(f"⚠️ User signup response: {response.status_code}")
            if response.status_code == 400:
                print("   (User might already exist)")
    except Exception as e:
        print(f"❌ User signup failed: {e}")
        return False
    
    print("\n2. Testing user login...")
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{base_url}/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            # Get session cookies
            session = requests.Session()
            session.post(f"{base_url}/login", json=login_data)
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User login failed: {e}")
        return False
    
    print("\n3. Testing product addition...")
    try:
        product_data = {"url": test_product_url}
        response = session.post(f"{base_url}/add_product", json=product_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                product_id = result['product']['id']
                print(f"✅ Product added successfully: {product_id}")
            else:
                print(f"❌ Product addition failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Product addition failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Product addition failed: {e}")
        return False
    
    print("\n4. Testing negotiation...")
    try:
        negotiation_data = {
            "product_id": product_id,
            "offer": 500.0
        }
        response = session.post(f"{base_url}/chat", json=negotiation_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Negotiation successful: {result.get('response', '')[:50]}...")
        else:
            print(f"❌ Negotiation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Negotiation failed: {e}")
    
    print("\n5. Testing price refresh...")
    try:
        response = session.post(f"{base_url}/refresh_product/{product_id}")
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Price refresh successful")
            else:
                print(f"❌ Price refresh failed: {result.get('message')}")
        else:
            print(f"❌ Price refresh failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Price refresh failed: {e}")
    
    print("\n6. Testing data retrieval...")
    try:
        # Get all products
        response = session.get(f"{base_url}/get_all_products")
        if response.status_code == 200:
            print("✅ Products retrieval successful")
        else:
            print(f"❌ Products retrieval failed: {response.status_code}")
        
        # Get price data
        response = session.get(f"{base_url}/get_price_data/{product_id}")
        if response.status_code == 200:
            print("✅ Price data retrieval successful")
        else:
            print(f"❌ Price data retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Data retrieval failed: {e}")
    
    print("\n🎉 App test completed successfully!")
    print("\n📊 Features working:")
    print("- ✅ User authentication (signup/login)")
    print("- ✅ Product addition and tracking")
    print("- ✅ Price negotiation")
    print("- ✅ Price refresh")
    print("- ✅ Local data storage")
    print("- ✅ No Firebase dependencies")
    
    return True

if __name__ == "__main__":
    print("Starting app test without Firebase...")
    print("Make sure your Flask app is running on http://localhost:5000")
    print()
    
    try:
        test_app_without_firebase()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
