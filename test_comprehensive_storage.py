#!/usr/bin/env python3
"""
Test script to verify comprehensive data storage in Firebase
"""

import requests
import json
import time

def test_comprehensive_storage():
    """Test all data storage functionality"""
    print("🧪 Testing Comprehensive Data Storage")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test data
    test_user = {
        "username": "testuser_firebase",
        "email": "test_firebase@example.com",
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
        # Get user data
        response = session.get(f"{base_url}/get_user_data")
        if response.status_code == 200:
            print("✅ User data retrieval successful")
        else:
            print(f"❌ User data retrieval failed: {response.status_code}")
        
        # Get product analytics
        response = session.get(f"{base_url}/get_product_analytics/{product_id}")
        if response.status_code == 200:
            print("✅ Product analytics retrieval successful")
        else:
            print(f"❌ Product analytics retrieval failed: {response.status_code}")
        
        # Get negotiations
        response = session.get(f"{base_url}/get_all_negotiations")
        if response.status_code == 200:
            print("✅ Negotiations retrieval successful")
        else:
            print(f"❌ Negotiations retrieval failed: {response.status_code}")
        
        # Get price trends
        response = session.get(f"{base_url}/get_price_trends/{product_id}")
        if response.status_code == 200:
            print("✅ Price trends retrieval successful")
        else:
            print(f"❌ Price trends retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Data retrieval failed: {e}")
    
    print("\n🎉 Comprehensive storage test completed!")
    print("\n📊 Check Firebase Console to see all stored data:")
    print("- Users: /users")
    print("- User Inputs: /user_inputs")
    print("- User Activities: /user_activities")
    print("- Negotiations: /negotiations")
    print("- Products: /products")
    print("- Price History: /price_history")
    print("- Product Metadata: /product_metadata")
    
    return True

if __name__ == "__main__":
    print("Starting comprehensive storage test...")
    print("Make sure your Flask app is running on http://localhost:5000")
    print()
    
    try:
        test_comprehensive_storage()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
