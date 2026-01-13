"""
Database Migration Script
迁移数据库表结构以匹配最新的模型定义
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.database import DatabaseManager, Base
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError

def migrate_database(db_path='industrial_real_estate.db'):
    """迁移数据库表结构"""
    
    print("=" * 60)
    print("🔧 Database Migration Script")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("   Creating new database...")
        db = DatabaseManager(db_path)
        Base.metadata.create_all(db.engine)
        print("✅ New database created with all tables")
        return True
    
    # 创建引擎
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    inspector = inspect(engine)
    
    print(f"\n📊 Current database: {db_path}")
    print(f"   Tables: {len(inspector.get_table_names())}")
    
    # 检查并添加缺失的列
    print("\n🔍 Checking table structure...")
    
    with engine.connect() as conn:
        # 检查 assets 表
        if 'assets' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('assets')]
            print(f"\n   assets 表列: {columns}")
            
            # 检查 address 列
            if 'address' not in columns:
                print("   ⚠️  缺少 address 列，正在添加...")
                try:
                    conn.execute(text("ALTER TABLE assets ADD COLUMN address TEXT"))
                    conn.commit()
                    print("   ✅ address 列已添加")
                except Exception as e:
                    print(f"   ❌ 添加 address 列失败: {e}")
                    return False
            
            # 检查其他可能缺失的列
            required_columns = {
                'name': 'TEXT NOT NULL',
                'asset_type': 'TEXT',
                'region': 'TEXT',
                'land_area_sqm': 'REAL',
                'building_area_sqm': 'REAL',
                'current_valuation': 'REAL',
                'acquisition_date': 'DATETIME',
                'status': 'TEXT',
                'notes': 'TEXT',
                'created_at': 'DATETIME',
                'updated_at': 'DATETIME'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    print(f"   ⚠️  缺少 {col_name} 列，正在添加...")
                    try:
                        conn.execute(text(f"ALTER TABLE assets ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        print(f"   ✅ {col_name} 列已添加")
                    except Exception as e:
                        print(f"   ⚠️  添加 {col_name} 列失败（可能已存在）: {e}")
        
        # 确保所有表都存在
        print("\n📝 Creating missing tables...")
        Base.metadata.create_all(engine)
        
        # 验证所有表
        print("\n✅ Verifying tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'assets',
            'transactions',
            'projects',
            'dd_projects',
            'market_indicators',
            'development_projects',
            'rental_data',
            'infrastructure_projects',
            'competitor_analysis'
        ]
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"   ⚠️  缺失的表: {missing}")
            print("   正在创建...")
            Base.metadata.create_all(engine)
        else:
            print(f"   ✅ 所有必需的表都存在 ({len(tables)} 个表)")
    
    print("\n" + "=" * 60)
    print("✅ Database migration complete!")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database schema')
    parser.add_argument('--db', type=str, default='industrial_real_estate.db',
                       help='Database file path (default: industrial_real_estate.db)')
    
    args = parser.parse_args()
    
    success = migrate_database(args.db)
    
    if success:
        print("\n✅ Migration successful! You can now restart your Streamlit app.")
    else:
        print("\n❌ Migration failed. Please check errors above.")
    
    sys.exit(0 if success else 1)
