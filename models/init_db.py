"""
Database Initialization Script
Creates database tables and optionally adds sample data for testing

Developer: Gilbert - Brisbane, QLD
Usage:
    python -m models.init_db              # Create tables only
    python -m models.init_db --sample     # Create tables and add sample data
    python -m models.init_db --reset      # Drop and recreate all tables (CAUTION!)
"""

import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import (
    DatabaseManager, Asset, Project, Transaction, RentalIncome, DebtInstrument,
    AssetType, AssetStatus, ProjectStatus, TransactionType, ExpenseCategory, DebtType
)


def create_database_tables(db_manager):
    """
    Create all database tables
    
    Args:
        db_manager: DatabaseManager instance
    """
    print("\n🔨 Creating database tables...")
    db_manager.create_all_tables()
    print("✅ All tables created successfully!")


def drop_all_tables(db_manager):
    """
    Drop all database tables (use with caution!)
    
    Args:
        db_manager: DatabaseManager instance
    """
    print("\n⚠️  Dropping all tables...")
    db_manager.drop_all_tables()
    print("✅ All tables dropped!")


def create_brisbane_warehouse(session):
    """
    Create Brisbane operational warehouse with rental income
    
    Returns:
        Asset: The created warehouse asset
    """
    print("\n📦 Creating Brisbane Logistics Hub (Operational Warehouse)...")
    
    # Create warehouse asset
    warehouse = Asset(
        name="Brisbane Logistics Hub",
        asset_type=AssetType.WAREHOUSE,
        status=AssetStatus.LEASED,
        address_line1="45 Gateway Drive",
        suburb="Eagle Farm",
        state="Queensland",
        postcode="4009",
        region="Brisbane",
        land_area_sqm=6000,
        building_area_sqm=5000,
        warehouse_area_sqm=4500,
        office_area_sqm=500,
        clear_height_meters=10.0,
        power_capacity_kva=600,
        loading_docks=6,
        car_parking_spaces=30,
        purchase_price=6500000.00,
        purchase_date=(datetime.now() - timedelta(days=730)).date(),
        current_valuation=7200000.00,
        valuation_date=datetime.now().date(),
        zoning="Industrial 1",
        council="Brisbane City Council",
        description="Modern A-grade warehouse with excellent highway access and full tenancy"
    )
    session.add(warehouse)
    session.flush()  # Get the ID
    
    # Create rental income for this warehouse
    rental = RentalIncome(
        asset_id=warehouse.id,
        tenant_name="XYZ Logistics Pty Ltd",
        tenant_abn="12 345 678 901",
        tenant_contact="contact@xyzlogistics.com.au",
        lease_start_date=(datetime.now() - timedelta(days=365)).date(),
        lease_end_date=(datetime.now() + timedelta(days=1095)).date(),  # 3 years remaining
        lease_term_months=60,
        monthly_rent=45000.00,
        annual_rent=540000.00,
        rent_per_sqm=108.00,
        outgoings=5000.00,
        gst_amount=5000.00,
        payment_frequency="Monthly",
        payment_day=1,
        payment_method="Direct Deposit",
        rent_review_date=(datetime.now() + timedelta(days=365)).date(),
        rent_increase_percent=3.0,
        rent_increase_type="Fixed",
        bond_amount=90000.00,
        is_active=True,
        lease_status="Active",
        leased_area_sqm=5000.00,
        lease_type="Triple Net"
    )
    session.add(rental)
    
    # Create rental income transactions (last 6 months)
    for i in range(6):
        trans_date = datetime.now() - timedelta(days=30 * i)
        transaction = Transaction(
            asset_id=warehouse.id,
            transaction_date=trans_date.date(),
            transaction_type=TransactionType.INCOME,
            amount=45000.00,
            gst_amount=4500.00,
            category="Rental Income",
            description=f"Monthly rent - {trans_date.strftime('%B %Y')} - XYZ Logistics",
            reference_number=f"INV-{trans_date.strftime('%Y-%m')}-001",
            vendor_payee="XYZ Logistics Pty Ltd",
            payment_method="Bank Transfer",
            is_reconciled=True,
            reconciliation_date=(trans_date + timedelta(days=2)).date()
        )
        session.add(transaction)
    
    # Add some expense transactions
    expenses = [
        {
            "days_ago": 20,
            "amount": 2500.00,
            "category": ExpenseCategory.MAINTENANCE,
            "description": "Roof maintenance and gutter cleaning",
            "vendor": "Industrial Maintenance Services"
        },
        {
            "days_ago": 45,
            "amount": 1800.00,
            "category": ExpenseCategory.UTILITIES,
            "description": "Electricity bill - December 2024",
            "vendor": "Energex"
        },
        {
            "days_ago": 90,
            "amount": 12500.00,
            "category": ExpenseCategory.INSURANCE,
            "description": "Annual building insurance premium",
            "vendor": "QBE Insurance"
        }
    ]
    
    for expense in expenses:
        transaction = Transaction(
            asset_id=warehouse.id,
            transaction_date=(datetime.now() - timedelta(days=expense["days_ago"])).date(),
            transaction_type=TransactionType.EXPENSE,
            amount=expense["amount"],
            gst_amount=expense["amount"] * 0.1,
            expense_category=expense["category"],
            description=expense["description"],
            vendor_payee=expense["vendor"],
            payment_method="Bank Transfer",
            is_reconciled=True
        )
        session.add(transaction)
    
    print(f"  ✅ Created: {warehouse.name}")
    print(f"     - Rental Income: ${rental.monthly_rent:,.2f}/month")
    print(f"     - 6 months of rental transactions")
    print(f"     - 3 expense transactions")
    
    return warehouse


