# Firebase Real-time Integration Setup

This guide will help you set up Firebase for real-time data synchronization with your DealMaker AI application.

## 🔥 Firebase Setup Steps

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter project name: `dealmaker-ai` (or your preferred name)
4. Enable Google Analytics (optional)
5. Click "Create project"

### 2. Enable Firestore Database

1. In your Firebase project, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a location close to your users
5. Click "Done"

### 3. Create Service Account

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `firebase_config.json` and place it in your project root

### 4. Configure Environment Variables (Alternative)

Instead of using a config file, you can set environment variables:

```bash
# Windows PowerShell
$env:FIREBASE_PROJECT_ID="your-project-id"
$env:FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
$env:FIREBASE_CLIENT_EMAIL="your-service-account@your-project-id.iam.gserviceaccount.com"

# Linux/Mac
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
export FIREBASE_CLIENT_EMAIL="your-service-account@your-project-id.iam.gserviceaccount.com"
```

### 5. Install Firebase Dependencies

```bash
pip install firebase-admin==6.4.0 pyrebase4==4.7.1
```

## 🚀 Features Enabled

### Real-time Data Sync
- **Product Data**: Automatically synced to Firebase when products are added/updated
- **Price Updates**: Real-time price changes are stored in Firebase
- **Cross-device Sync**: Access your data from any device

### New Dashboard Features
- **Real-time Updates Panel**: Shows recent price changes
- **Firebase Sync Button**: Manually sync all local data to Firebase
- **Auto-refresh**: Updates every 30 seconds automatically

### API Endpoints
- `GET /realtime_updates` - Get recent price updates
- `POST /sync_to_firebase` - Sync all local data to Firebase

## 📊 Firebase Collections Structure

### Products Collection (`products`)
```json
{
  "product_id": "B0DHY1V1GM",
  "name": "Product Name",
  "current_price": 121275.0,
  "avg_price": 120701.67,
  "max_price": 121275.00,
  "min_price": 120415.00,
  "url": "https://amazon.in/...",
  "last_updated": "2024-01-20T10:30:00Z",
  "firebase_sync": true
}
```

### Price History Collection (`price_history`)
```json
{
  "product_id": "B0DHY1V1GM",
  "price": 121275.0,
  "timestamp": "2024-01-20T10:30:00Z",
  "source": "scraper"
}
```

## 🔧 Configuration Options

### Option 1: Config File
Place `firebase_config.json` in your project root with your service account credentials.

### Option 2: Environment Variables
Set the required environment variables as shown above.

### Option 3: Default Initialization
The app will attempt to initialize Firebase with default credentials if no configuration is found.

## 🛡️ Security Rules (Firestore)

For production, update your Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to read/write their own data
    match /products/{productId} {
      allow read, write: if request.auth != null;
    }
    
    match /price_history/{historyId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 🧪 Testing Firebase Integration

1. **Start the application**: `python app.py`
2. **Login to your account**
3. **Add a product** - It will automatically sync to Firebase
4. **Check Real-time Updates panel** - Should show recent updates
5. **Click "Sync to Firebase"** - Syncs all local data
6. **Refresh the page** - Data should persist

## 🔍 Troubleshooting

### Common Issues

1. **"Firebase not initialized" error**
   - Check your Firebase configuration
   - Ensure service account has proper permissions

2. **"Permission denied" error**
   - Update Firestore security rules
   - Check service account permissions

3. **Real-time updates not showing**
   - Check browser console for errors
   - Verify Firebase connection

### Debug Mode

Enable debug logging by setting the log level in `app.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📱 Mobile App Integration

The Firebase integration also enables:
- **Mobile app development** using Firebase SDKs
- **Cross-platform data sync**
- **Offline support** with Firebase offline persistence
- **Push notifications** for price alerts

## 🎯 Next Steps

1. Set up Firebase project and get credentials
2. Configure authentication (optional)
3. Set up Firestore security rules
4. Test the integration
5. Deploy to production with proper security rules

Your DealMaker AI application now has real-time Firebase integration! 🎉
