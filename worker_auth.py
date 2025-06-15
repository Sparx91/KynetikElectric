"""
Worker authentication system for Kynetik Electric
"""
import os
import functools
from flask import session, redirect, url_for, request, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Admin


class Worker(UserMixin):
    """Worker user class for authentication"""
    
    def __init__(self, worker_data):
        self.id = worker_data['id']
        self.name = worker_data['name']
        self.email = worker_data['email']
        self.phone = worker_data.get('phone', '')
        self.role = worker_data.get('role', 'technician')
        self.active = worker_data.get('active', True)
    
    def get_id(self):
        return self.id
    
    def is_admin(self):
        return self.role in ['admin', 'supervisor']
    
    def is_worker(self):
        return self.role in ['technician', 'senior_technician', 'apprentice']


def admin_required(f):
    """Decorator to require admin access"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('worker_login'))
        
        # Check if it's an admin user from the existing admin system
        if hasattr(current_user, 'username'):
            return f(*args, **kwargs)
        
        # Check if it's a worker with admin role
        if hasattr(current_user, 'role') and current_user.is_admin():
            return f(*args, **kwargs)
        
        flash('Admin access required.', 'error')
        return redirect(url_for('worker_dashboard'))
    
    return decorated_function


def worker_required(f):
    """Decorator to require worker access"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('worker_login'))
        return f(*args, **kwargs)
    
    return decorated_function


def authenticate_worker(email, password):
    """Authenticate worker with email/password"""
    # Normalize email to lowercase for consistent lookup
    email = email.strip().lower()
    
    # For now, use simple hardcoded authentication
    # In production, this would validate against Firebase Auth
    workers = {
        'mike@kynetikelectric.com': {
            'id': 'worker1',
            'name': 'Mike Rodriguez',
            'email': 'mike@kynetikelectric.com',
            'phone': '+15551234567',
            'role': 'technician',
            'password_hash': generate_password_hash('worker123'),
            'active': True
        },
        'sarah@kynetikelectric.com': {
            'id': 'worker2',
            'name': 'Sarah Johnson',
            'email': 'sarah@kynetikelectric.com',
            'phone': '+15551234568',
            'role': 'senior_technician',
            'password_hash': generate_password_hash('worker123'),
            'active': True
        },
        'admin@kynetikelectric.com': {
            'id': 'admin1',
            'name': 'Admin User',
            'email': 'admin@kynetikelectric.com',
            'phone': '+15551234569',
            'role': 'admin',
            'password_hash': generate_password_hash('admin123'),
            'active': True
        }
    }
    
    print(f"[DEBUG] Authenticating user: {email}")
    print(f"[DEBUG] Available workers: {list(workers.keys())}")
    
    worker_data = workers.get(email)
    if worker_data and worker_data['active']:
        print(f"[DEBUG] Found worker data for: {email}")
        if check_password_hash(worker_data['password_hash'], password):
            print(f"[DEBUG] Password verification successful for: {email}")
            return Worker(worker_data)
        else:
            print(f"[DEBUG] Password verification failed for: {email}")
    else:
        print(f"[DEBUG] No worker data found for: {email}")
    
    return None


def get_current_worker():
    """Get current authenticated worker"""
    if current_user.is_authenticated and hasattr(current_user, 'role'):
        return current_user
    return None