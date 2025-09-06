# How to Get Firebase Credentials

## Step-by-Step Guide

### 1. Go to Firebase Console
- Visit: https://console.firebase.google.com/
- Sign in with your Google account

### 2. Create or Select Project
- If you don't have a project: Click "Create a project"
- If you have a project: Select it from the list

### 3. Enable Real-time Database
- In the left sidebar, click "Realtime Database"
- Click "Create Database"
- Choose "Start in test mode" (for development)
- Select a location (choose closest to your users)
- Click "Done"

### 4. Get Service Account Credentials
- Click the gear icon (⚙️) → "Project settings"
- Go to "Service accounts" tab
- Click "Generate new private key"
- Click "Generate key" in the popup
- A JSON file will download automatically

### 5. Use the Downloaded JSON
The downloaded file contains something like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-name",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project-name.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-name.iam.gserviceaccount.com"
}
```

### 6. Run the Setup Script
```bash
python quick_firebase_setup.py
```

Then paste the ENTIRE JSON content from the downloaded file.

## Important Notes

- ✅ **DO**: Copy the entire JSON content from the downloaded file
- ❌ **DON'T**: Copy just the database URL
- ❌ **DON'T**: Copy just the private key
- ✅ **DO**: Include the curly braces `{` and `}`

## What You Need to Copy

Copy everything from the downloaded JSON file, including:
- The opening `{`
- All the fields (project_id, private_key, client_email, etc.)
- The closing `}`

## Example of What to Copy

```
{
  "type": "service_account",
  "project_id": "dealmaker-ea2ba",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@dealmaker-ea2ba.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40dealmaker-ea2ba.iam.gserviceaccount.com"
}
```

## After Setup

1. Test your configuration:
   ```bash
   python test_firebase_signup.py
   ```

2. Start your app:
   ```bash
   python app.py
   ```

3. Test user signup at: http://localhost:5000/signup