def create_sunshine_coast_project(session):
    """
    Create Sunshine Coast construction project
    
    Returns:
        tuple: (Asset, Project) - The created asset and project
    """
    print("\n🏗️  Creating Sunshine Coast Warehouse Development (Under Construction)...")
    
    # Create land asset
    land = Asset(
        name="Sunshine Coast Industrial Estate",
        asset_type=AssetType.LAND,
        status=AssetStatus.UNDER_DEVELOPMENT,
        address_line1="Lot 15 Progress Road",
        suburb="Kawana",
        state="Queensland",
        postcode="4556",
        region="Sunshine Coast",
        land_area_sqm=12000,
        purchase_price=3200000.00,
        purchase_date=(datetime.now() - timedelta(days=180)).date(),
        current_valuation=3500000.00,
        valuation_date=datetime.now().date(),
        zoning="Industrial 2",
        council="Sunshine Coast Council",
        description="Prime industrial land under development - 4200sqm warehouse construction in progress"
    )
    session.add(land)
    session.flush()
    
    # Create development project
    project = Project(
        asset_id=land.id,
        project_name="Sunshine Coast Warehouse Construction",
        project_code="SC-WH-2024-001",
        status=ProjectStatus.CONSTRUCTION,
        description="New 4200sqm warehouse with modern specifications and 750kVA power",
        scope_of_work="Design and construct warehouse facility including civil works, building, electrical services, and landscaping",
        planned_start_date=(datetime.now() - timedelta(days=90)).date(),
        actual_start_date=(datetime.now() - timedelta(days=85)).date(),
        planned_completion_date=(datetime.now() + timedelta(days=180)).date(),
        total_budget=4500000.00,
        actual_cost=1850000.00,
        contingency_budget=225000.00,
        project_manager="Sarah Chen",
        contractor="ABC Construction Pty Ltd",
        architect="Design Partners Architecture",
        engineer="Structural Solutions QLD",
        da_number="DA-2024-0456",
        da_approval_date=(datetime.now() - timedelta(days=120)).date(),
        building_approval_date=(datetime.now() - timedelta(days=95)).date(),
        is_active=True
    )
    session.add(project)
    session.flush()
    
    # Create construction expense transactions
    construction_costs = [
        {
            "days_ago": 85,
            "amount": 320000.00,
            "description": "Site preparation and civil works",
            "reference": "PC-001"
        },
        {
            "days_ago": 70,
            "amount": 450000.00,
            "description": "Foundation and slab construction",
            "reference": "PC-002"
        },
        {
            "days_ago": 50,
            "amount": 580000.00,
            "description": "Structural steel and roof frame",
            "reference": "PC-003"
        },
        {
            "days_ago": 30,
            "amount": 320000.00,
            "description": "Wall cladding and insulation",
            "reference": "PC-004"
        },
        {
            "days_ago": 15,
            "amount": 180000.00,
            "description": "Electrical rough-in and power infrastructure",
            "reference": "PC-005"
        }
    ]
    
    for cost in construction_costs:
        transaction = Transaction(
            asset_id=land.id,
            project_id=project.id,
            transaction_date=(datetime.now() - timedelta(days=cost["days_ago"])).date(),
            transaction_type=TransactionType.EXPENSE,
            amount=cost["amount"],
            gst_amount=cost["amount"] * 0.1,
            expense_category=ExpenseCategory.CONSTRUCTION,
            description=cost["description"],
            reference_number=cost["reference"],
            vendor_payee="ABC Construction Pty Ltd",
            payment_method="Bank Transfer",
            is_reconciled=True
        )
        session.add(transaction)
    
    # Add professional fees
    professional_fees = [
        {
            "days_ago": 100,
            "amount": 45000.00,
            "category": ExpenseCategory.CONSULTING,
            "description": "Architectural design services",
            "vendor": "Design Partners Architecture"
        },
        {
            "days_ago": 95,
            "amount": 32000.00,
            "category": ExpenseCategory.CONSULTING,
            "description": "Structural engineering services",
            "vendor": "Structural Solutions QLD"
        },
        {
            "days_ago": 110,
            "amount": 15000.00,
            "category": ExpenseCategory.LEGAL_FEES,
            "description": "Development approval legal services",
            "vendor": "Thompson Legal"
        }
    ]
    
    for fee in professional_fees:
        transaction = Transaction(
            asset_id=land.id,
            project_id=project.id,
            transaction_date=(datetime.now() - timedelta(days=fee["days_ago"])).date(),
            transaction_type=TransactionType.EXPENSE,
            amount=fee["amount"],
            gst_amount=fee["amount"] * 0.1,
            expense_category=fee["category"],
            description=fee["description"],
            vendor_payee=fee["vendor"],
            payment_method="Bank Transfer",
            is_reconciled=True
        )
        session.add(transaction)
    
    # Add construction loan
    loan = DebtInstrument(
        asset_id=land.id,
        debt_name="Sunshine Coast Construction Facility",
        debt_type=DebtType.CONSTRUCTION_LOAN,
        loan_number="CL-2024-8765",
        lender_name="Commonwealth Bank of Australia",
        lender_contact="commercial.lending@cba.com.au",
        original_principal=3600000.00,
        current_principal=3250000.00,
        currency="AUD",
        interest_rate=6.75,
        interest_type="Variable",
        margin=2.25,
        loan_start_date=(datetime.now() - timedelta(days=90)).date(),
        maturity_date=(datetime.now() + timedelta(days=545)).date(),
        loan_term_months=18,
        repayment_frequency="Monthly",
        monthly_payment=22000.00,
        interest_payment=18281.25,
        principal_payment=3718.75,
        ltv_ratio=65.0,
        establishment_fee=18000.00,
        ongoing_fees=500.00,
        is_active=True,
        status="Active",
        purpose="Fund construction of industrial warehouse",
        security="First mortgage over land and works"
    )
    session.add(loan)
    
    print(f"  ✅ Created: {land.name}")
    print(f"     - Project: {project.project_name}")
    print(f"     - Budget: ${project.total_budget:,.2f}")
    print(f"     - Spent: ${project.actual_cost:,.2f} ({project.budget_utilization_percent:.1f}%)")
    print(f"     - 5 construction payment transactions")
    print(f"     - 3 professional fee transactions")
    print(f"     - Construction loan: ${loan.current_principal:,.2f}")
    
    return land, project


