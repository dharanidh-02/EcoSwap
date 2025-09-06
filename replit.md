# EcoSwap - Sustainable Second-Hand Marketplace

## Overview

EcoSwap is a Flask-based web application that serves as a sustainable marketplace for second-hand items. The platform enables users to buy and sell pre-owned products, promoting environmental sustainability through circular economy principles. The application provides core e-commerce functionality including user authentication, product listings, shopping cart, and transaction management.

## Recent Changes

### September 2025 - Complete UI Modernization
- **Design Overhaul**: Transformed the entire UI with a modern emerald/teal gradient theme
- **Typography**: Added Inter font family from Google Fonts for professional appearance
- **Color System**: Implemented CSS custom properties for consistent theming throughout the app
- **Enhanced Components**: Modernized buttons, cards, forms, and navigation with contemporary styling
- **Animations**: Added smooth transitions, hover effects, and floating animations
- **Glass Effects**: Implemented backdrop-filter styling for modern visual depth
- **Mobile Enhancement**: Improved responsive design with better mobile breakpoints
- **Accessibility**: Added reduced motion preferences support for better accessibility
- **Hero Section**: Redesigned with gradient text, better CTAs, and visual enhancements
- **Search Interface**: Enhanced with emoji icons and improved user experience

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with modular structure separating concerns across multiple files
- **Database ORM**: SQLAlchemy with declarative base model for database operations
- **Authentication**: Flask-Login for session management with Werkzeug/Flask-Bcrypt for password hashing
- **Form Handling**: Flask-WTF with CSRF protection and comprehensive form validation
- **File Uploads**: Custom image processing with Pillow for automatic resizing and optimization
- **Security**: CSRF protection, secure password hashing, and session management

### Frontend Architecture
- **Template Engine**: Jinja2 with inheritance-based template structure using base.html
- **CSS Framework**: Bootstrap 5 for responsive design and mobile-first approach
- **Icons**: Font Awesome for consistent iconography
- **Typography**: Inter font family loaded via Google Fonts for modern, professional appearance
- **JavaScript**: Vanilla JavaScript for interactive features like image previews and form enhancements
- **Design System**: Modern emerald/teal gradient theme with CSS custom properties for consistency
- **Animations**: Contemporary CSS animations with reduced motion accessibility support
- **Glass Effects**: Modern backdrop-filter styling for cards and navigation elements
- **Security**: XSS-safe DOM manipulation using textContent instead of innerHTML for user-generated content

### Database Design
- **User Management**: User model with relationships to products, cart items, and purchase history
- **Product System**: Product model with category classification, ownership tracking, and sold status
- **Shopping Cart**: Cart model implementing many-to-many relationship between users and products
- **Transaction History**: PurchaseHistory model for tracking completed transactions
- **Data Integrity**: Foreign key constraints and unique constraints to maintain data consistency

### Application Structure
- **Modular Design**: Separation of concerns with dedicated files for models, forms, routes, and utilities
- **Configuration Management**: Environment-based configuration with development and production settings
- **Static Asset Management**: Organized static files with dedicated directories for CSS, JavaScript, and uploads
- **Error Handling**: Comprehensive form validation and user feedback through flash messages

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **SQLAlchemy**: Database ORM and migrations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-Bcrypt**: Password hashing
- **Werkzeug**: Security utilities and file handling
- **Pillow**: Image processing and optimization

### Frontend Libraries
- **Bootstrap 5**: CSS framework delivered via CDN
- **Font Awesome**: Icon library delivered via CDN
- **jQuery**: JavaScript library (implied by Bootstrap usage)

### Database
- **SQLite**: Default database for development (configured via DATABASE_URL environment variable)
- **PostgreSQL**: Production-ready database option (configurable via environment variables)

### File Storage
- **Local File System**: Image uploads stored in static/uploads directory with automatic processing
- **Werkzeug Secure Filename**: File name sanitization for security

### Development Tools
- **Flask Debug Mode**: Development server with hot reloading
- **Logging**: Python logging module for debugging and monitoring
- **ProxyFix**: Werkzeug middleware for handling proxy headers in production