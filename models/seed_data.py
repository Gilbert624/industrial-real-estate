"""
Database Testing Script
Test all database models and relationships

Usage: python test_database.py
"""

from models import (
    DatabaseManager, Asset, Project, Transaction, RentalIncome, DebtInstrument,
    AssetType, AssetStatus, ProjectStatus, TransactionType, ExpenseCategory, DebtType
)
from datetime import datetime, timedelta


def test_asset_creation(session):
    """Test creating and querying assets"""
    print("\n" + "="*70)
    print("TEST 1: Asset Creation and Queries")
    print("="*70)
    
    # Create test asset
    asset = Asset(
        name="Test Brisbane Warehouse",
        asset_type=AssetType.WAREHOUSE,
        status=AssetStatus.ACTIVE,
        address_line1="Test Street 123",
        suburb="Test Suburb",
        state="Queensland",
        postcode="4000",
        region="Brisbane",
        land_area_sqm=5000,
        building_area_sqm=4000
    )
    session.add(asset)
    session.commit()
    
    print(f"✅ Created: {asset}")
    
    # Query assets
    all_assets = session.query(Asset).all()
    print(f"📊 Total assets in database: {len(all_assets)}")
    
    brisbane_assets = session.query(Asset).filter_by(region="Brisbane").all()
    print(f"📊 Brisbane assets: {len(brisbane_assets)}")
    
    return asset


def test_project_relationships(session, asset):
    """Test project creation and relationships"""
    print("\n" + "="*70)
    print("TEST 2: Project Creation and Relationships")
    print("="*70)
    
    project = Project(
        asset_id=asset.id,
        project_name="Test Development Project",
        project_code="TEST-001",
        status=ProjectStatus.PLANNING,
        total_budget=1000000.00,
        actual_cost=250000.00,
        planned_start_date=datetime.now().date(),
        planned_completion_date=(datetime.now() + timedelta(days=180)).date()
    )
    session.add(project)
    session.commit()
    
    print(f"✅ Created: {project}")
    print(f"   Budget Variance: ${project.budget_variance:,.2f}")
    print(f"   Budget Utilization: {project.budget_utilization_percent:.1f}%")
    
    # Test relationship
    print(f"   Linked to Asset: {project.asset.name}")
    
    return project


def test_transactions(session, asset, project):
    """Test transaction recording"""
    print("\n" + "="*70)
    print("TEST 3: Transaction Recording")
    print("="*70)
    
    # Income transaction
    income = Transaction(
        asset_id=asset.id,
        transaction_date=datetime.now().date(),
        transaction_type=TransactionType.INCOME,
        amount=50000.00,
        gst_amount=5000.00,
        category="Rental Income",
        description="Test rental payment",
        vendor_payee="Test Tenant"
    )
    session.add(income)
    
    # Expense transaction
    expense = Transaction(
        asset_id=asset.id,
        project_id=project.id,
        transaction_date=datetime.now().date(),
        transaction_type=TransactionType.EXPENSE,
        amount=25000.00,
        gst_amount=2500.00,
        expense_category=ExpenseCategory.CONSTRUCTION,
        description="Test construction payment",
        vendor_payee="Test Contractor"
    )
    session.add(expense)
    session.commit()
    
    print(f"✅ Created income transaction: ${income.amount:,.2f}")
    print(f"   Amount including GST: ${income.amount_including_gst:,.2f}")
    print(f"✅ Created expense transaction: ${expense.amount:,.2f}")
    
    # Query transactions
    from sqlalchemy import func
    total_income = session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == TransactionType.INCOME
    ).scalar() or 0
    
    total_expense = session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == TransactionType.EXPENSE
    ).scalar() or 0
    
    print(f"\n📊 Total Income: ${total_income:,.2f}")
    print(f"📊 Total Expenses: ${total_expense:,.2f}")
    print(f"📊 Net: ${(total_income - total_expense):,.2f}")