def create_development_land(session):
    """
    Create undeveloped land holding
    
    Returns:
        Asset: The created land asset
    """
    print("\n🏞️  Creating Acacia Ridge Development Land (Future Development)...")
    
    land = Asset(
        name="Acacia Ridge Industrial Land",
        asset_type=AssetType.LAND,
        status=AssetStatus.ACTIVE,
        address_line1="Lot 22 Industry Boulevard",
        suburb="Acacia Ridge",
        state="Queensland",
        postcode="4110",
        region="Brisbane",
        land_area_sqm=15000,
        purchase_price=4200000.00,
        purchase_date=(datetime.now() - timedelta(days=60)).date(),
        current_valuation=4200000.00,
        valuation_date=datetime.now().date(),
        zoning="Industrial 1",
        council="Brisbane City Council",
        description="Strategic land holding for future warehouse development - excellent location near airport and motorway"
    )
    session.add(land)
    session.flush()
    
    # Add purchase transaction
    purchase = Transaction(
        asset_id=land.id,
        transaction_date=(datetime.now() - timedelta(days=60)).date(),
        transaction_type=TransactionType.ASSET_PURCHASE,
        amount=4200000.00,
        gst_amount=0,  # Land is GST-free
        category="Land Acquisition",
        description="Purchase of Lot 22 Industry Boulevard, Acacia Ridge",
        reference_number="SETTLE-2024-AR001",
        vendor_payee="Brisbane Industrial Properties Pty Ltd",
        payment_method="Bank Transfer",
        is_reconciled=True
    )
    session.add(purchase)
    
    # Add holding costs
    holding_costs = [
        {
            "days_ago": 30,
            "amount": 8500.00,
            "category": ExpenseCategory.PROPERTY_TAX,
            "description": "Quarterly council rates",
            "vendor": "Brisbane City Council"
        },
        {
            "days_ago": 45,
            "amount": 15000.00,
            "category": ExpenseCategory.LEGAL_FEES,
            "description": "Legal fees for land acquisition",
            "vendor": "Brisbane Property Lawyers"
        }
    ]
    
    for cost in holding_costs:
        transaction = Transaction(
            asset_id=land.id,
            transaction_date=(datetime.now() - timedelta(days=cost["days_ago"])).date(),
            transaction_type=TransactionType.EXPENSE,
            amount=cost["amount"],
            gst_amount=cost["amount"] * 0.1 if cost["category"] != ExpenseCategory.PROPERTY_TAX else 0,
            expense_category=cost["category"],
            description=cost["description"],
            vendor_payee=cost["vendor"],
            payment_method="Bank Transfer",
            is_reconciled=True
        )
        session.add(transaction)
    
    print(f"  ✅ Created: {land.name}")
    print(f"     - Purchase Price: ${land.purchase_price:,.2f}")
    print(f"     - Land Area: {land.land_area_sqm:,.0f} sqm")
    print(f"     - 3 transactions (purchase + holding costs)")
    
    return land


