#!/usr/bin/env python3
"""Test Projects database methods"""

from models.database import DatabaseManager
from datetime import datetime, timedelta

print("🧪 Testing Projects database methods...\n")

db = DatabaseManager()

# Test 1: Get all projects
try:
    projects = db.get_all_projects()
    print(f"✓ get_all_projects: {len(projects)} projects found")
except Exception as e:
    print(f"✗ get_all_projects failed: {e}")

# Test 2: Add test project
try:
    test_project = {
        "name": "Brisbane South Warehouse Development",
        "status": "Construction",
        "project_type": "New Development",
        "budget": 6000000.0,
        "actual_cost": 3500000.0,
        "start_date": datetime.now() - timedelta(days=120),
        "expected_completion": datetime.now() + timedelta(days=60),
        "completion_percentage": 65,
        "location": "Brisbane South",
        "land_area_sqm": 5000.0,
        "building_area_sqm": 3500.0,
        "estimated_value": 9000000.0,
        "description": "Modern industrial warehouse with office space"
    }
    
    new_project = db.add_project(test_project)
    print(f"✓ add_project: Created '{new_project.name}' (ID: {new_project.id})")
    test_id = new_project.id
except Exception as e:
    print(f"✗ add_project failed: {e}")
    test_id = None

# Test 3: Get active projects count
try:
    active = db.get_active_projects_count()
    print(f"✓ get_active_projects_count: {active} active projects")
except Exception as e:
    print(f"✗ get_active_projects_count failed: {e}")

# Test 4: Get project cost summary
if test_id:
    try:
        summary = db.get_project_cost_summary(test_id)
        print(f"✓ get_project_cost_summary:")
        print(f"  Total spent: ${summary.get('total_spent', 0):,.0f}")
        print(f"  Budget: ${summary.get('budget', 0):,.0f}")
        print(f"  Variance: ${summary.get('variance', 0):,.0f}")
    except Exception as e:
        print(f"✗ get_project_cost_summary failed: {e}")

# Test 5: Get by status
try:
    construction = db.get_projects_by_status("Construction")
    print(f"✓ get_projects_by_status: {len(construction)} projects in construction")
except Exception as e:
    print(f"✗ get_projects_by_status failed: {e}")

# Test 6: Get total budget
try:
    total_budget = db.get_total_projects_budget()
    print(f"✓ get_total_projects_budget: ${total_budget:,.0f}")
except Exception as e:
    print(f"✗ get_total_projects_budget failed: {e}")

# Test 7: Get total cost
try:
    total_cost = db.get_total_projects_cost()
    print(f"✓ get_total_projects_cost: ${total_cost:,.0f}")
except Exception as e:
    print(f"✗ get_total_projects_cost failed: {e}")

# Test 8: Get average completion
try:
    avg_completion = db.get_average_completion()
    print(f"✓ get_average_completion: {avg_completion:.1f}%")
except Exception as e:
    print(f"✗ get_average_completion failed: {e}")

# Test 9: Update project
if test_id:
    try:
        update_data = {
            "completion_percentage": 75,
            "actual_cost": 4000000.0
        }
        updated = db.update_project(test_id, update_data)
        if updated:
            print(f"✓ update_project: Updated to {updated.completion_percentage}% complete")
        else:
            print(f"✗ update_project: Project not found")
    except Exception as e:
        print(f"✗ update_project failed: {e}")

# Test 10: Get project by ID
if test_id:
    try:
        project = db.get_project_by_id(test_id)
        if project:
            print(f"✓ get_project_by_id: Found '{project.name}'")
        else:
            print(f"✗ get_project_by_id: Project not found")
    except Exception as e:
        print(f"✗ get_project_by_id failed: {e}")

print("\n" + "="*50)
print("✅ All tests completed!")
print("="*50)