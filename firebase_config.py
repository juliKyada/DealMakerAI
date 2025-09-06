"""
Firebase configuration and initialization for DealMaker AI
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Firebase service for real-time data operations"""
    
    def __init__(self):
        self.db = None
        self.db_realtime = None
        self.initialized = False
        
    def initialize(self, config_path=None):
        """Initialize Firebase with configuration"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.db_realtime = firebase_db.reference()
                self.initialized = True
                return True
            
            # Try to get config from environment variables first
            firebase_config = self._get_config_from_env()
            
            # If not found in env, try to load from file
            if not firebase_config and config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    firebase_config = json.load(f)
            
            if not firebase_config:
                logger.info("No Firebase configuration found. Real-time features disabled.")
                return False
            else:
                # Initialize with provided credentials
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
            
            self.db_realtime = firebase_db.reference()
            self.initialized = True
            logger.info("Firebase initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False
    
    def _get_config_from_env(self):
        """Get Firebase configuration from environment variables"""
        config = {}
        
        # Required fields for Firebase config
        required_fields = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL'
        ]
        
        # Check if all required fields are present
        if all(os.getenv(field) for field in required_fields):
            config = {
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}"
            }
        
        return config if config else None
    
    def save_product_data(self, product_id, product_data):
        """Save product data to Firebase Real-time Database"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Save to Real-time Database
            product_ref = self.db_realtime.child('products').child(product_id)
            product_ref.set({
                **product_data,
                'last_updated': datetime.utcnow().isoformat(),
                'firebase_sync': True
            })
            logger.info(f"Product {product_id} saved to Firebase Real-time Database")
            return True
        except Exception as e:
            logger.error(f"Failed to save product {product_id} to Firebase: {e}")
            return False
    
    def save_price_update(self, product_id, price_data):
        """Save price update to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Save to price_history collection
            price_ref = self.db.collection('price_history').document()
            price_ref.set({
                'product_id': product_id,
                'price': price_data['price'],
                'timestamp': datetime.utcnow(),
                'source': 'scraper'
            })
            
            # Update product document with latest price
            product_ref = self.db.collection('products').document(product_id)
            product_ref.update({
                'current_price': price_data['price'],
                'last_price_update': datetime.utcnow()
            })
            
            logger.info(f"Price update for {product_id} saved to Firebase")
            return True
        except Exception as e:
            logger.error(f"Failed to save price update for {product_id}: {e}")
            return False
    
    def get_product_data(self, product_id):
        """Get product data from Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None
        
        try:
            doc_ref = self.db.collection('products').document(product_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                logger.info(f"Product {product_id} not found in Firebase")
                return None
        except Exception as e:
            logger.error(f"Failed to get product {product_id} from Firebase: {e}")
            return None
    
    def get_price_history(self, product_id, limit=100):
        """Get price history from Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return []
        
        try:
            price_history = []
            docs = self.db.collection('price_history')\
                .where('product_id', '==', product_id)\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            for doc in docs:
                data = doc.to_dict()
                price_history.append({
                    'timestamp': data['timestamp'],
                    'price': data['price']
                })
            
            return price_history
        except Exception as e:
            logger.error(f"Failed to get price history for {product_id}: {e}")
            return []
    
    def sync_local_data_to_firebase(self, local_product_data):
        """Sync local product data to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            batch = self.db.batch()
            synced_count = 0
            
            for product_id, data in local_product_data.items():
                doc_ref = self.db.collection('products').document(product_id)
                batch.set(doc_ref, {
                    **data,
                    'last_updated': datetime.utcnow(),
                    'firebase_sync': True
                })
                synced_count += 1
            
            batch.commit()
            logger.info(f"Synced {synced_count} products to Firebase")
            return True
        except Exception as e:
            logger.error(f"Failed to sync data to Firebase: {e}")
            return False
    
    def save_user_input(self, user_id, input_type, input_data):
        """Save user input data (URLs, offers, negotiations) to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            input_ref = self.db_realtime.child('user_inputs').child(str(user_id)).child(input_type).push()
            input_ref.set({
                **input_data,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': str(user_id)
            })
            logger.info(f"User input saved for user {user_id}, type: {input_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user input: {e}")
            return False
    
    def save_negotiation(self, user_id, product_id, negotiation_data):
        """Save negotiation data to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            negotiation_ref = self.db_realtime.child('negotiations').push()
            negotiation_ref.set({
                **negotiation_data,
                'user_id': str(user_id),
                'product_id': product_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f"Negotiation saved for user {user_id}, product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save negotiation: {e}")
            return False
    
    def save_price_history(self, product_id, price_data):
        """Save detailed price history to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            price_ref = self.db_realtime.child('price_history').child(product_id).push()
            price_ref.set({
                **price_data,
                'product_id': product_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f"Price history saved for product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save price history: {e}")
            return False
    
    def save_user_activity(self, user_id, activity_type, activity_data):
        """Save user activity and interactions to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            activity_ref = self.db_realtime.child('user_activities').child(str(user_id)).push()
            activity_ref.set({
                **activity_data,
                'activity_type': activity_type,
                'user_id': str(user_id),
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f"User activity saved for user {user_id}, type: {activity_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user activity: {e}")
            return False
    
    def save_product_metadata(self, product_id, metadata):
        """Save product metadata (images, descriptions, categories) to Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            metadata_ref = self.db_realtime.child('product_metadata').child(product_id)
            metadata_ref.set({
                **metadata,
                'product_id': product_id,
                'last_updated': datetime.utcnow().isoformat()
            })
            logger.info(f"Product metadata saved for product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save product metadata: {e}")
            return False
    
    def get_user_data(self, user_id):
        """Get all user-related data from Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None
        
        try:
            user_data = {}
            
            # Get user inputs
            inputs = self.db_realtime.child('user_inputs').child(str(user_id)).get()
            if inputs:
                user_data['inputs'] = inputs
            
            # Get user activities
            activities = self.db_realtime.child('user_activities').child(str(user_id)).get()
            if activities:
                user_data['activities'] = activities
            
            # Get user negotiations
            negotiations = self.db_realtime.child('negotiations').order_by_child('user_id').equal_to(str(user_id)).get()
            if negotiations:
                user_data['negotiations'] = negotiations
            
            return user_data
        except Exception as e:
            logger.error(f"Failed to get user data: {e}")
            return None
    
    def get_product_analytics(self, product_id):
        """Get comprehensive product analytics from Firebase"""
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None
        
        try:
            analytics = {}
            
            # Get price history
            price_history = self.db_realtime.child('price_history').child(product_id).get()
            if price_history:
                analytics['price_history'] = price_history
            
            # Get negotiations for this product
            negotiations = self.db_realtime.child('negotiations').order_by_child('product_id').equal_to(product_id).get()
            if negotiations:
                analytics['negotiations'] = negotiations
            
            # Get product metadata
            metadata = self.db_realtime.child('product_metadata').child(product_id).get()
            if metadata:
                analytics['metadata'] = metadata
            
            return analytics
        except Exception as e:
            logger.error(f"Failed to get product analytics: {e}")
            return None

# Global Firebase service instance
firebase_service = FirebaseService()

def init_firebase(config_path=None):
    """Initialize Firebase service"""
    return firebase_service.initialize(config_path)

def get_firebase_service():
    """Get Firebase service instance"""
    return firebase_service