def insert_sample_data(session):
    """
    Insert comprehensive sample data into the database
    
    Args:
        session: Database session
    """
    print("\n" + "="*70)
    print("CREATING SAMPLE DATA")
    print("="*70)
    
    # Create the three main assets
    brisbane_warehouse = create_brisbane_warehouse(session)
    sunshine_land, sunshine_project = create_sunshine_coast_project(session)
    development_land = create_development_land(session)
    
    # Commit all data
    session.commit()
    
    # Print summary
    print("\n" + "="*70)
    print("SAMPLE DATA SUMMARY")
    print("="*70)
    
    # Count all records
    from sqlalchemy import func
    
    asset_count = session.query(func.count(Asset.id)).scalar()
    project_count = session.query(func.count(Project.id)).scalar()
    transaction_count = session.query(func.count(Transaction.id)).scalar()
    rental_count = session.query(func.count(RentalIncome.id)).scalar()
    debt_count = session.query(func.count(DebtInstrument.id)).scalar()
    
    print(f"\n📊 Database Statistics:")
    print(f"   Assets:              {asset_count}")
    print(f"   Projects:            {project_count}")
    print(f"   Transactions:        {transaction_count}")
    print(f"   Rental Income:       {rental_count}")
    print(f"   Debt Instruments:    {debt_count}")
    
    # Financial summary
    total_income = session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == TransactionType.INCOME
    ).scalar() or 0
    
    total_expense = session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type.in_([
            TransactionType.EXPENSE,
            TransactionType.CAPITAL_EXPENDITURE
        ])
    ).scalar() or 0
    
    total_debt = session.query(func.sum(DebtInstrument.current_principal)).filter(
        DebtInstrument.is_active == True
    ).scalar() or 0
    
    total_valuation = session.query(func.sum(Asset.current_valuation)).scalar() or 0
    
    print(f"\n💰 Financial Summary:")
    print(f"   Total Portfolio Value:    ${total_valuation:,.2f}")
    print(f"   Total Income (6 months):  ${total_income:,.2f}")
    print(f"   Total Expenses:           ${total_expense:,.2f}")
    print(f"   Net Cash Flow:            ${(total_income - total_expense):,.2f}")
    print(f"   Outstanding Debt:         ${total_debt:,.2f}")
    print(f"   Equity:                   ${(total_valuation - total_debt):,.2f}")
    
    print("\n✅ Sample data created successfully!")


