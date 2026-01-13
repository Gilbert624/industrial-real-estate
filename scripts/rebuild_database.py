"""
Rebuild Database with Market Intelligence Tables
强制重建数据库，包含所有市场情报表
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.database import (
    Base, 
    Asset, 
    Transaction, 
    Project, 
    DDProject,
    MarketIndicator,
    DevelopmentProject,
    RentalData,
    InfrastructureProject,
    CompetitorAnalysis,
    DatabaseManager
)
from sqlalchemy import create_engine, inspect

def rebuild_database(db_path='industrial_real_estate.db'):
    """重建数据库"""
    
    print("=" * 60)
    print("🔧 Database Rebuild Script")
    print("=" * 60)
    
    # 备份现有数据库
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        print(f"📦 Backing up existing database to: {backup_path}")
        import shutil
        shutil.copy(db_path, backup_path)
    
    # 创建新引擎
    engine = create_engine(f'sqlite:///{db_path}', echo=True)
    
    print("\n📝 Creating all tables...")
    
    # 删除所有现有表（可选，谨慎使用）
    # Base.metadata.drop_all(engine)
    
    # 创建所有表
    Base.metadata.create_all(engine)
    
    # 验证表创建
    print("\n✅ Verifying tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Created tables ({len(tables)}):")
    for table in sorted(tables):
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"   ✓ {table} ({len(columns)} columns)")
    
    # 检查必需的表
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
        print(f"\n⚠️  WARNING: Missing tables: {missing}")
        return False
    else:
        print(f"\n✅ All required tables present!")
    
    # 测试DatabaseManager
    print("\n🧪 Testing DatabaseManager...")
    db = DatabaseManager(db_path)
    
    # 检查方法
    methods_to_check = [
        'get_all_assets',
        'get_all_transactions',
        'get_all_projects',
        'get_development_projects',
        'get_rental_data',
        'get_competitor_analysis',
        'add_development_project',
        'add_rental_data',
        'add_competitor_analysis'
    ]
    
    print("\n📋 Checking DatabaseManager methods:")
    for method in methods_to_check:
        has_method = hasattr(db, method)
        status = "✅" if has_method else "❌"
        print(f"   {status} {method}")
        
        if not has_method:
            print(f"\n❌ ERROR: Method '{method}' not found!")
            return False
    
    print("\n" + "=" * 60)
    print("✅ Database rebuild complete!")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = rebuild_database()
    
    if success:
        print("\n✅ You can now restart your Streamlit app.")
    else:
        print("\n❌ Database rebuild failed. Please check errors above.")
    
    sys.exit(0 if success else 1)
