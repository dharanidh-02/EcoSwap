# EcoSwap - Sustainable Second-Hand Marketplace

A modern, responsive web application built with Flask that enables users to buy and sell second-hand items sustainably.

## Features

### User Authentication
- Secure user registration and login
- Password hashing with Werkzeug
- Session management with Flask-Login
- User profile management

### Product Management
- Create, read, update, and delete product listings
- Image upload support with automatic resizing
- Category-based organization
- Product search and filtering

### Shopping Experience
- Shopping cart functionality
- Purchase history tracking
- Product browsing with pagination
- Responsive design for all devices

### Modern UI/UX
- Bootstrap 5 responsive design
- Font Awesome icons
- Mobile-first approach
- Sustainable green color scheme
- Interactive elements and animations

## Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation
- **Flask-Bcrypt** - Password hashing
- **Werkzeug** - Security utilities
- **Pillow** - Image processing

### Frontend
- **HTML5** - Semantic markup
- **Bootstrap 5** - CSS framework
- **Font Awesome** - Icons
- **Vanilla JavaScript** - Interactive features
- **Jinja2** - Template engine

### Database
- **SQLite** - Development database (configurable for PostgreSQL in production)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Environment Variables
Set the following environment variables:

```bash
# Required
SESSION_SECRET=your-secret-key-here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///ecoswap.db
