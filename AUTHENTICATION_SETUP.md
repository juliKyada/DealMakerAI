# Authentication Setup Guide

## Overview
The DealMaker AI application now includes a complete authentication system with:
- User registration and login
- Password reset functionality
- Session management
- Protected routes

## Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///users.db

# Email Configuration (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@dealmaker-ai.com

# Server Configuration
PORT=5000
```

## Email Setup for Password Reset

### Gmail Setup:
1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" for this application
3. Use the app password (not your regular password) in MAIL_PASSWORD

### Other Email Providers:
- **Outlook/Hotmail**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom SMTP**: Use your provider's SMTP settings

## Installation

1. Install the new dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

## Features

### User Registration
- Username and email validation
- Password strength checking
- Duplicate account prevention

### Login System
- Secure password authentication
- Remember me functionality
- Session management

### Password Reset
- Email-based password reset
- Secure token generation
- 1-hour token expiration

### Protected Routes
All main application routes now require authentication:
- Dashboard access
- Product management
- Price tracking
- Negotiation features

## Security Features

- Password hashing with bcrypt
- CSRF protection
- Secure session management
- Token-based password reset
- Input validation and sanitization

## Database

The application uses SQLite by default and will automatically create the necessary tables on first run. The database file `users.db` will be created in your project directory.

## Troubleshooting

### Email Not Sending
- Check your email credentials
- Ensure 2FA is enabled and app password is used
- Verify SMTP settings
- Check firewall/network restrictions

### Database Issues
- Ensure write permissions in project directory
- Check if users.db file is corrupted
- Delete users.db to reset database

### Login Issues
- Clear browser cookies/cache
- Check if user account exists
- Verify password strength requirements
