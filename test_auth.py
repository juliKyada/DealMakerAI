#!/usr/bin/env python3
"""
Simple test script to verify authentication system
Run this after starting the main application to test auth functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_signup():
    """Test user registration"""
    print("Testing user registration...")
    
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signup", 
                               json=signup_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Signup successful: {result.get('message')}")
            return True
        else:
            print(f"❌ Signup failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False

def test_login():
    """Test user login"""
    print("Testing user login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful: {result.get('message')}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_protected_route():
    """Test accessing protected route without authentication"""
    print("Testing protected route access...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            # Check if redirected to login
            if "login" in response.url or "Login" in response.text:
                print("✅ Protected route correctly redirects to login")
                return True
            else:
                print("❌ Protected route should require authentication")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Protected route test error: {e}")
        return False

def test_forgot_password():
    """Test forgot password functionality"""
    print("Testing forgot password...")
    
    forgot_data = {
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/forgot_password", 
                               json=forgot_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Forgot password request: {result.get('message')}")
            return True
        else:
            print(f"❌ Forgot password failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Forgot password error: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("🔐 DealMaker AI Authentication Test Suite")
    print("=" * 50)
    
    tests = [
        ("Protected Route", test_protected_route),
        ("User Signup", test_signup),
        ("User Login", test_login),
        ("Forgot Password", test_forgot_password)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All authentication tests passed!")
    else:
        print("⚠️  Some tests failed. Check the application setup.")

if __name__ == "__main__":
    main()