def main():
    """Main function to initialize database"""
    parser = argparse.ArgumentParser(
        description='Initialize Industrial Real Estate Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m models.init_db              # Create tables only
  python -m models.init_db --sample     # Create tables and add sample data
  python -m models.init_db --reset      # Reset database (WARNING: deletes all data!)
        """
    )
    parser.add_argument('--sample', action='store_true', 
                       help='Create sample data for testing')
    parser.add_argument('--reset', action='store_true', 
                       help='Drop and recreate all tables (CAUTION!)')
    parser.add_argument('--db', type=str, default='industrial_real_estate.db',
                       help='Database file path (default: industrial_real_estate.db)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Industrial Real Estate Asset Management System")
    print("Database Initialization")
    print("Developer: Gilbert - Brisbane, QLD")
    print("="*70)
    
    # Initialize database manager
    db_path = f'sqlite:///{args.db}'
    db_manager = DatabaseManager(db_path)
    
    if args.reset:
        print("\n⚠️  WARNING: This will delete all existing data!")
        confirm = input("Type 'YES' to confirm reset: ")
        if confirm == 'YES':
            drop_all_tables(db_manager)
            create_database_tables(db_manager)
            print("✅ Database reset complete")
        else:
            print("❌ Reset cancelled")
            return
    else:
        create_database_tables(db_manager)
    
    # Add sample data if requested
    if args.sample:
        session = db_manager.get_session()
        try:
            insert_sample_data(session)
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error creating sample data: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            db_manager.close_session(session)
    
    print("\n" + "="*70)
    print("✨ Database initialization complete!")
    print("="*70)
    print(f"\nDatabase file: {args.db}")
    print("\nNext steps:")
    print("  1. Import models: from models import Asset, Project, Transaction")
    print("  2. Create session: db = DatabaseManager(); session = db.get_session()")
    print("  3. Query data: assets = session.query(Asset).all()")
    print("\n")


if __name__ == "__main__":
    main()