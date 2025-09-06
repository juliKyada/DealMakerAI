from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, flash
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os
import json
from amazon_scraper import (
    get_product_details, save_price_data, analyze_prices, 
    get_product_id, save_product_data, load_product_data, start_continuous_scraping
)
from auth import init_auth, register_auth_routes, db, User
from firebase_config import init_firebase, get_firebase_service
from firebase_admin import firestore
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Initialize authentication
init_auth(app)

# Initialize Firebase
firebase_initialized = init_firebase()
if firebase_initialized:
    logger.info("Firebase initialized successfully")
else:
    logger.info("Firebase not configured - continuing without real-time features")

# Global variables to store product data
product_data = {}

def load_saved_data():
    global product_data
    try:
        if os.path.exists('product_data.json'):
            with open('product_data.json', 'r') as f:
                product_data = json.load(f)
        else:
            product_data = {}
    except Exception as e:
        logger.error(f"Error loading saved data: {e}")
        product_data = {}

def save_data():
    try:
        with open('product_data.json', 'w') as f:
            json.dump(product_data, f)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def predict_price(product_id):
    try:
        filename = f"price_history_{product_id}.csv"
        if not os.path.exists(filename):
            return []

        df = pd.read_csv(filename)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Prepare data for prediction
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['Price'].values
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate predictions for next 7 days
        future_dates = np.arange(len(df), len(df) + 7).reshape(-1, 1)
        predictions = model.predict(future_dates)
        
        # Create prediction dates
        last_date = df['Timestamp'].iloc[-1]
        prediction_dates = [last_date + timedelta(days=i+1) for i in range(7)]
        
        return list(zip(prediction_dates, predictions))
    except Exception as e:
        logger.error(f"Error predicting price: {e}")
        return []

def get_price_history(product_id):
    try:
        filename = f"price_history_{product_id}.csv"
        if not os.path.exists(filename):
            return {'dates': [], 'prices': []}
        
        df = pd.read_csv(filename)
        return {
            'dates': df['Timestamp'].tolist(),
            'prices': df['Price'].tolist()
        }
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        return {'dates': [], 'prices': []}

