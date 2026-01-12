"""
Database Backup Script
Run this daily via cron job or scheduler
"""

import os
import shutil
from datetime import datetime
import sqlite3
import gzip

def backup_database():
    """Backup SQLite database with compression"""
    
    # Database file
    db_file = 'industrial_real_estate.db'
    
    # Check if production database exists
    prod_db = 'production_data.db'
    if os.path.exists(prod_db):
        db_file = prod_db
    
    if not os.path.exists(db_file):
        print(f"Database file {db_file} not found!")
        return False
    
    # Create backup directory
    backup_dir = os.getenv('BACKUP_PATH', 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')
    compressed_file = f'{backup_file}.gz'
    
    try:
        # Copy database file
        print(f"Backing up {db_file}...")
        shutil.copy2(db_file, backup_file)
        
        # Compress backup
        print("Compressing backup...")
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed backup
        os.remove(backup_file)
        
        # Get file size
        size_mb = os.path.getsize(compressed_file) / (1024 * 1024)
        print(f"✅ Backup created: {compressed_file} ({size_mb:.2f} MB)")
        
        # Clean old backups (keep last 30 days)
        cleanup_old_backups(backup_dir, days=30)
        
        return True
    
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


def cleanup_old_backups(backup_dir, days=30):
    """Remove backups older than specified days"""
    import time
    
    now = time.time()
    cutoff = now - (days * 86400)  # days to seconds
    
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                print(f"Removed old backup: {filename}")


def restore_database(backup_file):
    """Restore database from backup"""
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    try:
        # Decompress if needed
        if backup_file.endswith('.gz'):
            print("Decompressing backup...")
            temp_file = backup_file.replace('.gz', '')
            with gzip.open(backup_file, 'rb') as f_in:
                with open(temp_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            backup_file = temp_file
        
        # Restore database
        db_file = 'industrial_real_estate.db'
        print(f"Restoring to {db_file}...")
        shutil.copy2(backup_file, db_file)
        
        print("✅ Database restored successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) > 2:
            restore_database(sys.argv[2])
        else:
            print("Usage: python backup.py restore <backup_file>")
    else:
        backup_database()
