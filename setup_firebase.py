#!/usr/bin/env python3
"""
Interactive Firebase setup script for DealMaker AI
This script will help you configure Firebase Real-time Database
"""

import os
import json
import sys

def create_firebase_config():
    """Create Firebase configuration interactively"""
    print("🔥 Firebase Real-time Database Setup")
    print("=" * 50)
    print()
    print("To get your Firebase credentials:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Go to Project Settings → Service Accounts")
    print("4. Click 'Generate new private key'")
    print("5. Download the JSON file")
    print()
    
    # Get project details
    project_id = input("Enter your Firebase Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required!")
        return False
    
    # Get service account email
    client_email = input("Enter your Service Account Email: ").strip()
    if not client_email:
        print("❌ Service Account Email is required!")
        return False
    
    # Get private key
    print("\nEnter your Private Key (paste the entire key including BEGIN/END lines):")
    print("(Press Enter twice when done)")
    private_key_lines = []
    while True:
        line = input()
        if line == "" and private_key_lines and private_key_lines[-1] == "":
            break
        private_key_lines.append(line)
    
    private_key = "\n".join(private_key_lines[:-1])  # Remove last empty line
    
    if not private_key or "BEGIN PRIVATE KEY" not in private_key:
        print("❌ Invalid private key format!")
        return False
    
    # Optional fields
    private_key_id = input("Enter Private Key ID (optional): ").strip()
    client_id = input("Enter Client ID (optional): ").strip()
    
    # Create config
    config = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
        "databaseURL": f"https://{project_id}-default-rtdb.firebaseio.com/"
    }
    
    # Save config file
    try:
        with open("firebase_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("\n✅ Firebase configuration saved to firebase_config.json")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def create_env_file():
    """Create .env file with Firebase environment variables"""
    print("\n🌍 Creating .env file for environment variables...")
    
    try:
        with open("firebase_config.json", "r") as f:
            config = json.load(f)
        
        env_content = f"""# Firebase Configuration
FIREBASE_PROJECT_ID={config['project_id']}
FIREBASE_PRIVATE_KEY_ID={config.get('private_key_id', '')}
FIREBASE_PRIVATE_KEY="{config['private_key']}"
FIREBASE_CLIENT_EMAIL={config['client_email']}
FIREBASE_CLIENT_ID={config.get('client_id', '')}
FIREBASE_DATABASE_URL={config['databaseURL']}
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Environment variables saved to .env file")
        print("💡 Add .env to your .gitignore file to keep credentials secure")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def setup_database_rules():
    """Provide instructions for setting up database rules"""
    print("\n🔒 Database Security Rules Setup")
    print("=" * 40)
    print("Go to Firebase Console → Realtime Database → Rules")
    print("Replace the rules with one of these options:")
    print()
    print("For Development (Test Mode):")
    print('''{
  "rules": {
    ".read": true,
    ".write": true
  }
}''')
    print()
    print("For Production (Secure):")
    print('''{
  "rules": {
    "users": {
      "$uid": {
        ".read": "auth != null && auth.uid == $uid",
        ".write": "auth != null && auth.uid == $uid"
      }
    },
    "users_by_email": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}''')

def main():
    """Main setup function"""
    print("Welcome to Firebase Real-time Database Setup!")
    print()
    
    # Check if config already exists
    if os.path.exists("firebase_config.json"):
        overwrite = input("firebase_config.json already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Create Firebase config
    if not create_firebase_config():
        print("Setup failed!")
        return
    
    # Create .env file
    create_env_file()
    
    # Setup instructions
    setup_database_rules()
    
    print("\n🎉 Setup Complete!")
    print("Next steps:")
    print("1. Test your setup: python test_firebase_signup.py")
    print("2. Start your app: python app.py")
    print("3. Try signing up a new user")
    print("4. Check Firebase Console to see user data")

if __name__ == "__main__":
    main()