def negotiate_price(product_id, offer):
    if product_id not in product_data:
        return {"response": "❌ Sorry, product not found."}

    product = product_data[product_id]
    price = float(product["current_price"])
    min_price = float(product["min_price"]) if "min_price" in product else price * 0.85  # fallback 15% discount

    if offer >= price:
        return {"response": f"✅ Great! The {product['name']} is yours for ₹{price}"}

    if offer >= price * 0.9:  # 90%+
        return {"response": f"🎉 Deal! I can give you the {product['name']} for ₹{offer}"}

    if offer >= price * 0.7:  # 70–90%
        counter = max((offer + price) // 2, min_price)
        return {"response": f"🤝 Hmm, I can’t do ₹{offer}, but how about ₹{counter}?"}

    if offer < price * 0.7:  # Too low
        return {"response": f"😅 That’s too low. Best I can do is ₹{min_price}"}

    return {"response": "Let's discuss further!"}

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    try:
        data = request.json
        product_id = data.get("product_id")
        offer = data.get("offer")

        if not product_id or offer is None:
            return jsonify({"response": "❌ Missing product_id or offer"}), 400

        result = negotiate_price(product_id, float(offer))
        
        # Store negotiation data in Firebase
        if firebase_initialized:
            firebase_service = get_firebase_service()
            
            # Save negotiation
            firebase_service.save_negotiation(current_user.id, product_id, {
                'user_offer': float(offer),
                'ai_response': result.get('response', ''),
                'product_name': product_data.get(product_id, {}).get('name', 'Unknown'),
                'current_price': product_data.get(product_id, {}).get('current_price', 0),
                'negotiation_type': 'price_negotiation'
            })
            
            # Save user input
            firebase_service.save_user_input(current_user.id, 'negotiation_offer', {
                'product_id': product_id,
                'offer_amount': float(offer),
                'product_name': product_data.get(product_id, {}).get('name', 'Unknown')
            })
            
            # Save user activity
            firebase_service.save_user_activity(current_user.id, 'negotiation_attempt', {
                'product_id': product_id,
                'offer_amount': float(offer),
                'ai_response': result.get('response', ''),
                'success': '✅' in result.get('response', '')
            })
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({"response": "⚠️ Something went wrong"}), 500


@app.route('/')
@login_required
def index():
    return render_template('index.html', products=product_data, user=current_user)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'status': 'error', 'message': 'URL is required'}), 400
        
        product_id = get_product_id(url)
        if not product_id:
            return jsonify({'status': 'error', 'message': 'Invalid Amazon URL'}), 400
        
        if product_id in product_data:
            return jsonify({'status': 'error', 'message': 'Product already being tracked'}), 400
        
        # Get initial product details
        product_name, current_price, error = get_product_details(url)
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
        
        if current_price is None:
            return jsonify({'status': 'error', 'message': 'Could not fetch product details'}), 400
        
        # If product name is not found, use product ID
        if not product_name:
            product_name = f"Product {product_id}"
        
        # Save initial price data
        save_price_data(product_id, current_price)
        avg_price, max_price, min_price = analyze_prices(product_id)
        
        # Store product data
        product_data[product_id] = {
            'url': url,
            'name': product_name,
            'current_price': current_price,
            'avg_price': avg_price,
            'max_price': max_price,
            'min_price': min_price,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save data to file
        save_data()
        
        # Store comprehensive data in Firebase
        if firebase_initialized:
            firebase_service = get_firebase_service()
            
            # Save product data
            firebase_service.save_product_data(product_id, product_data[product_id])
            
            # Save user input (URL submission)
            firebase_service.save_user_input(current_user.id, 'product_url', {
                'url': url,
                'product_id': product_id,
                'product_name': product_name
            })
            
            # Save user activity
            firebase_service.save_user_activity(current_user.id, 'product_added', {
                'product_id': product_id,
                'product_name': product_name,
                'url': url,
                'initial_price': current_price
            })
            
            # Save price history
            firebase_service.save_price_history(product_id, {
                'price': current_price,
                'price_type': 'initial',
                'source': 'user_added'
            })
            
            # Save product metadata
            firebase_service.save_product_metadata(product_id, {
                'name': product_name,
                'url': url,
                'category': 'amazon_product',
                'added_by_user': current_user.id,
                'added_at': datetime.now().isoformat()
            })
        
        return jsonify({
            'status': 'success', 
            'message': 'Product added successfully',
            'product': {
                'id': product_id,
                'name': product_name,
                'current_price': current_price
            }
        })
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_price_data/<product_id>')
@login_required
def get_price_data(product_id):
    try:
        if product_id not in product_data:
            return jsonify({'error': 'Product not found'}), 404
        
        product = product_data[product_id]
        price_history = get_price_history(product_id)
        predictions = predict_price(product_id)
        
        return jsonify({
            'current_price': float(product['current_price']),
            'avg_price': float(product['avg_price']),
            'max_price': float(product['max_price']),
            'min_price': float(product['min_price']),
            'last_updated': product['last_updated'],
            'name': product['name'],
            'history': price_history,
            'predictions': predictions
        })
    except Exception as e:
        logger.error(f"Error getting price data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_all_products')
@login_required
def get_all_products():
    try:
        products = []
        for product_id, data in product_data.items():
            products.append({
                'id': product_id,
                'name': data['name'],
                'current_price': data['current_price'],
                'last_updated': data['last_updated']
            })
        return jsonify(products)
    except Exception as e:
        logger.error(f"Error getting all products: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/refresh_product/<product_id>', methods=['POST'])
@login_required
def refresh_product(product_id):
    try:
        if product_id not in product_data:
            return jsonify({'status': 'error', 'message': 'Product not found'}), 404
        url = product_data[product_id]['url']
        product_name, current_price, error = get_product_details(url)
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
        if current_price is None:
            return jsonify({'status': 'error', 'message': 'Could not fetch product details'}), 400
        # Use old name if new name is missing
        if not product_name:
            product_name = product_data[product_id].get('name', f"Product {product_id}")
        # Save new price data
        save_price_data(product_id, current_price)
        avg_price, max_price, min_price = analyze_prices(product_id)
        # Update product data
        product_data[product_id].update({
            'name': product_name,
            'current_price': current_price,
            'avg_price': avg_price,
            'max_price': max_price,
            'min_price': min_price,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_data()
        
        # Store comprehensive price update data in Firebase
        if firebase_initialized:
            firebase_service = get_firebase_service()
            
            # Save price update
            firebase_service.save_price_update(product_id, {'price': current_price})
            
            # Save detailed price history
            firebase_service.save_price_history(product_id, {
                'price': current_price,
                'price_type': 'refresh',
                'source': 'manual_refresh',
                'previous_price': product_data[product_id].get('current_price', 0),
                'price_change': current_price - float(product_data[product_id].get('current_price', 0)),
                'price_change_percent': ((current_price - float(product_data[product_id].get('current_price', 0))) / float(product_data[product_id].get('current_price', 1))) * 100
            })
            
            # Save user activity
            firebase_service.save_user_activity(current_user.id, 'price_refresh', {
                'product_id': product_id,
                'product_name': product_name,
                'old_price': product_data[product_id].get('current_price', 0),
                'new_price': current_price,
                'price_change': current_price - float(product_data[product_id].get('current_price', 0))
            })
        return jsonify({'status': 'success', 'product': {
            'id': product_id,
            'name': product_name,
            'current_price': current_price,
            'avg_price': avg_price,
            'max_price': max_price,
            'min_price': min_price,
            'last_updated': product_data[product_id]['last_updated']
        }})
    except Exception as e:
        logger.error(f"Error refreshing product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/refresh_all_products', methods=['POST'])
@login_required
def refresh_all_products():
    try:
        updated_products = []
        for product_id, data in product_data.items():
            url = data['url']
            product_name, current_price, error = get_product_details(url)
            if error or current_price is None:
                continue  # Skip products that fail to update
            # Use old name if new name is missing
            if not product_name:
                product_name = data.get('name', f"Product {product_id}")
            save_price_data(product_id, current_price)
            avg_price, max_price, min_price = analyze_prices(product_id)
            product_data[product_id].update({
                'name': product_name,
                'current_price': current_price,
                'avg_price': avg_price,
                'max_price': max_price,
                'min_price': min_price,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            updated_products.append({
                'id': product_id,
                'name': product_name,
                'current_price': current_price,
                'avg_price': avg_price,
                'max_price': max_price,
                'min_price': min_price,
                'last_updated': product_data[product_id]['last_updated']
            })
        save_data()
        return jsonify({'status': 'success', 'products': updated_products})
    except Exception as e:
        logger.error(f"Error refreshing all products: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/realtime_updates')
@login_required
def realtime_updates():
    """Get real-time updates from Firebase"""
    try:
        if not firebase_initialized:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        firebase_service = get_firebase_service()
        updates = []
        
        # Get recent price updates (last 10)
        recent_updates = firebase_service.db.collection('price_history')\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(10)\
            .stream()
        
        for update in recent_updates:
            data = update.to_dict()
            updates.append({
                'product_id': data['product_id'],
                'price': data['price'],
                'timestamp': data['timestamp'].isoformat() if hasattr(data['timestamp'], 'isoformat') else str(data['timestamp'])
            })
        
        return jsonify({'updates': updates})
    except Exception as e:
        logger.error(f"Error getting real-time updates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sync_to_firebase', methods=['POST'])
@login_required
def sync_to_firebase():
    """Sync all local data to Firebase"""
    try:
        if not firebase_initialized:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        firebase_service = get_firebase_service()
        success = firebase_service.sync_local_data_to_firebase(product_data)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Data synced to Firebase successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to sync data to Firebase'}), 500
    except Exception as e:
        logger.error(f"Error syncing to Firebase: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_user_data')
@login_required
def get_user_data():
    """Get all user-related data from Firebase"""
    try:
        if not firebase_initialized:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        firebase_service = get_firebase_service()
        user_data = firebase_service.get_user_data(current_user.id)
        
        if user_data:
            return jsonify({'status': 'success', 'data': user_data})
        else:
            return jsonify({'status': 'error', 'message': 'No user data found'}), 404
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_product_analytics/<product_id>')
@login_required
def get_product_analytics(product_id):
    """Get comprehensive product analytics from Firebase"""
    try:
        if not firebase_initialized:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        firebase_service = get_firebase_service()
        analytics = firebase_service.get_product_analytics(product_id)
        
        if analytics:
            return jsonify({'status': 'success', 'analytics': analytics})
        else:
            return jsonify({'status': 'error', 'message': 'No analytics found for this product'}), 404
    except Exception as e:
        logger.error(f"Error getting product analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_all_negotiations')
@login_required
def get_all_negotiations():
    """Get all negotiations for the current user"""
    try:
        if not firebase_initialized:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        firebase_service = get_firebase_service()
        user_data = firebase_service.get_user_data(current_user.id)
        
        if user_data and 'negotiations' in user_data:
            return jsonify({'status': 'success', 'negotiations': user_data['negotiations']})
        else:
            return jsonify({'status': 'success', 'negotiations': {}})
    except Exception as e:
        logger.error(f"Error getting negotiations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_price_trends/<product_id>')
@login_required
def get_price_trends(product_id):
    """Get detailed price trends for a product"""
    try:
        if not firebase_initialized:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        firebase_service = get_firebase_service()
        analytics = firebase_service.get_product_analytics(product_id)
        
        if analytics and 'price_history' in analytics:
            price_history = analytics['price_history']
            # Process price history for trends
            trends = {
                'total_updates': len(price_history) if price_history else 0,
                'price_history': price_history,
                'latest_price': None,
                'price_changes': []
            }
            
            if price_history:
                # Sort by timestamp and get latest price
                sorted_prices = sorted(price_history.values(), key=lambda x: x.get('timestamp', ''))
                if sorted_prices:
                    trends['latest_price'] = sorted_prices[-1].get('price')
            
            return jsonify({'status': 'success', 'trends': trends})
        else:
            return jsonify({'status': 'error', 'message': 'No price history found'}), 404
    except Exception as e:
        logger.error(f"Error getting price trends: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    # Register authentication routes
    register_auth_routes(app)
    
    # Ensure static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Load saved data
    load_saved_data()
    
    # Start automatic refresh every 24 hours
    start_continuous_scraping(product_data, interval_minutes=1440)
    
    # Start the Flask application
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
