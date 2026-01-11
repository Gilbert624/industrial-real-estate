"""
Industrial Real Estate Asset Management System - Database Models
SQLAlchemy ORM models for managing industrial properties in Brisbane and Sunshine Coast

Developer: Gilbert - Brisbane, QLD
Version: 1.0
Database: SQLite
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    ForeignKey, Text, Boolean, Numeric, Date, Enum, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

# Base class for all models
Base = declarative_base()


# ============================================================================
# ENUMS - Define standard values for certain fields
# ============================================================================

class AssetType(enum.Enum):
    """Types of industrial real estate assets"""
    WAREHOUSE = "warehouse"
    FACTORY = "factory"
    DISTRIBUTION_CENTER = "distribution_center"
    FLEX_SPACE = "flex_space"
    COLD_STORAGE = "cold_storage"
    LAND = "land"
    MIXED_USE = "mixed_use"


class AssetStatus(enum.Enum):
    """Current status of the asset"""
    ACTIVE = "active"
    UNDER_DEVELOPMENT = "under_development"
    LEASED = "leased"
    VACANT = "vacant"
    UNDER_CONTRACT = "under_contract"
    SOLD = "sold"
    DISPOSED = "disposed"


class ProjectStatus(enum.Enum):
    """Development project status"""
    PLANNING = "planning"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    CONSTRUCTION = "construction"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class TransactionType(enum.Enum):
    """Types of financial transactions"""
    INCOME = "income"
    EXPENSE = "expense"
    CAPITAL_EXPENDITURE = "capital_expenditure"
    LOAN_DRAWDOWN = "loan_drawdown"
    LOAN_REPAYMENT = "loan_repayment"
    ASSET_PURCHASE = "asset_purchase"
    ASSET_SALE = "asset_sale"


class ExpenseCategory(enum.Enum):
    """Categories for expense tracking"""
    CONSTRUCTION = "construction"
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    PROPERTY_TAX = "property_tax"
    INSURANCE = "insurance"
    LEGAL_FEES = "legal_fees"
    CONSULTING = "consulting"
    PROPERTY_MANAGEMENT = "property_management"
    MARKETING = "marketing"
    OTHER = "other"


class DebtType(enum.Enum):
    """Types of debt instruments"""
    BANK_LOAN = "bank_loan"
    CONSTRUCTION_LOAN = "construction_loan"
    BRIDGE_LOAN = "bridge_loan"
    PRIVATE_DEBT = "private_debt"
    BOND = "bond"
    MEZZANINE = "mezzanine"
    LINE_OF_CREDIT = "line_of_credit"


# ============================================================================
# CORE MODELS
# ============================================================================

class Asset(Base):
    """
    Assets/Properties Table
    Represents individual industrial real estate assets/properties
    """
    __tablename__ = 'assets'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    name = Column(String(200), nullable=False, index=True)
    asset_type = Column(Enum(AssetType), nullable=False, index=True)
    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE, index=True)
    
    # Location Information
    address_line1 = Column(String(200), nullable=False)
    address_line2 = Column(String(200), nullable=True)
    suburb = Column(String(100), nullable=False, index=True)  # Brisbane, Sunshine Coast suburbs
    state = Column(String(50), nullable=False, default='Queensland')
    postcode = Column(String(10), nullable=False)
    region = Column(String(100), nullable=False, index=True)  # e.g., "Brisbane", "Sunshine Coast"
    
    # Physical Characteristics
    land_area_sqm = Column(Float, nullable=True)  # Land area in square meters
    building_area_sqm = Column(Float, nullable=True)  # Building/GLA in square meters
    warehouse_area_sqm = Column(Float, nullable=True)  # Warehouse space
    office_area_sqm = Column(Float, nullable=True)  # Office space
    
    # Technical Specifications
    clear_height_meters = Column(Float, nullable=True)  # Internal clear height
    power_capacity_kva = Column(Float, nullable=True)  # Electrical capacity
    loading_docks = Column(Integer, nullable=True)  # Number of loading docks
    car_parking_spaces = Column(Integer, nullable=True)
    
    # Financial Information
    purchase_price = Column(Numeric(15, 2), nullable=True)  # Purchase price in AUD
    purchase_date = Column(Date, nullable=True)
    current_valuation = Column(Numeric(15, 2), nullable=True)  # Current market value
    valuation_date = Column(Date, nullable=True)
    
    # Zoning and Compliance
    zoning = Column(String(100), nullable=True)  # e.g., "Industrial 1"
    council = Column(String(100), nullable=True)  # Local council name
    
    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="asset", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")
    rental_incomes = relationship("RentalIncome", back_populates="asset", cascade="all, delete-orphan")
    debt_instruments = relationship("DebtInstrument", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', type={self.asset_type.value}, suburb='{self.suburb}')>"
    
    def __str__(self):
        return f"{self.name} - {self.suburb}, {self.state}"


class Project(Base):
    """
    Development Projects Table
    Tracks development projects and their milestones
    """
    __tablename__ = 'projects'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False, index=True)
    
    # Basic Information
    project_name = Column(String(200), nullable=False, index=True)
    project_code = Column(String(50), nullable=True, unique=True, index=True)  # e.g., "BNE-WH-001"
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING, index=True)
    
    # Project Details
    description = Column(Text, nullable=True)
    scope_of_work = Column(Text, nullable=True)
    
    # Timeline
    planned_start_date = Column(Date, nullable=True)
    actual_start_date = Column(Date, nullable=True)
    planned_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    
    # Budget and Costs
    total_budget = Column(Numeric(15, 2), nullable=True)  # Total project budget in AUD
    actual_cost = Column(Numeric(15, 2), nullable=True, default=0)  # Actual costs incurred
    contingency_budget = Column(Numeric(15, 2), nullable=True)
    
    # Project Team
    project_manager = Column(String(100), nullable=True)
    contractor = Column(String(200), nullable=True)
    architect = Column(String(200), nullable=True)
    engineer = Column(String(200), nullable=True)
    
    # Milestones (stored as text, could be expanded to separate table)
    key_milestones = Column(Text, nullable=True)  # JSON or delimited string
    
    # Approvals and Compliance
    da_number = Column(String(100), nullable=True)  # Development Approval number
    da_approval_date = Column(Date, nullable=True)
    building_approval_date = Column(Date, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", back_populates="projects")
    transactions = relationship("Transaction", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.project_name}', status={self.status.value})>"
    
    def __str__(self):
        return f"{self.project_name} ({self.status.value})"
    
    @property
    def budget_variance(self):
        """Calculate budget variance (actual vs planned)"""
        if self.total_budget and self.actual_cost:
            return float(self.actual_cost - self.total_budget)
        return None
    
    @property
    def budget_utilization_percent(self):
        """Calculate percentage of budget used"""
        if self.total_budget and self.actual_cost and self.total_budget > 0:
            return float((self.actual_cost / self.total_budget) * 100)
        return None


class Transaction(Base):
    """
    Financial Transactions Table
    Records all financial transactions (income and expenses)
    """
    __tablename__ = 'transactions'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True, index=True)
    
    # Transaction Information
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    
    # Amount and Currency
    amount = Column(Numeric(15, 2), nullable=False)  # Amount in AUD
    currency = Column(String(3), nullable=False, default='AUD')
    gst_amount = Column(Numeric(15, 2), nullable=True, default=0)  # GST component
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)
    expense_category = Column(Enum(ExpenseCategory), nullable=True, index=True)
    
    # Description and Reference
    description = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True, index=True)  # Invoice/receipt number
    vendor_payee = Column(String(200), nullable=True, index=True)  # Who we paid or who paid us
    
    # Payment Information
    payment_method = Column(String(50), nullable=True)  # e.g., "Bank Transfer", "Cheque"
    bank_account = Column(String(100), nullable=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False, nullable=False, index=True)
    reconciliation_date = Column(Date, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    attachments = Column(Text, nullable=True)  # File paths or URLs to receipts/invoices
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", back_populates="transactions")
    project = relationship("Project", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type.value}, amount={self.amount}, date={self.transaction_date})>"
    
    def __str__(self):
        return f"{self.transaction_type.value}: ${self.amount} - {self.description[:50]}"
    
    @property
    def amount_including_gst(self):
        """Total amount including GST"""
        return float(self.amount + (self.gst_amount or 0))


class RentalIncome(Base):
    """
    Rental Income Table
    Tracks rental income from leased properties
    """
    __tablename__ = 'rental_income'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False, index=True)
    
    # Tenant Information
    tenant_name = Column(String(200), nullable=False, index=True)
    tenant_abn = Column(String(20), nullable=True)
    tenant_contact = Column(String(200), nullable=True)
    
    # Lease Details
    lease_start_date = Column(Date, nullable=False, index=True)
    lease_end_date = Column(Date, nullable=False, index=True)
    lease_term_months = Column(Integer, nullable=True)
    
    # Rental Amounts
    monthly_rent = Column(Numeric(12, 2), nullable=False)  # Base monthly rent in AUD
    annual_rent = Column(Numeric(12, 2), nullable=False)  # Annual rent
    rent_per_sqm = Column(Numeric(10, 2), nullable=True)  # Rent per square meter
    
    # Additional Charges
    outgoings = Column(Numeric(12, 2), nullable=True, default=0)  # Monthly outgoings
    gst_amount = Column(Numeric(12, 2), nullable=True, default=0)
    
    # Payment Information
    payment_frequency = Column(String(50), nullable=False, default='Monthly')  # Monthly, Quarterly
    payment_day = Column(Integer, nullable=True)  # Day of month payment is due
    payment_method = Column(String(50), nullable=True)
    
    # Lease Terms
    rent_review_date = Column(Date, nullable=True)
    rent_increase_percent = Column(Float, nullable=True)  # Annual increase percentage
    rent_increase_type = Column(String(50), nullable=True)  # Fixed, CPI, Market
    
    # Security and Guarantees
    bond_amount = Column(Numeric(12, 2), nullable=True)
    bank_guarantee = Column(Numeric(12, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    lease_status = Column(String(50), nullable=True, index=True)  # Active, Expired, Terminated
    
    # Area Leased
    leased_area_sqm = Column(Float, nullable=True)
    
    # Additional Information
    lease_type = Column(String(50), nullable=True)  # Gross, Net, Triple Net
    special_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", back_populates="rental_incomes")
    
    def __repr__(self):
        return f"<RentalIncome(id={self.id}, tenant='{self.tenant_name}', monthly_rent={self.monthly_rent})>"
    
    def __str__(self):
        return f"{self.tenant_name} - ${self.monthly_rent}/month"
    
    @property
    def total_monthly_income(self):
        """Total monthly income including outgoings"""
        return float(self.monthly_rent + (self.outgoings or 0))
    
    @property
    def remaining_lease_days(self):
        """Calculate days remaining in lease"""
        if self.lease_end_date:
            delta = self.lease_end_date - datetime.now().date()
            return delta.days if delta.days > 0 else 0
        return None


class DebtInstrument(Base):
    """
    Debt Instruments Table
    Tracks loans, bonds, and other debt financing
    """
    __tablename__ = 'debt_instruments'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key (optional - debt may not be tied to specific asset)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True, index=True)
    
    # Debt Identification
    debt_name = Column(String(200), nullable=False, index=True)
    debt_type = Column(Enum(DebtType), nullable=False, index=True)
    loan_number = Column(String(100), nullable=True, unique=True, index=True)
    
    # Lender Information
    lender_name = Column(String(200), nullable=False, index=True)
    lender_contact = Column(String(200), nullable=True)
    
    # Principal Amount
    original_principal = Column(Numeric(15, 2), nullable=False)  # Original loan amount
    current_principal = Column(Numeric(15, 2), nullable=False)  # Current outstanding balance
    currency = Column(String(3), nullable=False, default='AUD')
    
    # Interest and Fees
    interest_rate = Column(Float, nullable=False)  # Annual interest rate (%)
    interest_type = Column(String(50), nullable=True)  # Fixed, Variable, Mixed
    margin = Column(Float, nullable=True)  # Margin over base rate (e.g., BBSY + 2.5%)
    
    # Loan Terms
    loan_start_date = Column(Date, nullable=False, index=True)
    maturity_date = Column(Date, nullable=False, index=True)
    loan_term_months = Column(Integer, nullable=True)
    
    # Repayment
    repayment_frequency = Column(String(50), nullable=False, default='Monthly')
    monthly_payment = Column(Numeric(12, 2), nullable=True)
    principal_payment = Column(Numeric(12, 2), nullable=True)
    interest_payment = Column(Numeric(12, 2), nullable=True)
    
    # Loan to Value Ratio
    ltv_ratio = Column(Float, nullable=True)  # Loan to Value ratio (%)
    
    # Covenants and Conditions
    covenants = Column(Text, nullable=True)  # Key loan covenants
    security = Column(Text, nullable=True)  # Security/collateral details
    
    # Fees
    establishment_fee = Column(Numeric(12, 2), nullable=True)
    ongoing_fees = Column(Numeric(12, 2), nullable=True)
    exit_fee = Column(Numeric(12, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    status = Column(String(50), nullable=True, index=True)  # Active, Paid Off, Default
    
    # Additional Information
    purpose = Column(Text, nullable=True)  # Purpose of the loan
    notes = Column(Text, nullable=True)
    documents = Column(Text, nullable=True)  # Paths to loan documents
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", back_populates="debt_instruments")
    
    def __repr__(self):
        return f"<DebtInstrument(id={self.id}, name='{self.debt_name}', type={self.debt_type.value}, principal={self.current_principal})>"
    
    def __str__(self):
        return f"{self.debt_name} - {self.lender_name}: ${self.current_principal}"
    
    @property
    def total_repaid(self):
        """Calculate total amount repaid"""
        if self.original_principal and self.current_principal:
            return float(self.original_principal - self.current_principal)
        return None
    
    @property
    def remaining_term_days(self):
        """Calculate days remaining until maturity"""
        if self.maturity_date:
            delta = self.maturity_date - datetime.now().date()
            return delta.days if delta.days > 0 else 0
        return None
    
    @property
    def annual_interest_cost(self):
        """Calculate annual interest cost"""
        if self.current_principal and self.interest_rate:
            return float(self.current_principal * (self.interest_rate / 100))
        return None


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

class DatabaseManager:
    """
    Database Manager for easy database operations
    """
    
    def __init__(self, database_url='sqlite:///industrial_real_estate.db'):
        """
        Initialize database connection
        
        Args:
            database_url: SQLAlchemy database URL (default: SQLite)
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_all_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ All database tables created successfully!")
    
    def drop_all_tables(self):
        """Drop all tables from the database (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        print("⚠️  All database tables dropped!")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close a database session"""
        session.close()
    
    def get_cash_balance(self) -> float:
        """
        Get the total cash balance (sum of all transaction amounts)
        
        Returns:
            float: Total cash balance, 0 if no transactions or error occurs
        """
        session = self.get_session()
        try:
            result = session.query(func.sum(Transaction.amount)).scalar()
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error getting cash balance: {e}")
            return 0.0
        finally:
            self.close_session(session)
    
    def get_monthly_income(self, year: int, month: int) -> float:
        """
        Get total income for a specific month
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            
        Returns:
            float: Total income for the specified month, 0 if no income or error occurs
        """
        session = self.get_session()
        try:
            from datetime import date
            start_date = date(year, month, 1)
            # Calculate end date (first day of next month)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            result = session.query(func.sum(Transaction.amount)).filter(
                Transaction.transaction_type == TransactionType.INCOME,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date
            ).scalar()
            
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error getting monthly income: {e}")
            return 0.0
        finally:
            self.close_session(session)
    
    def get_monthly_expense(self, year: int, month: int) -> float:
        """
        Get total expenses for a specific month
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            
        Returns:
            float: Total expenses for the specified month, 0 if no expenses or error occurs
        """
        session = self.get_session()
        try:
            from datetime import date
            start_date = date(year, month, 1)
            # Calculate end date (first day of next month)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            result = session.query(func.sum(Transaction.amount)).filter(
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date
            ).scalar()
            
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error getting monthly expense: {e}")
            return 0.0
        finally:
            self.close_session(session)
    
    def get_cashflow_trend(self, months: int = 6) -> List[Dict]:
        """
        Get cashflow trend for multiple months
        
        Args:
            months: Number of months to retrieve (default: 6)
            
        Returns:
            List[Dict]: List of dictionaries with keys: 'year', 'month', 'income', 'expense', 'net'
                       Returns empty list if error occurs
        """
        try:
            from datetime import date
            
            today = date.today()
            trend_data = []
            
            for i in range(months):
                # Calculate the date for each month going backwards
                if today.month - i <= 0:
                    target_year = today.year - 1
                    target_month = today.month - i + 12
                else:
                    target_year = today.year
                    target_month = today.month - i
                
                income = self.get_monthly_income(target_year, target_month)
                expense = self.get_monthly_expense(target_year, target_month)
                net = income - expense
                
                trend_data.append({
                    'year': target_year,
                    'month': target_month,
                    'income': income,
                    'expense': expense,
                    'net': net
                })
            
            # Reverse to show oldest to newest
            trend_data.reverse()
            return trend_data
        except Exception as e:
            print(f"Error getting cashflow trend: {e}")
            return []
    
    def get_recent_transactions(self, limit: int = 20) -> List[Transaction]:
        """
        Get recent transactions ordered by date (most recent first)
        
        Args:
            limit: Number of transactions to retrieve (default: 20)
            
        Returns:
            List[Transaction]: List of Transaction objects, returns empty list if error occurs
        """
        session = self.get_session()
        try:
            transactions = session.query(Transaction).order_by(
                Transaction.transaction_date.desc(),
                Transaction.id.desc()
            ).limit(limit).all()
            
            return transactions
        except Exception as e:
            print(f"Error getting recent transactions: {e}")
            return []
        finally:
            self.close_session(session)
    
    def add_asset(self, asset_data: dict, session=None) -> Asset:
        """
        添加新资产
        
        Args:
            asset_data: 包含资产字段的字典
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Asset: 创建的Asset对象
        
        Raises:
            Exception: 如果创建失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 处理地址字段 - 如果只提供了address，需要拆分为address_line1
            # 同时设置必需的suburb, state, postcode字段
            if 'address' in asset_data and 'address_line1' not in asset_data:
                asset_data['address_line1'] = asset_data.pop('address')
            
            # 确保必需的地址字段存在
            if 'suburb' not in asset_data:
                asset_data['suburb'] = asset_data.get('region', 'TBD')
            if 'state' not in asset_data:
                asset_data['state'] = 'Queensland'
            if 'postcode' not in asset_data:
                asset_data['postcode'] = '0000'
            
            # 处理asset_type - 映射用户友好的值到枚举
            if 'asset_type' in asset_data and isinstance(asset_data['asset_type'], str):
                asset_type_str = asset_data['asset_type'].lower().replace(' ', '_')
                asset_type_map = {
                    'industrial_warehouse': AssetType.WAREHOUSE,
                    'warehouse': AssetType.WAREHOUSE,
                    'land': AssetType.LAND,
                    'mixed_use': AssetType.MIXED_USE
                }
                if asset_type_str in asset_type_map:
                    asset_data['asset_type'] = asset_type_map[asset_type_str]
                elif asset_type_str in [e.value for e in AssetType]:
                    # 如果已经是正确的枚举值字符串
                    for at in AssetType:
                        if at.value == asset_type_str:
                            asset_data['asset_type'] = at
                            break
            
            # 处理status - 映射用户友好的值到枚举
            if 'status' in asset_data and isinstance(asset_data['status'], str):
                status_str = asset_data['status'].lower().replace(' ', '_')
                status_map = {
                    'operating': AssetStatus.ACTIVE,
                    'under_development': AssetStatus.UNDER_DEVELOPMENT,
                    'planned': AssetStatus.UNDER_DEVELOPMENT
                }
                if status_str in status_map:
                    asset_data['status'] = status_map[status_str]
                elif status_str in [e.value for e in AssetStatus]:
                    # 如果已经是正确的枚举值字符串
                    for s in AssetStatus:
                        if s.value == status_str:
                            asset_data['status'] = s
                            break
            
            # 处理acquisition_date -> purchase_date
            if 'acquisition_date' in asset_data and 'purchase_date' not in asset_data:
                asset_data['purchase_date'] = asset_data.pop('acquisition_date')
            
            # 创建Asset对象
            new_asset = Asset(**asset_data)
            session.add(new_asset)
            session.commit()
            session.refresh(new_asset)
            return new_asset
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to add asset: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def update_asset(self, asset_id: int, asset_data: dict, session=None) -> Asset:
        """
        更新资产
        
        Args:
            asset_id: 资产ID
            asset_data: 包含要更新的字段的字典（只更新提供的字段）
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Asset: 更新后的Asset对象，如果资产不存在则返回None
        
        Raises:
            Exception: 如果更新失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询资产
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return None
            
            # 处理地址字段
            if 'address' in asset_data:
                asset_data['address_line1'] = asset_data.pop('address')
            
            # 处理asset_type
            if 'asset_type' in asset_data and isinstance(asset_data['asset_type'], str):
                asset_type_str = asset_data['asset_type'].lower().replace(' ', '_')
                asset_type_map = {
                    'industrial_warehouse': AssetType.WAREHOUSE,
                    'warehouse': AssetType.WAREHOUSE,
                    'land': AssetType.LAND,
                    'mixed_use': AssetType.MIXED_USE
                }
                if asset_type_str in asset_type_map:
                    asset_data['asset_type'] = asset_type_map[asset_type_str]
                elif asset_type_str in [e.value for e in AssetType]:
                    for at in AssetType:
                        if at.value == asset_type_str:
                            asset_data['asset_type'] = at
                            break
            
            # 处理status
            if 'status' in asset_data and isinstance(asset_data['status'], str):
                status_str = asset_data['status'].lower().replace(' ', '_')
                status_map = {
                    'operating': AssetStatus.ACTIVE,
                    'under_development': AssetStatus.UNDER_DEVELOPMENT,
                    'planned': AssetStatus.UNDER_DEVELOPMENT
                }
                if status_str in status_map:
                    asset_data['status'] = status_map[status_str]
                elif status_str in [e.value for e in AssetStatus]:
                    for s in AssetStatus:
                        if s.value == status_str:
                            asset_data['status'] = s
                            break
            
            # 处理acquisition_date -> purchase_date
            if 'acquisition_date' in asset_data:
                asset_data['purchase_date'] = asset_data.pop('acquisition_date')
            
            # 更新字段（只更新提供的字段）
            for key, value in asset_data.items():
                if hasattr(asset, key):
                    setattr(asset, key, value)
            
            session.commit()
            session.refresh(asset)
            return asset
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to update asset: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def delete_asset(self, asset_id: int, session=None) -> bool:
        """
        删除资产
        
        Args:
            asset_id: 资产ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            bool: 如果删除成功返回True，如果资产不存在返回False
        
        Raises:
            Exception: 如果删除失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询资产
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return False
            
            session.delete(asset)
            session.commit()
            return True
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to delete asset: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def get_asset_by_id(self, asset_id: int, session=None) -> Asset:
        """
        根据ID获取资产
        
        Args:
            asset_id: 资产ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Asset: Asset对象，如果不存在则返回None
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            return asset
        except Exception as e:
            print(f"Error getting asset by id: {e}")
            return None
        finally:
            if should_close:
                self.close_session(session)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize database
    db_manager = DatabaseManager('sqlite:///industrial_real_estate.db')
    
    # Create all tables
    db_manager.create_all_tables()
    
    # Create a session
    session = db_manager.get_session()
    
    try:
        # Example: Create a new asset
        new_asset = Asset(
            name="Brisbane Logistics Centre",
            asset_type=AssetType.WAREHOUSE,
            status=AssetStatus.UNDER_DEVELOPMENT,
            address_line1="123 Industrial Drive",
            suburb="Eagle Farm",
            state="Queensland",
            postcode="4009",
            region="Brisbane",
            land_area_sqm=5000,
            building_area_sqm=4200,
            warehouse_area_sqm=3800,
            office_area_sqm=400,
            clear_height_meters=9.0,
            power_capacity_kva=500,
            loading_docks=4,
            car_parking_spaces=20,
            purchase_price=5000000.00,
            purchase_date=datetime(2024, 1, 15).date(),
            description="Modern warehouse facility with high clearance"
        )
        
        session.add(new_asset)
        session.commit()
        
        print(f"✅ Created: {new_asset}")
        
        # Query example
        assets = session.query(Asset).filter_by(region="Brisbane").all()
        print(f"\n📊 Found {len(assets)} asset(s) in Brisbane")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    
    finally:
        db_manager.close_session(session)
    
    print("\n✨ Database setup complete!")