#!/usr/bin/env python3
"""
Simple Firebase test to verify configuration
"""

import json
import os

def test_firebase():
    print("🔥 Testing Firebase Configuration")
    print("=" * 40)
    
    # Check if config file exists
    if not os.path.exists('firebase_config.json'):
        print("❌ firebase_config.json not found")
        return False
    
    # Load config
    try:
        with open('firebase_config.json', 'r') as f:
            config = json.load(f)
        print("✅ Config file loaded successfully")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    # Check required fields
    required_fields = ['project_id', 'private_key', 'client_email', 'databaseURL']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"❌ Missing fields: {', '.join(missing_fields)}")
        return False
    
    print(f"✅ Project ID: {config['project_id']}")
    print(f"✅ Database URL: {config['databaseURL']}")
    
    # Test Firebase initialization
    try:
        import firebase_admin
        from firebase_admin import credentials, db as firebase_db
        
        print("✅ Firebase imports successful")
        
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': config['databaseURL']
            })
            print("✅ Firebase initialized successfully")
        else:
            print("✅ Firebase already initialized")
        
        # Test database connection
        db_ref = firebase_db.reference()
        print("✅ Database reference created")
        
        # Test write operation
        test_data = {
            "test": True,
            "message": "Firebase connection test",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        db_ref.child('test').child('connection').set(test_data)
        print("✅ Test data written to Firebase")
        
        # Test read operation
        test_result = db_ref.child('test').child('connection').get()
        if test_result and test_result.get('test'):
            print("✅ Test data read from Firebase")
            
            # Clean up
            db_ref.child('test').child('connection').delete()
            print("✅ Test data cleaned up")
            
            print("\n🎉 Firebase is working perfectly!")
            return True
        else:
            print("❌ Failed to read test data")
            return False
            
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        return False

if __name__ == "__main__":
    success = test_firebase()
    if success:
        print("\n✅ Your Firebase setup is ready!")
        print("You can now run your Flask app and test user signup.")
    else:
        print("\n❌ Firebase setup needs attention.")
        print("Check the error messages above.")
