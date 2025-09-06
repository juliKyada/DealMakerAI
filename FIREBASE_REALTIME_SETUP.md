# Firebase Real-time Database Setup Guide

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "dealmaker-ai")
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Real-time Database

1. In your Firebase project, go to "Realtime Database" in the left sidebar
2. Click "Create Database"
3. Choose "Start in test mode" (for development) or "Start in production mode"
4. Select a location for your database (choose closest to your users)
5. Click "Done"

## Step 3: Get Database URL

1. In the Realtime Database section, you'll see your database URL
2. It looks like: `https://your-project-id-default-rtdb.firebaseio.com/`
3. Copy this URL - you'll need it for configuration

## Step 4: Create Service Account

1. Go to Project Settings (gear icon) → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. **Important**: Keep this file secure and never commit it to version control

## Step 5: Configure Your Application

### Option A: Using Environment Variables (Recommended)

Set these environment variables:

```bash
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_PRIVATE_KEY_ID="your-private-key-id"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
export FIREBASE_CLIENT_EMAIL="your-service-account@your-project-id.iam.gserviceaccount.com"
export FIREBASE_CLIENT_ID="your-client-id"
export FIREBASE_DATABASE_URL="https://your-project-id-default-rtdb.firebaseio.com/"
```

### Option B: Using Configuration File

1. Copy `firebase_config.json.example` to `firebase_config.json`
2. Fill in your actual Firebase project details from the downloaded service account JSON
3. **Important**: Add `firebase_config.json` to your `.gitignore` file

## Step 6: Database Rules (Security)

In Firebase Console → Realtime Database → Rules, set up appropriate rules:

### For Development (Test Mode):
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### For Production (Secure):
```json
{
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
}
```

## Step 7: Test the Setup

1. Start your Flask application
2. Try to sign up a new user
3. Check the Firebase Console → Realtime Database to see if user data appears
4. Look for console output showing "✅ User saved to Firebase Real-time Database"

## Troubleshooting

### Common Issues:

1. **"Firebase initialization failed"**
   - Check your environment variables or config file
   - Ensure the service account has proper permissions

2. **"Firebase Real-time Database connection failed"**
   - Verify your database URL is correct
   - Check if Real-time Database is enabled in Firebase Console

3. **"User created locally but Firebase sync failed"**
   - Check Firebase Console for error logs
   - Verify database rules allow writes
   - Check network connectivity

### Database Structure

Your Firebase Real-time Database will have this structure:

```
{
  "users": {
    "1": {
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T12:00:00.000Z",
      "is_active": true,
      "email_verified": false
    }
  },
  "users_by_email": {
    "john_example_com": {
      "user_id": "1",
      "username": "john_doe"
    }
  }
}
```

## Environment Variables for Production

For production deployment (Heroku, etc.), set these environment variables:

```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/
```

## Security Best Practices

1. **Never commit** `firebase_config.json` to version control
2. Use environment variables in production
3. Set up proper database rules for production
4. Regularly rotate service account keys
5. Monitor Firebase usage and costs
