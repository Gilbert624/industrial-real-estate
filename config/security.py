"""
Security Configuration for Production Environment
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
import streamlit as st

class SecurityManager:
    """Manage security features for production"""
    
    def __init__(self):
        self.env = os.getenv('APP_ENV', 'development')
        self.is_production = self.env == 'production'
        
    def validate_api_key(self):
        """Validate that API key is properly configured"""
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        if not api_key or api_key == 'your_production_api_key_here':
            if self.is_production:
                st.error("⚠️ API key not configured properly for production!")
                st.stop()
            else:
                st.warning("⚠️ Using development API key")
        
        return api_key
    
    def check_file_upload_security(self, uploaded_file):
        """Validate uploaded file for security"""
        if uploaded_file is None:
            return True
        
        # Check file size
        max_size = int(os.getenv('MAX_UPLOAD_SIZE', 200)) * 1024 * 1024  # MB to bytes
        if uploaded_file.size > max_size:
            st.error(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
            return False
        
        # Check file type
        allowed_types = os.getenv('ALLOWED_FILE_TYPES', 'pdf,xlsx,docx,jpg,png').split(',')
        file_ext = uploaded_file.name.split('.')[-1].lower()
        
        if file_ext not in allowed_types:
            st.error(f"File type not allowed. Allowed types: {', '.join(allowed_types)}")
            return False
        
        return True
    
    def sanitize_filename(self, filename):
        """Sanitize filename to prevent path traversal"""
        import re
        # Remove any path separators and special characters
        safe_name = re.sub(r'[^\w\s.-]', '', filename)
        safe_name = safe_name.replace('..', '')
        return safe_name
    
    def generate_session_id(self):
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    def hash_sensitive_data(self, data):
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def check_rate_limit(self, action_type, limit_per_hour=100):
        """Simple rate limiting"""
        if f'rate_limit_{action_type}' not in st.session_state:
            st.session_state[f'rate_limit_{action_type}'] = {
                'count': 0,
                'reset_time': datetime.now() + timedelta(hours=1)
            }
        
        rate_data = st.session_state[f'rate_limit_{action_type}']
        
        # Reset if time expired
        if datetime.now() > rate_data['reset_time']:
            rate_data['count'] = 0
            rate_data['reset_time'] = datetime.now() + timedelta(hours=1)
        
        # Check limit
        if rate_data['count'] >= limit_per_hour:
            return False
        
        rate_data['count'] += 1
        return True
    
    def mask_sensitive_data(self, text, visible_chars=4):
        """Mask sensitive data for display"""
        if len(text) <= visible_chars:
            return '*' * len(text)
        return text[:visible_chars] + '*' * (len(text) - visible_chars)
    
    def get_security_headers(self):
        """Get security headers for production"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        }


# Singleton instance
_security_manager = None

def get_security_manager():
    """Get or create security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def require_production_check():
    """Decorator to require production environment checks"""
    security = get_security_manager()
    if security.is_production:
        security.validate_api_key()
