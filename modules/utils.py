"""Utility functions for pharmacy management system"""
import hashlib
from datetime import datetime
import re

def hash_password(password):
    """Hash a password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify a password"""
    return hash_password(password) == hashed

def format_currency(amount):
    """Format amount as currency"""
    return f"Rs {amount:,.2f}"

def format_date(date_obj):
    """Format date"""
    if date_obj:
        return datetime.strptime(str(date_obj), '%Y-%m-%d').strftime('%B %d, %Y')
    return "N/A"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')) is not None

def calculate_profit_margin(selling_price, cost_price):
    """Calculate profit margin percentage"""
    if cost_price == 0:
        return 0
    return ((selling_price - cost_price) / cost_price) * 100

def generate_report_filename(report_type):
    """Generate report filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{report_type}_{timestamp}.csv"
