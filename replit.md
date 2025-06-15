# Kynetik Electric - Professional Electrical Contracting Platform

## Overview

Kynetik Electric is a comprehensive web application for a professional electrical contracting company, featuring AI-powered assistance, object detection capabilities, and integrated business management tools. The platform serves both customer-facing and internal operator needs with advanced features like 3D LiDAR scanning integration, Stripe payment processing, and intelligent bid request management.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5.3+ with custom CSS implementing official Kynetik Electric brand guidelines
- **Responsive Design**: Mobile-first approach with modern UI/UX
- **Brand Colors**: Official brand cyan (#00AEEF), medium grey (#777777), dark charcoal (#333333) per brand guidelines
- **Typography**: Orbitron font for headings, RethinkSans for body text following brand hierarchy
- **JavaScript**: Vanilla JS with Bootstrap components, custom chat widget for AI assistant
- **Templates**: Jinja2 templating engine with modular component structure

### Backend Architecture
- **Framework**: Flask 3.1+ with Python 3.11
- **Database**: SQLAlchemy ORM with PostgreSQL 16 (configured for autoscale deployment)
- **Session Management**: Flask-Login for admin authentication
- **File Handling**: Werkzeug for secure file uploads (16MB max)
- **Web Server**: Gunicorn with auto-reloading in development

### AI Integration
- **OpenAI API**: GPT-4o model for Toolie AI assistant
- **Computer Vision**: Custom YOLOv8-style object detection using OpenCV
- **Context Switching**: Dual-mode AI (customer-facing vs. solo-operator)

## Key Components

### 1. Toolie AI Assistant (`ai_assistant.py`, `yolo_detect.py`)
- **Purpose**: Intelligent chatbot providing electrical expertise and guidance
- **Modes**: Customer-facing (basic guidance) and operator mode (technical calculations)
- **Integration**: OpenAI GPT-4o with custom prompts for electrical domain knowledge
- **Object Detection**: Custom electrical component detection system mimicking YOLOv8

### 2. Business Management System
- **Bid Requests**: Comprehensive form system with file uploads and status tracking
- **Service Management**: Categorized service offerings with detailed descriptions
- **Admin Dashboard**: Complete CRUD operations for products, services, and bid management

### 3. E-commerce Platform (`stripe_integration.py`)
- **Payment Processing**: Stripe integration for both one-time and subscription payments
- **Product Types**: Digital downloads and physical products
- **Inventory Management**: Admin-controlled product catalog with pricing

### 4. Training & Content Hub
- **Video Training**: YouTube integration with premium content gating
- **Digital Store**: Professional forms, guides, and electrical resources
- **Content Management**: Admin-controlled content with access levels

### 5. Object Detection System
- **Component Recognition**: Electrical panels, conduit, junction boxes, wiring, etc.
- **Database Matching**: Detected components matched against parts database
- **Quote Generation**: Automatic bid request pre-filling based on detected components

## Data Flow

### 1. Customer Journey
```
Landing Page → Services → Bid Request → AI Assistance → File Upload → Admin Review → Quote
```

### 2. AI Assistant Flow
```
User Input → Context Detection → OpenAI API → Response Generation → UI Display
```

### 3. Object Detection Flow
```
Image Upload → OpenCV Processing → Component Detection → Database Matching → Results Display
```

### 4. Payment Flow
```
Product Selection → Stripe Checkout → Payment Processing → Digital Delivery/Order Fulfillment
```

## External Dependencies

### Core Dependencies
- **Flask Stack**: Flask, Flask-SQLAlchemy, Flask-WTF, Flask-Login
- **Database**: PostgreSQL with psycopg2-binary adapter
- **Payment**: Stripe API for payment processing
- **AI Services**: OpenAI API for GPT-4o model access
- **Computer Vision**: OpenCV for image processing and object detection
- **PDF Generation**: ReportLab for document creation
- **File Processing**: Pillow for image manipulation

### Development Tools
- **Package Management**: UV with pyproject.toml configuration
- **Web Server**: Gunicorn for production deployment
- **Form Handling**: WTForms with validation and file upload support

### Environment Configuration
- **Deployment**: Replit autoscale deployment target
- **Database**: PostgreSQL 16 with connection pooling
- **File Storage**: Local file system with configurable upload directory
- **SSL/Security**: ProxyFix middleware for secure headers

## Deployment Strategy

### Production Environment
- **Platform**: Replit autoscale deployment
- **Database**: PostgreSQL 16 with automated backups
- **File Uploads**: Persistent storage in `/static/uploads/`
- **Environment Variables**: Secure configuration for API keys and database URLs
- **Process Management**: Gunicorn with port binding and reload capabilities

### Security Measures
- **File Upload Validation**: Restricted file types and size limits
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Session Security**: Secure session management with configurable secrets

### Monitoring & Maintenance
- **Logging**: Python logging module with configurable levels
- **Error Handling**: Comprehensive exception handling and user feedback
- **Database Health**: Connection pool management with pre-ping validation

## Recent Changes

### June 15, 2025
- **Operator-Friendly Field Service Interface**: Complete redesign focused on usability for field technicians
  - Replaced complex dark theme with clean, bright interface using large buttons and clear text
  - Implemented essential field worker features: time tracking, emergency calls, parts lookup, issue reporting
  - Added GPS-enabled navigation directly to job sites with automatic location detection
  - Built one-tap customer calling and photo upload with camera integration
  - Created mobile-optimized layout with large touch targets for work gloves
  - Designed simple visual hierarchy that non-technical workers can understand instantly
- **Premium ServiceTitan-Style Field Service Interface**: Complete transformation into enterprise-grade field service management
  - Modern worker dashboard with glassmorphic job cards and color-coded status indicators (Blue=Open, Yellow=Urgent, Green=Complete, Purple=Progress)
  - Professional sidebar navigation with metrics dashboard showing completed jobs, hours worked, and earnings
  - Advanced job cards with progress steppers, location links, and inline photo/note management
  - Mobile-first responsive design with slide-in navigation and touch-optimized controls
  - Enhanced action buttons with loading states and smooth hover animations
  - Integrated file upload with drag-and-drop support and real-time preview thumbnails
  - Toolie AI chat bubble with contextual assistance and animated idle states
  - Professional Inter typography with modern spacing and visual hierarchy
  - Real-time job sync capabilities with automated status updates and SMS integration
- **Worker Dispatch System**: Implemented comprehensive service call management
  - Firebase Authentication integration for worker login system
  - Admin dashboard for creating and assigning service calls to workers
  - Worker dashboard for viewing assigned jobs, updating status, and uploading files
  - Twilio SMS notifications sent to workers when jobs are assigned
  - Mobile-responsive interface for field workers to use on phones
  - File upload system for job documentation and photos
  - Status tracking system (Open, In Progress, Completed, On Hold, Cancelled)
- **Brand Implementation**: Applied official Kynetik Electric brand guidelines
  - Updated color scheme to brand cyan (#00AEEF), medium grey (#777777), dark charcoal (#333333)
  - Implemented typography hierarchy with Orbitron for headings, RethinkSans for body text
  - Added official logo to navigation bar with proper sizing and positioning
  - Replaced placeholder fonts with brand-approved typefaces
- **Enhanced Object Detection**: Upgraded to YOLOv8-style detection system
  - Improved electrical component recognition accuracy
  - Added comprehensive parts database integration
  - Implemented mobile-friendly camera capture and file upload options
- **Complete Platform Features**: All major systems operational
  - Toolie AI assistant with dual-mode context switching
  - Stripe payment processing with digital and physical products
  - Training video hub with premium content gating
  - Professional bid request system with file upload capabilities

## User Preferences

Preferred communication style: Simple, everyday language.