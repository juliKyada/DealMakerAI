# DealMaker AI - Amazon Price Tracker with Authentication

A comprehensive Amazon price tracking application with user authentication, price prediction, and negotiation features.

## Features

### 🔐 Authentication System
- **User Registration**: Create accounts with username, email, and secure passwords
- **Login/Logout**: Secure session management with "Remember Me" functionality
- **Password Reset**: Email-based password recovery with secure tokens
- **Protected Routes**: All features require user authentication

### 📊 Price Tracking
- **Real-time Monitoring**: Track Amazon product prices continuously
- **Price History**: Visual charts showing price trends over time
- **Price Predictions**: AI-powered price forecasting for the next 7 days
- **Price Analysis**: Average, minimum, and maximum price calculations

### 🤖 Negotiation Features
- **AI Chatbot**: Negotiate prices with an intelligent chatbot
- **Dynamic Pricing**: Smart counter-offers based on price history
- **Deal Making**: Automated negotiation responses

### 🎨 Modern UI
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Beautiful Interface**: Modern Bootstrap-based design
- **Interactive Charts**: Real-time price visualization
- **User-Friendly**: Intuitive navigation and controls

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd DealMaker-AI

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your settings:
```bash
SECRET_KEY=your-secret-key-here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the Application
- Open your browser to `http://localhost:5000`
- Create an account or login
- Start tracking Amazon products!

## Authentication Setup

For detailed authentication configuration, see [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md).

### Email Configuration
To enable password reset functionality:
1. Enable 2-factor authentication on your email account
2. Generate an app password
3. Configure SMTP settings in your `.env` file

## Usage

### Adding Products
1. Login to your account
2. Paste an Amazon product URL in the "Add New Product" form
3. Click "Add Product" to start tracking

### Viewing Price Data
- Click on any product in the "Tracked Products" list
- View current price, average price, and price change
- Analyze price history charts
- See AI predictions for future prices

### Negotiating Prices
1. Select a product from your tracked list
2. Enter your offer price in the negotiation section
3. Chat with the AI to negotiate the best deal

## API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `POST /forgot_password` - Request password reset
- `POST /reset_password/<token>` - Reset password with token

### Product Management
- `POST /add_product` - Add new product to track
- `GET /get_all_products` - Get all tracked products
- `GET /get_price_data/<product_id>` - Get detailed price data
- `POST /refresh_product/<product_id>` - Refresh single product
- `POST /refresh_all_products` - Refresh all products

### Negotiation
- `POST /chat` - Negotiate price with AI chatbot

## Security Features

- **Password Hashing**: Bcrypt encryption for secure password storage
- **Session Management**: Secure Flask-Login integration
- **CSRF Protection**: Built-in CSRF protection
- **Input Validation**: Comprehensive input sanitization
- **Token Security**: Secure password reset tokens with expiration

## Testing

Run the authentication test suite:
```bash
python test_auth.py
```

This will test:
- User registration
- Login functionality
- Protected route access
- Password reset features

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Flask-Mail**: Email functionality
- **Flask-Bcrypt**: Password hashing
- **Pandas**: Data analysis
- **Scikit-learn**: Machine learning for price prediction
- **BeautifulSoup4**: Web scraping
- **Chart.js**: Interactive charts

## Deployment

### Heroku
1. Create a `Procfile` with: `web: python app.py`
2. Set environment variables in Heroku dashboard
3. Deploy using Git

### Other Platforms
- Ensure all dependencies are installed
- Set environment variables
- Configure email settings for production
- Use a production WSGI server (e.g., Gunicorn)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) guide
2. Review the test suite for troubleshooting
3. Open an issue on GitHub

---

**DealMaker AI** - Making smart deals with AI-powered price tracking and negotiation! 🚀
