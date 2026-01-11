#!/usr/bin/env python3
"""
Test script for the new financial query methods in DatabaseManager
"""

from models.database import DatabaseManager
from datetime import datetime

def test_financial_methods():
    """Test all new financial query methods"""
    print("=" * 70)
    print("Testing Financial Query Methods")
    print("=" * 70)
    
    db = DatabaseManager()
    
    # Test 1: get_cash_balance()
    print("\n1. Testing get_cash_balance()...")
    try:
        balance = db.get_cash_balance()
        print(f"   ✓ Cash Balance: ${balance:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: get_monthly_income()
    print("\n2. Testing get_monthly_income()...")
    try:
        now = datetime.now()
        income = db.get_monthly_income(now.year, now.month)
        print(f"   ✓ This Month Income ({now.year}-{now.month:02d}): ${income:,.2f}")
        
        # Test previous month
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
        income_prev = db.get_monthly_income(prev_year, prev_month)
        print(f"   ✓ Previous Month Income ({prev_year}-{prev_month:02d}): ${income_prev:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: get_monthly_expense()
    print("\n3. Testing get_monthly_expense()...")
    try:
        now = datetime.now()
        expense = db.get_monthly_expense(now.year, now.month)
        print(f"   ✓ This Month Expense ({now.year}-{now.month:02d}): ${expense:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: get_cashflow_trend()
    print("\n4. Testing get_cashflow_trend()...")
    try:
        trend = db.get_cashflow_trend(months=6)
        print(f"   ✓ Cashflow Trend (last 6 months):")
        for month_data in trend:
            year = month_data['year']
            month = month_data['month']
            income = month_data['income']
            expense = month_data['expense']
            net = month_data['net']
            print(f"      {year}-{month:02d}: Income=${income:,.2f}, Expense=${expense:,.2f}, Net=${net:,.2f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: get_recent_transactions()
    print("\n5. Testing get_recent_transactions()...")
    try:
        transactions = db.get_recent_transactions(limit=10)
        print(f"   ✓ Recent Transactions (last {len(transactions)}):")
        for trans in transactions:
            print(f"      {trans.transaction_date} - {trans.transaction_type.value}: ${trans.amount:,.2f} - {trans.description[:50]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_financial_methods()