"""
Production Logging Configuration
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import streamlit as st

def setup_logging():
    """Setup production logging"""
    
    # Create logs directory if not exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Log file path
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Rotating file handler (10MB per file, keep 5 files)
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def log_error(error, context=""):
    """Log error with context"""
    logger = logging.getLogger(__name__)
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    # In production, don't show full error to user
    if os.getenv('APP_ENV') == 'production':
        st.error("❌ An error occurred. Please contact support if the issue persists.")
    else:
        st.error(f"❌ Error: {str(error)}")


def log_user_action(action, details=""):
    """Log user actions for audit trail"""
    logger = logging.getLogger(__name__)
    user_id = st.session_state.get('session_id', 'unknown')
    logger.info(f"User {user_id} - {action}: {details}")


def log_api_call(endpoint, cost=0, success=True):
    """Log API calls for monitoring"""
    logger = logging.getLogger(__name__)
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"API Call - {endpoint} - {status} - Cost: ${cost:.4f}")


# Initialize logging on module import
logger = setup_logging()