def test_rental_income(session, asset):
    """Test rental income tracking"""
    print("\n" + "="*70)
    print("TEST 4: Rental Income Tracking")
    print("="*70)
    
    rental = RentalIncome(
        asset_id=asset.id,
        tenant_name="Test Tenant Pty Ltd",
        lease_start_date=datetime.now().date(),
        lease_end_date=(datetime.now() + timedelta(days=1095)).date(),  # 3 years
        lease_term_months=36,
        monthly_rent=40000.00,
        annual_rent=480000.00,
        rent_per_sqm=100.00,
        outgoings=5000.00,
        payment_frequency="Monthly",
        is_active=True,
        leased_area_sqm=4000.00
    )
    session.add(rental)
    session.commit()
    
    print(f"✅ Created: {rental}")
    print(f"   Monthly Rent: ${rental.monthly_rent:,.2f}")
    print(f"   Total Monthly Income: ${rental.total_monthly_income:,.2f}")
    print(f"   Remaining Lease Days: {rental.remaining_lease_days}")
    print(f"   Annual Income: ${rental.annual_rent:,.2f}")


def test_debt_instruments(session, asset):
    """Test debt tracking"""
    print("\n" + "="*70)
    print("TEST 5: Debt Instrument Tracking")
    print("="*70)
    
    debt = DebtInstrument(
        asset_id=asset.id,
        debt_name="Test Construction Loan",
        debt_type=DebtType.CONSTRUCTION_LOAN,
        loan_number="TEST-LOAN-001",
        lender_name="Test Bank",
        original_principal=3000000.00,
        current_principal=2750000.00,
        interest_rate=6.5,
        interest_type="Variable",
        loan_start_date=(datetime.now() - timedelta(days=90)).date(),
        maturity_date=(datetime.now() + timedelta(days=540)).date(),
        repayment_frequency="Monthly",
        monthly_payment=18000.00,
        ltv_ratio=60.0,
        is_active=True
    )
    session.add(debt)
    session.commit()
    
    print(f"✅ Created: {debt}")
    print(f"   Original Principal: ${debt.original_principal:,.2f}")
    print(f"   Current Principal: ${debt.current_principal:,.2f}")
    print(f"   Total Repaid: ${debt.total_repaid:,.2f}")
    print(f"   Annual Interest Cost: ${debt.annual_interest_cost:,.2f}")
    print(f"   Remaining Term: {debt.remaining_term_days} days")
    print(f"   LTV Ratio: {debt.ltv_ratio}%")


def test_complex_queries(session):
    """Test complex database queries"""
    print("\n" + "="*70)
    print("TEST 6: Complex Queries")
    print("="*70)
    
    # Assets with active leases
    leased_assets = session.query(Asset).join(RentalIncome).filter(
        RentalIncome.is_active == True
    ).all()
    print(f"📊 Assets with active leases: {len(leased_assets)}")
    
    # Active projects
    active_projects = session.query(Project).filter_by(is_active=True).all()
    print(f"📊 Active projects: {len(active_projects)}")
    
    # Total debt outstanding
    from sqlalchemy import func
    total_debt = session.query(func.sum(DebtInstrument.current_principal)).filter(
        DebtInstrument.is_active == True
    ).scalar() or 0
    print(f"📊 Total debt outstanding: ${total_debt:,.2f}")
    
    # Monthly rental income
    monthly_rental = session.query(func.sum(RentalIncome.monthly_rent)).filter(
        RentalIncome.is_active == True
    ).scalar() or 0
    print(f"📊 Total monthly rental income: ${monthly_rental:,.2f}")
    print(f"📊 Annual rental income: ${monthly_rental * 12:,.2f}")


def main():
    """Run all tests"""
    print("="*70)
    print("Industrial Real Estate Database - Testing Suite")
    print("="*70)
    
    # Initialize database
    db = DatabaseManager('sqlite:///test_database.db')
    
    # Clean slate
    print("\n🔨 Setting up test database...")
    db.drop_all_tables()
    db.create_all_tables()
    
    session = db.get_session()
    
    try:
        # Run tests
        asset = test_asset_creation(session)
        project = test_project_relationships(session, asset)
        test_transactions(session, asset, project)
        test_rental_income(session, asset)
        test_debt_instruments(session, asset)
        test_complex_queries(session)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nTest database created: test_database.db")
        print("You can now inspect the database with SQLite Browser")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ TEST FAILED: {e}")
        raise
    
    finally:
        db.close_session(session)


if __name__ == "__main__":
    main()