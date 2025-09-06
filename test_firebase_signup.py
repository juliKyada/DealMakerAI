#!/usr/bin/env python3
"""
Test script to verify Firebase Real-time Database signup functionality
Run this script to test if Firebase is properly configured
"""

import os
import sys
import json
from datetime import datetime

def test_firebase_connection():
    """Test Firebase connection and configuration"""
    print("🔍 Testing Firebase Real-time Database connection...")
    
    try:
        # Test Firebase imports
        import firebase_admin
        from firebase_admin import credentials, db as firebase_db
        print("✅ Firebase imports successful")
        
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            # Try to load config from file
            if os.path.exists('firebase_config.json'):
                with open('firebase_config.json', 'r') as f:
                    config = json.load(f)
                cred = credentials.Certificate(config)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': config['databaseURL']
                })
                print("✅ Firebase initialized from config file")
            else:
                print("❌ Firebase not initialized and no config file found")
                return False
        else:
            print("✅ Firebase already initialized")
        
        # Test database connection
        db_ref = firebase_db.reference()
        print("✅ Firebase Real-time Database reference created")
        
        # Test write operation
        test_data = {
            "test": True,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Firebase connection test"
        }
        
        db_ref.child('test').child('connection').set(test_data)
        print("✅ Test data written to Firebase")
        
        # Test read operation
        test_result = db_ref.child('test').child('connection').get()
        if test_result and test_result.get('test'):
            print("✅ Test data read from Firebase")
            
            # Clean up test data
            db_ref.child('test').child('connection').delete()
            print("✅ Test data cleaned up")
            return True
        else:
            print("❌ Failed to read test data from Firebase")
            return False
            
    except ImportError as e:
        print(f"❌ Firebase import error: {e}")
        print("💡 Install Firebase: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Firebase connection error: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL'
    ]
    
    optional_vars = [
        'FIREBASE_DATABASE_URL',
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_CLIENT_ID'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} is set")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
    
    return True

def test_config_file():
    """Test if Firebase config file exists and is valid"""
    print("\n🔍 Checking Firebase config file...")
    
    config_file = "firebase_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            required_fields = ['project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if not config.get(field)]
            
            if missing_fields:
                print(f"❌ Config file missing fields: {', '.join(missing_fields)}")
                return False
            else:
                print("✅ Firebase config file is valid")
                return True
        except json.JSONDecodeError:
            print("❌ Firebase config file is not valid JSON")
            return False
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return False
    else:
        print("⚠️  Firebase config file not found")
        print("💡 Create firebase_config.json or set environment variables")
        return False

def main():
    """Main test function"""
    print("🚀 Firebase Real-time Database Setup Test")
    print("=" * 50)
    
    # Test 1: Environment variables or config file
    env_ok = test_environment_variables()
    config_ok = test_config_file()
    
    if not env_ok and not config_ok:
        print("\n❌ No Firebase configuration found!")
        print("\n📋 Setup Instructions:")
        print("1. Set environment variables OR create firebase_config.json")
        print("2. See FIREBASE_REALTIME_SETUP.md for detailed instructions")
        return False
    
    # Test 2: Firebase connection
    connection_ok = test_firebase_connection()
    
    if connection_ok:
        print("\n🎉 All tests passed! Firebase is properly configured.")
        print("✅ You can now run your Flask app and test user signup.")
        return True
    else:
        print("\n❌ Firebase connection test failed!")
        print("💡 Check your configuration and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
