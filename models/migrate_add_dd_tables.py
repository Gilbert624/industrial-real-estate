"""
Migration Script: Add Due Diligence (DD) Tables
Adds DD-related tables to existing database without affecting other tables

Developer: Gilbert - Brisbane, QLD
Usage:
    python -m models.migrate_add_dd_tables
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import (
    DatabaseManager, Base, 
    DDProject, DDScenario, DDAssumption, DDCashFlow
)


def migrate_add_dd_tables():
    """
    Add DD tables to existing database using SQLAlchemy
    This will only create tables that don't already exist
    """
    print("="*70)
    print("Migration: Adding Due Diligence Tables")
    print("="*70)
    
    # Initialize database manager
    db_manager = DatabaseManager('sqlite:///industrial_real_estate.db')
    
    print("\n🔨 Creating DD tables...")
    
    try:
        # Create only the DD tables using SQLAlchemy metadata
        # This will only create tables that don't exist
        DDProject.__table__.create(bind=db_manager.engine, checkfirst=True)
        DDScenario.__table__.create(bind=db_manager.engine, checkfirst=True)
        DDAssumption.__table__.create(bind=db_manager.engine, checkfirst=True)
        DDCashFlow.__table__.create(bind=db_manager.engine, checkfirst=True)
        
        print("✅ DD tables created successfully!")
        print("\nCreated tables:")
        print("  - dd_projects")
        print("  - dd_scenarios")
        print("  - dd_assumptions")
        print("  - dd_cashflows")
        
    except Exception as e:
        print(f"\n❌ Error creating DD tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*70)
    print("✨ Migration complete!")
    print("="*70)
    return True


if __name__ == "__main__":
    success = migrate_add_dd_tables()
    sys.exit(0 if success else 1)
