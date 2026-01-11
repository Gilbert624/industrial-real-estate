#!/usr/bin/env python3
"""
Project Structure Diagnostic Tool
Checks your project structure and identifies issues

Developer: Gilbert - Brisbane, QLD
Usage: python diagnose.py
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(text)
    print("="*70)


def check_directory_structure():
    """Check and display directory structure"""
    print_header("DIRECTORY STRUCTURE CHECK")
    
    current_dir = Path.cwd()
    print(f"\n📂 Current directory: {current_dir}")
    
    # Check for models directory
    models_dir = current_dir / 'models'
    if models_dir.exists() and models_dir.is_dir():
        print(f"✅ models/ directory exists")
        
        # List contents
        print(f"\n📁 Contents of models/:")
        try:
            for item in sorted(models_dir.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    print(f"   📄 {item.name} ({size:,} bytes)")
                elif item.is_dir():
                    print(f"   📁 {item.name}/")
        except Exception as e:
            print(f"   ❌ Error listing directory: {e}")
    else:
        print(f"❌ models/ directory NOT FOUND")
        return False
    
    return True


def check_required_files():
    """Check for required Python files"""
    print_header("REQUIRED FILES CHECK")
    
    current_dir = Path.cwd()
    
    required_files = {
        'models/__init__.py': 'Package initialization file',
        'models/database.py': 'Core database models',
        'models/init_db.py': 'Database initialization script'
    }
    
    all_present = True
    
    for file_path, description in required_files.items():
        full_path = current_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path}")
            print(f"   Size: {size:,} bytes")
            print(f"   Description: {description}")
            
            # Check if file is empty
            if size == 0:
                print(f"   ⚠️  WARNING: File is EMPTY!")
                all_present = False
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_present = False
        print()
    
    return all_present


def check_init_file():
    """Check the models/__init__.py file content"""
    print_header("models/__init__.py CONTENT CHECK")
    
    init_file = Path.cwd() / 'models' / '__init__.py'
    
    if not init_file.exists():
        print("❌ models/__init__.py does NOT exist")
        return False
    
    # Read content
    try:
        with open(init_file, 'r') as f:
            content = f.read()
        
        if not content.strip():
            print("❌ models/__init__.py is EMPTY")
            print("\nThis is the problem! The file needs content.")
            return False
        
        print(f"✅ File exists and has content ({len(content)} characters)")
        
        # Check for key imports
        required_imports = ['Asset', 'DatabaseManager', 'Project', 'Transaction']
        missing_imports = []
        
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"\n⚠️  Missing imports: {', '.join(missing_imports)}")
        else:
            print(f"✅ All required imports present")
        
        # Show first few lines
        lines = content.split('\n')[:10]
        print("\n📄 First 10 lines:")
        for i, line in enumerate(lines, 1):
            print(f"   {i:2d}: {line}")
        
        return len(missing_imports) == 0
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def check_database_file():
    """Check the database.py file"""
    print_header("models/database.py CHECK")
    
    db_file = Path.cwd() / 'models' / 'database.py'
    
    if not db_file.exists():
        print("❌ models/database.py does NOT exist")
        return False
    
    size = db_file.stat().st_size
    print(f"✅ File exists ({size:,} bytes)")
    
    # Check if it has expected classes
    try:
        with open(db_file, 'r') as f:
            content = f.read()
        
        expected_classes = ['class Asset', 'class Project', 'class Transaction', 
                          'class DatabaseManager', 'class RentalIncome', 'class DebtInstrument']
        
        found_classes = []
        for cls in expected_classes:
            if cls in content:
                found_classes.append(cls.replace('class ', ''))
        
        print(f"\n✅ Found {len(found_classes)} of {len(expected_classes)} expected classes:")
        for cls in found_classes:
            print(f"   - {cls}")
        
        return len(found_classes) == len(expected_classes)
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def try_import():
    """Try to import the models"""
    print_header("IMPORT TEST")
    
    print("Attempting to import models...\n")
    
    try:
        # Try importing the package
        import models
        print(f"✅ Successfully imported 'models' package")
        print(f"   Package location: {models.__file__ if hasattr(models, '__file__') else 'unknown'}")
        
        # Check what's available
        available = dir(models)
        print(f"\n   Available attributes: {len(available)}")
        
        # Try importing specific classes
        classes_to_import = ['Asset', 'DatabaseManager', 'Project', 'Transaction']
        
        for cls_name in classes_to_import:
            try:
                cls = getattr(models, cls_name)
                print(f"   ✅ {cls_name}: {cls}")
            except AttributeError:
                print(f"   ❌ {cls_name}: NOT FOUND")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_python_path():
    """Check Python path"""
    print_header("PYTHON PATH CHECK")
    
    print("Python sys.path entries:\n")
    for i, path in enumerate(sys.path, 1):
        print(f"{i:2d}. {path}")
    
    current_dir = Path.cwd()
    if str(current_dir) in sys.path:
        print(f"\n✅ Current directory is in sys.path")
    else:
        print(f"\n⚠️  Current directory is NOT in sys.path")


def generate_fix():
    """Generate a fix based on findings"""
    print_header("RECOMMENDED FIX")
    
    current_dir = Path.cwd()
    init_file = current_dir / 'models' / '__init__.py'
    
    # Check if __init__.py is empty or missing
    if not init_file.exists() or init_file.stat().st_size == 0:
        print("\n🔧 The problem is models/__init__.py is empty or missing!")
        print("\nCreating a proper __init__.py file...")
        
        init_content = '''"""
Models Package for Industrial Real Estate Asset Management System
"""

from .database import (
    Base,
    Asset,
    Project,
    Transaction,
    RentalIncome,
    DebtInstrument,
    DatabaseManager,
    AssetType,
    AssetStatus,
    ProjectStatus,
    TransactionType,
    ExpenseCategory,
    DebtType
)

__all__ = [
    'Base',
    'Asset',
    'Project',
    'Transaction',
    'RentalIncome',
    'DebtInstrument',
    'DatabaseManager',
    'AssetType',
    'AssetStatus',
    'ProjectStatus',
    'TransactionType',
    'ExpenseCategory',
    'DebtType'
]
'''
        
        try:
            with open(init_file, 'w') as f:
                f.write(init_content)
            print(f"✅ Created models/__init__.py")
            print(f"\nNow try running:")
            print(f'   python -c "from models import Asset; print(\'Success!\')"')
            return True
        except Exception as e:
            print(f"❌ Error creating file: {e}")
            return False
    
    else:
        print("\n📋 Manual steps to fix:")
        print("\n1. Check that models/database.py exists and has content")
        print("2. Ensure models/__init__.py imports from .database")
        print("3. Try running: python -m models.init_db --sample")
    
    return False


def main():
    """Main diagnostic function"""
    
    print("="*70)
    print("Industrial Real Estate Asset Management System")
    print("Project Structure Diagnostic Tool")
    print("="*70)
    print(f"\nPython version: {sys.version}")
    print(f"Current working directory: {Path.cwd()}")
    
    # Run checks
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("__init__.py Content", check_init_file),
        ("database.py Content", check_database_file),
        ("Python Path", check_python_path),
        ("Import Test", try_import),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error during {name}: {e}")
            results[name] = False
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks\n")
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    # Generate fix if needed
    if not all(results.values()):
        generate_fix()
    else:
        print("\n✅ All checks passed! Your project structure is correct.")
        print("\nYou can now run:")
        print("   python -m models.init_db --sample")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
