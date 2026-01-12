"""
Performance Optimization Utilities
"""

import streamlit as st
import time
from functools import wraps
import psutil
import os

class PerformanceMonitor:
    """Monitor and optimize application performance"""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def cached_database_query(query_func, *args, **kwargs):
        """Cache database queries for 1 hour"""
        return query_func(*args, **kwargs)
    
    @staticmethod
    @st.cache_resource
    def load_heavy_resources():
        """Cache heavy resources like models"""
        # This is loaded once and reused
        pass
    
    @staticmethod
    def measure_time(func):
        """Decorator to measure function execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            if os.getenv('DEBUG') == 'True':
                st.sidebar.caption(f"⏱️ {func.__name__}: {end-start:.2f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def get_system_stats():
        """Get system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    @staticmethod
    def optimize_dataframe(df, max_rows=1000):
        """Optimize DataFrame for display"""
        if len(df) > max_rows:
            st.info(f"📊 Showing first {max_rows} rows of {len(df)} total")
            return df.head(max_rows)
        return df
    
    @staticmethod
    def lazy_load_images(image_list, batch_size=10):
        """Lazy load images in batches"""
        for i in range(0, len(image_list), batch_size):
            batch = image_list[i:i+batch_size]
            yield batch


def enable_performance_monitoring():
    """Enable performance monitoring in sidebar"""
    if os.getenv('DEBUG') == 'True':
        with st.sidebar:
            with st.expander("📊 Performance Stats", expanded=False):
                monitor = PerformanceMonitor()
                stats = monitor.get_system_stats()
                
                st.metric("CPU Usage", f"{stats['cpu_percent']:.1f}%")
                st.metric("Memory Usage", f"{stats['memory_percent']:.1f}%")
                st.metric("Disk Usage", f"{stats['disk_percent']:.1f}%")
