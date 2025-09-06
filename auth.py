from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os
import secrets
from datetime import datetime, timedelta

# Firebase imports
import firebase_admin
from firebase_admin import credentials, db as firebase_db, auth as firebase_auth

# Initialize Firebase app (only once)
if not firebase_admin._apps:
    try:
        # Try to load from environment variables first
        import os
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}"
        }
        
        if firebase_config.get('project_id') and firebase_config.get('private_key') and firebase_config.get('client_email'):
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL', f"https://{firebase_config['project_id']}-default-rtdb.firebaseio.com/")
            })
            print("✅ Firebase initialized with environment variables")
        else:
            # Try to load from file
            import json
            with open("firebase_config.json", 'r') as f:
                firebase_config = json.load(f)
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': firebase_config.get('databaseURL', f"https://{firebase_config['project_id']}-default-rtdb.firebaseio.com/")
            })
            print("✅ Firebase initialized with config file")
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")
        print("⚠️ User data will only be saved to local database")

# Firebase Real-time Database reference
try:
    db_realtime = firebase_db.reference()
    print("✅ Firebase Real-time Database connected")
except Exception as e:
    print(f"⚠️ Firebase Real-time Database connection failed: {e}")
    db_realtime = None

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev-secret-key'))
        self.reset_token = serializer.dumps(self.id, salt='password-reset')
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev-secret-key'))
        try:
            user_id = serializer.loads(token, salt='password-reset', max_age=3600)
            return User.query.get(user_id)
        except:
            return None

    def _repr_(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_auth(app):
    """Initialize authentication components with Flask app"""
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configure mail (for password reset)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@dealmaker-ai.com')
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create tables
    with app.app_context():
        db.create_all()

def send_reset_email(user, token):
    """Send password reset email"""
    try:
        msg = Message(
            'Password Reset Request - DealMaker AI',
            recipients=[user.email],
            sender=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@dealmaker-ai.com')
        )
        msg.body = f'''
Hello {user.username},

You requested a password reset for your DealMaker AI account.

Click the link below to reset your password:
{url_for('reset_password', token=token, _external=True)}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
DealMaker AI Team
        '''
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# ---------- Firebase Helper ----------
def save_user_to_firebase(user, plain_password=None):
    """Save user info to Firebase Real-time Database and Auth"""
    try:
        if db_realtime is None:
            print("⚠️ Firebase Real-time Database not available")
            return False
            
        # Save to Firebase Real-time Database
        user_data = {
            "username": user.username,
            "email": user.email,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": user.is_active,
            "email_verified": user.email_verified
        }
        
        # Save to users node with user ID as key
        db_realtime.child('users').child(str(user.id)).set(user_data)
        
        # Also save by email for easy lookup
        db_realtime.child('users_by_email').child(user.email.replace('.', '_').replace('@', '_')).set({
            "user_id": str(user.id),
            "username": user.username
        })

        # Optionally also create Firebase Auth user
        if plain_password:
            try:
                firebase_auth.create_user(
                    email=user.email,
                    password=plain_password,
                    display_name=user.username,
                    uid=str(user.id)  # Use local user ID as Firebase UID
                )
                print("✅ Firebase Auth user created")
            except Exception as e:
                print(f"⚠️ Firebase Auth error: {e}")

        print("✅ User saved to Firebase Real-time Database")
        return True
    except Exception as e:
        print(f"⚠️ Error saving user to Firebase: {e}")
        return False


def register_auth_routes(app):
    """Register authentication routes"""
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                if request.is_json:
                    return jsonify({'status': 'success', 'message': 'Login successful'})
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
                flash('Invalid username or password', 'error')
        
        return render_template('login.html')
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            
            # Validation
            if not username or not email or not password:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
                flash('All fields are required', 'error')
                return render_template('signup.html')
            
            if password != confirm_password:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
                flash('Passwords do not match', 'error')
                return render_template('signup.html')
            
            if len(password) < 6:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
                flash('Password must be at least 6 characters', 'error')
                return render_template('signup.html')
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
                flash('Username already exists', 'error')
                return render_template('signup.html')
            
            if User.query.filter_by(email=email).first():
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
                flash('Email already registered', 'error')
                return render_template('signup.html')
            
            # Create new user in local DB
            user = User(username=username, email=email)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()

                # Save to Firebase too (non-blocking)
                firebase_success = save_user_to_firebase(user, plain_password=password)
                if not firebase_success:
                    print("⚠️ User created locally but Firebase sync failed")
                
                if request.is_json:
                    return jsonify({'status': 'success', 'message': 'Account created successfully'})
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                print(f"DB Error: {e}")
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Error creating account'}), 500
                flash('Error creating account', 'error')
        
        return render_template('signup.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
    
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            email = data.get('email')
            
            if not email:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Email is required'}), 400
                flash('Email is required', 'error')
                return render_template('forgot_password.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                token = user.generate_reset_token()
                if send_reset_email(user, token):
                    if request.is_json:
                        return jsonify({'status': 'success', 'message': 'Password reset email sent'})
                    flash('Password reset email sent! Check your inbox.', 'success')
                else:
                    if request.is_json:
                        return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500
                    flash('Failed to send email. Please try again.', 'error')
            else:
                if request.is_json:
                    return jsonify({'status': 'success', 'message': 'If email exists, password reset email sent'})
                flash('If email exists, password reset email sent', 'info')
        
        return render_template('forgot_password.html')
    
    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        user = User.query.filter_by(reset_token=token).first()
        
        if not user or user.reset_token_expires < datetime.utcnow():
            flash('Invalid or expired reset token', 'error')
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            
            if not password or not confirm_password:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
                flash('All fields are required', 'error')
                return render_template('reset_password.html', token=token)
            
            if password != confirm_password:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
                flash('Passwords do not match', 'error')
                return render_template('reset_password.html', token=token)
            
            if len(password) < 6:
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
                flash('Password must be at least 6 characters', 'error')
                return render_template('reset_password.html', token=token)
            
            # Update password
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expires = None
            
            try:
                db.session.commit()
                if request.is_json:
                    return jsonify({'status': 'success', 'message': 'Password reset successfully'})
                flash('Password reset successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                if request.is_json:
                    return jsonify({'status': 'error', 'message': 'Error resetting password'}), 500
                flash('Error resetting password', 'error')
        
        return render_template('reset_password.html', token=token)