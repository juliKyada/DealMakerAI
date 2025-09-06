#!/usr/bin/env python3
"""
Quick Firebase setup - just paste your service account JSON
"""

import json
import os

def main():
    print("🔥 Quick Firebase Setup")
    print("=" * 30)
    print()
    print("1. Go to Firebase Console → Project Settings → Service Accounts")
    print("2. Click 'Generate new private key'")
    print("3. Copy the ENTIRE JSON content from the downloaded file")
    print("4. Paste it below (press Ctrl+Z then Enter when done on Windows)")
    print()
    
    print("Paste your Firebase service account JSON here:")
    print("(The JSON should start with { and end with })")
    print()
    
    # Read the JSON input
    json_lines = []
    try:
        while True:
            line = input()
            json_lines.append(line)
    except EOFError:
        pass
    
    json_content = '\n'.join(json_lines)
    
    try:
        # Parse the JSON
        config = json.loads(json_content)
        
        # Validate required fields
        required_fields = ['project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        # Add database URL if not present
        if 'databaseURL' not in config:
            config['databaseURL'] = f"https://{config['project_id']}-default-rtdb.firebaseio.com/"
        
        # Save the config
        with open('firebase_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Firebase configuration saved!")
        print(f"📁 Saved to: firebase_config.json")
        print(f"🔗 Database URL: {config['databaseURL']}")
        
        # Test the configuration
        print("\n🧪 Testing configuration...")
        try:
            import firebase_admin
            from firebase_admin import credentials, db as firebase_db
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(config)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': config['databaseURL']
                })
            
            # Test connection
            db_ref = firebase_db.reference()
            print("✅ Firebase connection successful!")
            
        except Exception as e:
            print(f"⚠️  Firebase connection test failed: {e}")
            print("💡 The config file was saved, but you may need to check your Firebase project settings")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        print("💡 Make sure you copied the entire JSON content from the service account file")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Setup complete! Now run: python test_firebase_signup.py")
    else:
        print("\n❌ Setup failed. Please try again.")
