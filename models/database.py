"""
Industrial Real Estate Asset Management System - Database Models
SQLAlchemy ORM models for managing industrial properties in Brisbane and Sunshine Coast

Developer: Gilbert - Brisbane, QLD
Version: 1.0
Database: SQLite
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    ForeignKey, Text, Boolean, Numeric, Date, Enum, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
import enum
import logging
import hashlib

# Setup logger
logger = logging.getLogger(__name__)

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


class APIUsage(Base):
    """Track Claude API usage for cost monitoring"""
    __tablename__ = 'api_usage'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    query_type = Column(String(50))  # 'natural_query', 'quick_analysis', etc.
    model_used = Column(String(50))  # 'sonnet-4', 'haiku', etc.
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    question_hash = Column(String(64))  # For detecting similar queries
    response_cached = Column(Boolean, default=False)
    user_question = Column(Text)  # Optional: store question for analysis
    
    def __repr__(self):
        return f"<APIUsage(id={self.id}, query_type='{self.query_type}', cost={self.estimated_cost})>"


# ============================================================================
# DUE DILIGENCE MODELS
# ============================================================================

class DDProject(Base):
    """Due Diligence Project - Investment opportunity being evaluated"""
    __tablename__ = 'dd_projects'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Basic Info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    property_type = Column(String(100))  # Industrial Warehouse, Land, Mixed Use
    status = Column(String(50), default='Under Review')  # Under Review, Approved, Rejected, On Hold
    
    # Land & Building
    land_area_sqm = Column(Float)
    building_area_sqm = Column(Float)
    zoning = Column(String(100))
    
    # Acquisition
    purchase_price = Column(Float)
    acquisition_costs = Column(Float)  # Legal, due diligence fees
    
    # Development
    construction_cost = Column(Float)
    construction_duration_months = Column(Integer)
    contingency_percentage = Column(Float, default=10.0)
    
    # Financing
    equity_percentage = Column(Float, default=30.0)
    debt_percentage = Column(Float, default=70.0)
    interest_rate = Column(Float, default=6.0)
    loan_term_years = Column(Integer, default=25)
    
    # Revenue
    estimated_monthly_rent = Column(Float)
    rent_growth_rate = Column(Float, default=3.0)  # Annual %
    occupancy_rate = Column(Float, default=95.0)  # %
    operating_expense_ratio = Column(Float, default=30.0)  # % of revenue
    
    # Exit
    holding_period_years = Column(Integer, default=10)
    exit_cap_rate = Column(Float, default=6.5)
    
    # Calculated Results (stored after calculation)
    irr = Column(Float)
    npv = Column(Float)
    equity_multiple = Column(Float)
    cash_on_cash_return = Column(Float)
    
    # Relationships
    scenarios = relationship("DDScenario", back_populates="project", cascade="all, delete-orphan")
    assumptions = relationship("DDAssumption", back_populates="project", cascade="all, delete-orphan")


class DDScenario(Base):
    """Different scenarios for sensitivity analysis"""
    __tablename__ = 'dd_scenarios'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('dd_projects.id'), nullable=False)
    
    scenario_name = Column(String(100), nullable=False)  # Base Case, Optimistic, Pessimistic
    
    # Adjusted parameters
    purchase_price_adjustment = Column(Float, default=0.0)  # % adjustment
    construction_cost_adjustment = Column(Float, default=0.0)
    rent_adjustment = Column(Float, default=0.0)
    occupancy_adjustment = Column(Float, default=0.0)
    exit_cap_adjustment = Column(Float, default=0.0)
    
    # Results for this scenario
    irr = Column(Float)
    npv = Column(Float)
    equity_multiple = Column(Float)
    
    # Relationship
    project = relationship("DDProject", back_populates="scenarios")


class DDAssumption(Base):
    """Custom assumptions and notes for DD project"""
    __tablename__ = 'dd_assumptions'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('dd_projects.id'), nullable=False)
    
    category = Column(String(100))  # Cost, Revenue, Risk, Market, etc.
    assumption_text = Column(Text, nullable=False)
    source = Column(String(200))  # Data source or reference
    confidence_level = Column(String(50))  # High, Medium, Low
    
    # Relationship
    project = relationship("DDProject", back_populates="assumptions")


class DDCashFlow(Base):
    """Projected cash flows for DD project"""
    __tablename__ = 'dd_cashflows'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('dd_projects.id'), nullable=False)
    scenario_id = Column(Integer, ForeignKey('dd_scenarios.id'), nullable=True)
    
    period = Column(Integer, nullable=False)  # Year number (0, 1, 2, ...)
    period_type = Column(String(20), default='annual')  # annual, monthly
    
    # Revenue
    gross_rental_income = Column(Float, default=0.0)
    vacancy_loss = Column(Float, default=0.0)
    effective_gross_income = Column(Float, default=0.0)
    
    # Expenses
    operating_expenses = Column(Float, default=0.0)
    net_operating_income = Column(Float, default=0.0)
    
    # Capital
    capital_expenditure = Column(Float, default=0.0)
    
    # Financing
    debt_service = Column(Float, default=0.0)
    
    # Results
    cash_flow_before_tax = Column(Float, default=0.0)
    cumulative_cash_flow = Column(Float, default=0.0)


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
        Uses joinedload to eager load asset relationship to avoid DetachedInstanceError
        
        Args:
            limit: Number of transactions to retrieve (default: 20)
            
        Returns:
            List[Transaction]: List of Transaction objects with asset relationship loaded, returns empty list if error occurs
        """
        session = self.get_session()
        try:
            transactions = session.query(Transaction).options(
                joinedload(Transaction.asset)
            ).order_by(
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
    
    def add_transaction(self, transaction_data: dict, session=None) -> Transaction:
        """
        添加新交易记录
        
        Args:
            transaction_data: 包含交易字段的字典
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Transaction: 创建的Transaction对象
        
        Raises:
            Exception: 如果创建失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 处理transaction_type - 映射字符串到枚举
            if 'transaction_type' in transaction_data and isinstance(transaction_data['transaction_type'], str):
                type_str = transaction_data['transaction_type'].upper()
                if type_str == 'INCOME':
                    transaction_data['transaction_type'] = TransactionType.INCOME
                elif type_str == 'EXPENSE':
                    transaction_data['transaction_type'] = TransactionType.EXPENSE
                else:
                    # 尝试匹配枚举值
                    for tt in TransactionType:
                        if tt.value.upper() == type_str:
                            transaction_data['transaction_type'] = tt
                            break
            
            # 确保currency有默认值
            if 'currency' not in transaction_data:
                transaction_data['currency'] = 'AUD'
            
            # 创建Transaction对象
            new_transaction = Transaction(**transaction_data)
            session.add(new_transaction)
            session.commit()
            session.refresh(new_transaction)
            return new_transaction
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to add transaction: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def update_transaction(self, transaction_id: int, transaction_data: dict, session=None) -> Optional[Transaction]:
        """
        更新交易记录
        
        Args:
            transaction_id: 交易ID
            transaction_data: 包含要更新的字段的字典（只更新提供的字段）
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Transaction: 更新后的Transaction对象，如果交易不存在则返回None
        
        Raises:
            Exception: 如果更新失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询交易
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return None
            
            # 处理transaction_type
            if 'transaction_type' in transaction_data and isinstance(transaction_data['transaction_type'], str):
                type_str = transaction_data['transaction_type'].upper()
                if type_str == 'INCOME':
                    transaction_data['transaction_type'] = TransactionType.INCOME
                elif type_str == 'EXPENSE':
                    transaction_data['transaction_type'] = TransactionType.EXPENSE
                else:
                    for tt in TransactionType:
                        if tt.value.upper() == type_str:
                            transaction_data['transaction_type'] = tt
                            break
            
            # 更新字段（只更新提供的字段）
            for key, value in transaction_data.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            session.commit()
            session.refresh(transaction)
            return transaction
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to update transaction: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def delete_transaction(self, transaction_id: int, session=None) -> bool:
        """
        删除交易记录
        
        Args:
            transaction_id: 交易ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            bool: 如果删除成功返回True，如果交易不存在返回False
        
        Raises:
            Exception: 如果删除失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询交易
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return False
            
            session.delete(transaction)
            session.commit()
            return True
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to delete transaction: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def get_transaction_by_id(self, transaction_id: int, session=None) -> Transaction:
        """
        根据ID获取交易
        
        Args:
            transaction_id: 交易ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Transaction: Transaction对象，如果不存在则返回None
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            return transaction
        except Exception as e:
            print(f"Error getting transaction by id: {e}")
            return None
        finally:
            if should_close:
                self.close_session(session)
    
    def get_all_assets_for_dropdown(self, session=None) -> List[Dict]:
        """
        获取所有资产用于下拉选择
        
        Args:
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            List[Dict]: 格式为 [{"id": 1, "name": "Asset Name"}, ...] 的列表
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            assets = session.query(Asset).order_by(Asset.name).all()
            return [{"id": asset.id, "name": asset.name} for asset in assets]
        except Exception as e:
            print(f"Error getting assets for dropdown: {e}")
            return []
        finally:
            if should_close:
                self.close_session(session)
    
    def get_all_projects(self, session=None) -> List[Project]:
        """
        获取所有项目
        
        Args:
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            List[Project]: 项目列表，按创建时间降序排列，返回空列表如果出错
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            projects = session.query(Project).options(
                joinedload(Project.asset)
            ).order_by(
                Project.created_at.desc()
            ).all()
            return projects
        except Exception as e:
            print(f"Error getting all projects: {e}")
            return []
        finally:
            if should_close:
                self.close_session(session)
    
    def add_project(self, project_data: dict, session=None) -> Project:
        """
        添加新项目
        
        Args:
            project_data: 包含项目字段的字典
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Project: 创建的Project对象
        
        Raises:
            Exception: 如果创建失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 字段映射：将用户友好的字段名映射到数据库字段名
            # name -> project_name
            if 'name' in project_data and 'project_name' not in project_data:
                project_data['project_name'] = project_data.pop('name')
            
            # budget -> total_budget
            if 'budget' in project_data and 'total_budget' not in project_data:
                project_data['total_budget'] = project_data.pop('budget')
            
            # start_date -> planned_start_date
            if 'start_date' in project_data and 'planned_start_date' not in project_data:
                project_data['planned_start_date'] = project_data.pop('start_date')
                # 如果提供了datetime对象，转换为date
                if isinstance(project_data['planned_start_date'], datetime):
                    project_data['planned_start_date'] = project_data['planned_start_date'].date()
            
            # expected_completion -> planned_completion_date
            if 'expected_completion' in project_data and 'planned_completion_date' not in project_data:
                project_data['planned_completion_date'] = project_data.pop('expected_completion')
                # 如果提供了datetime对象，转换为date
                if isinstance(project_data['planned_completion_date'], datetime):
                    project_data['planned_completion_date'] = project_data['planned_completion_date'].date()
            
            # completion_percentage 不是Project模型的字段，忽略或可以存储到notes中
            if 'completion_percentage' in project_data:
                # 可以将其添加到notes中，或者直接忽略
                project_data.pop('completion_percentage')
            
            # 移除其他不存在的字段（如project_type, location, land_area_sqm等，这些属于Asset模型）
            fields_to_remove = ['project_type', 'location', 'land_area_sqm', 'building_area_sqm', 'estimated_value']
            for field in fields_to_remove:
                project_data.pop(field, None)
            
            # 处理status - 映射字符串到枚举
            if 'status' in project_data and isinstance(project_data['status'], str):
                status_str = project_data['status'].lower().replace(' ', '_')
                # 处理常见的大小写变体
                status_map = {
                    'construction': ProjectStatus.CONSTRUCTION,
                    'planning': ProjectStatus.PLANNING,
                    'approved': ProjectStatus.APPROVED,
                    'completed': ProjectStatus.COMPLETED,
                    'on_hold': ProjectStatus.ON_HOLD,
                    'cancelled': ProjectStatus.CANCELLED,
                    'approval_pending': ProjectStatus.APPROVAL_PENDING
                }
                if status_str in status_map:
                    project_data['status'] = status_map[status_str]
                elif status_str in [e.value for e in ProjectStatus]:
                    for ps in ProjectStatus:
                        if ps.value == status_str:
                            project_data['status'] = ps
                            break
            
            # 确保asset_id存在（如果没有提供，可以尝试从现有资产中选择第一个，但这可能不是最佳实践）
            # 这里我们先不处理，让数据库约束来处理
            
            # 创建Project对象
            new_project = Project(**project_data)
            session.add(new_project)
            session.commit()
            session.refresh(new_project)
            return new_project
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to add project: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def update_project(self, project_id: int, project_data: dict, session=None) -> Optional[Project]:
        """
        更新项目
        
        Args:
            project_id: 项目ID
            project_data: 包含要更新的字段的字典（只更新提供的字段）
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Optional[Project]: 更新后的Project对象，如果项目不存在则返回None
        
        Raises:
            Exception: 如果更新失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询项目
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            
            # 字段映射：将用户友好的字段名映射到数据库字段名
            # name -> project_name
            if 'name' in project_data and 'project_name' not in project_data:
                project_data['project_name'] = project_data.pop('name')
            
            # budget -> total_budget
            if 'budget' in project_data and 'total_budget' not in project_data:
                project_data['total_budget'] = project_data.pop('budget')
            
            # start_date -> planned_start_date
            if 'start_date' in project_data and 'planned_start_date' not in project_data:
                project_data['planned_start_date'] = project_data.pop('start_date')
                if isinstance(project_data['planned_start_date'], datetime):
                    project_data['planned_start_date'] = project_data['planned_start_date'].date()
            
            # expected_completion -> planned_completion_date
            if 'expected_completion' in project_data and 'planned_completion_date' not in project_data:
                project_data['planned_completion_date'] = project_data.pop('expected_completion')
                if isinstance(project_data['planned_completion_date'], datetime):
                    project_data['planned_completion_date'] = project_data['planned_completion_date'].date()
            
            # completion_percentage 不是Project模型的字段，忽略
            if 'completion_percentage' in project_data:
                project_data.pop('completion_percentage')
            
            # 移除其他不存在的字段
            fields_to_remove = ['project_type', 'location', 'land_area_sqm', 'building_area_sqm', 'estimated_value']
            for field in fields_to_remove:
                project_data.pop(field, None)
            
            # 处理status
            if 'status' in project_data and isinstance(project_data['status'], str):
                status_str = project_data['status'].lower().replace(' ', '_')
                status_map = {
                    'construction': ProjectStatus.CONSTRUCTION,
                    'planning': ProjectStatus.PLANNING,
                    'approved': ProjectStatus.APPROVED,
                    'completed': ProjectStatus.COMPLETED,
                    'on_hold': ProjectStatus.ON_HOLD,
                    'cancelled': ProjectStatus.CANCELLED,
                    'approval_pending': ProjectStatus.APPROVAL_PENDING
                }
                if status_str in status_map:
                    project_data['status'] = status_map[status_str]
                elif status_str in [e.value for e in ProjectStatus]:
                    for ps in ProjectStatus:
                        if ps.value == status_str:
                            project_data['status'] = ps
                            break
            
            # 更新字段（只更新提供的字段）
            for key, value in project_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            session.commit()
            session.refresh(project)
            return project
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to update project: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def delete_project(self, project_id: int, session=None) -> bool:
        """
        删除项目
        
        注意：关联的transactions不会被自动删除，它们会保留但project_id将变为NULL
        如果需要同时删除关联的transactions，请先手动删除
        
        Args:
            project_id: 项目ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            bool: 如果删除成功返回True，如果项目不存在返回False
        
        Raises:
            Exception: 如果删除失败
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询项目
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            session.delete(project)
            session.commit()
            return True
        
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to delete project: {str(e)}")
        finally:
            if should_close:
                self.close_session(session)
    
    def get_project_by_id(self, project_id: int, session=None) -> Optional[Project]:
        """
        根据ID获取项目
        
        Args:
            project_id: 项目ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Optional[Project]: Project对象，如果不存在则返回None
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            project = session.query(Project).options(
                joinedload(Project.asset)
            ).filter(
                Project.id == project_id
            ).first()
            return project
        except Exception as e:
            print(f"Error getting project by id: {e}")
            return None
        finally:
            if should_close:
                self.close_session(session)
    
    def get_project_transactions(self, project_id: int, session=None) -> List[Transaction]:
        """
        获取项目的所有交易记录
        
        Args:
            project_id: 项目ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            List[Transaction]: 交易列表，按日期降序排列，返回空列表如果出错
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            transactions = session.query(Transaction).options(
                joinedload(Transaction.asset)
            ).filter(
                Transaction.project_id == project_id
            ).order_by(
                Transaction.transaction_date.desc(),
                Transaction.id.desc()
            ).all()
            return transactions
        except Exception as e:
            print(f"Error getting project transactions: {e}")
            return []
        finally:
            if should_close:
                self.close_session(session)
    
    def get_project_cost_summary(self, project_id: int, session=None) -> Dict:
        """
        获取项目成本汇总
        
        Args:
            project_id: 项目ID
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            Dict: 包含以下键的字典：
                - total_spent: 总支出（负数交易的绝对值）
                - transaction_count: 交易数量
                - budget: 预算
                - variance: 偏差（预算-实际）
                - variance_percentage: 偏差百分比
                如果项目不存在返回空dict
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询项目
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return {}
            
            # 查询所有关联的交易
            transactions = session.query(Transaction).filter(
                Transaction.project_id == project_id
            ).all()
            
            # 计算总支出（负数交易的绝对值，即所有支出交易的绝对值之和）
            total_spent = 0.0
            for trans in transactions:
                # 如果金额为负数（支出），取其绝对值
                if trans.amount < 0:
                    total_spent += abs(float(trans.amount))
            
            transaction_count = len(transactions)
            budget = float(project.total_budget) if project.total_budget else 0.0
            variance = budget - total_spent
            variance_percentage = (variance / budget * 100) if budget > 0 else 0.0
            
            return {
                "total_spent": total_spent,
                "transaction_count": transaction_count,
                "budget": budget,
                "variance": variance,
                "variance_percentage": variance_percentage
            }
        
        except Exception as e:
            print(f"Error getting project cost summary: {e}")
            return {}
        finally:
            if should_close:
                self.close_session(session)
    
    def get_projects_by_status(self, status: str, session=None) -> List[Project]:
        """
        按状态获取项目
        
        Args:
            status: 项目状态（字符串，将被转换为ProjectStatus枚举）
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            List[Project]: 项目列表，按创建时间降序排列，返回空列表如果出错
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 将字符串状态转换为枚举
            status_str = status.lower().replace(' ', '_')
            status_enum = None
            if status_str in [e.value for e in ProjectStatus]:
                for ps in ProjectStatus:
                    if ps.value == status_str:
                        status_enum = ps
                        break
            
            if status_enum is None:
                return []
            
            projects = session.query(Project).options(
                joinedload(Project.asset)
            ).filter(
                Project.status == status_enum
            ).order_by(
                Project.created_at.desc()
            ).all()
            return projects
        except Exception as e:
            print(f"Error getting projects by status: {e}")
            return []
        finally:
            if should_close:
                self.close_session(session)
    
    def get_active_projects_count(self, session=None) -> int:
        """
        获取活跃项目数量（status != 'Completed'）
        
        Args:
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            int: 活跃项目数量，如果出错返回0
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            count = session.query(Project).filter(
                Project.status != ProjectStatus.COMPLETED
            ).count()
            return count
        except Exception as e:
            print(f"Error getting active projects count: {e}")
            return 0
        finally:
            if should_close:
                self.close_session(session)
    
    def get_total_projects_budget(self, session=None) -> float:
        """
        获取所有项目的总预算
        
        Args:
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            float: 所有项目的总预算，如果出错返回0.0
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            result = session.query(func.sum(Project.total_budget)).scalar()
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error getting total projects budget: {e}")
            return 0.0
        finally:
            if should_close:
                self.close_session(session)
    
    def get_total_projects_cost(self, session=None) -> float:
        """
        获取所有项目的总实际成本
        
        从Transactions表计算所有项目相关的交易总支出
        
        Args:
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            float: 所有项目的总实际成本，如果出错返回0.0
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询所有有project_id的交易，计算负数交易的绝对值之和
            transactions = session.query(Transaction).filter(
                Transaction.project_id.isnot(None)
            ).all()
            
            total_cost = 0.0
            for trans in transactions:
                if trans.amount < 0:
                    total_cost += abs(float(trans.amount))
            
            return total_cost
        except Exception as e:
            print(f"Error getting total projects cost: {e}")
            return 0.0
        finally:
            if should_close:
                self.close_session(session)
    
    def get_average_completion(self, session=None) -> float:
        """
        获取所有项目的平均完成度
        
        基于预算使用率计算（actual_cost / total_budget * 100）
        只计算有预算的项目
        
        Args:
            session: 可选的数据库会话，如果为None则创建新会话
        
        Returns:
            float: 所有项目的平均完成度（百分比），如果出错或没有项目返回0.0
        """
        if session is None:
            session = self.get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # 查询所有有预算的项目
            projects = session.query(Project).filter(
                Project.total_budget.isnot(None),
                Project.total_budget > 0
            ).all()
            
            if not projects:
                return 0.0
            
            total_completion = 0.0
            valid_count = 0
            
            for project in projects:
                if project.total_budget and project.total_budget > 0:
                    actual_cost = float(project.actual_cost) if project.actual_cost else 0.0
                    budget = float(project.total_budget)
                    completion = (actual_cost / budget) * 100
                    total_completion += completion
                    valid_count += 1
            
            if valid_count == 0:
                return 0.0
            
            return total_completion / valid_count
        except Exception as e:
            print(f"Error getting average completion: {e}")
            return 0.0
        finally:
            if should_close:
                self.close_session(session)
    
    def log_api_usage(self, query_type, model_used, input_tokens, output_tokens, 
                      estimated_cost, question_hash=None, cached=False, question=None, session=None):
        """
        Log API usage for tracking and cost monitoring
        
        Args:
            query_type: Type of query (natural_query, quick_analysis, etc.)
            model_used: Model name (sonnet-4, haiku, etc.)
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            estimated_cost: Estimated cost in USD
            question_hash: Hash of question for similarity detection
            cached: Whether response was from cache
            question: Optional user question text
            session: Optional SQLAlchemy session
        
        Returns:
            APIUsage object
        """
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            usage = APIUsage(
                query_type=query_type,
                model_used=model_used,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=estimated_cost,
                question_hash=question_hash,
                response_cached=cached,
                user_question=question[:500] if question else None  # Limit length
            )
            session.add(usage)
            session.commit()
            return usage
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging API usage: {e}")
            return None
        finally:
            if managed_session:
                session.close()

    def get_monthly_api_usage(self, year=None, month=None, session=None):
        """
        Get API usage statistics for a given month
        
        Args:
            year: Year (default: current year)
            month: Month (default: current month)
            session: Optional SQLAlchemy session
        
        Returns:
            Dictionary with usage statistics
        """
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            from datetime import datetime
            if year is None or month is None:
                now = datetime.now()
                year = year or now.year
                month = month or now.month
            
            # Get first and last day of month
            from calendar import monthrange
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
            
            # Query usage
            usage_records = session.query(APIUsage).filter(
                APIUsage.timestamp >= first_day,
                APIUsage.timestamp <= last_day
            ).all()
            
            # Calculate statistics
            total_queries = len(usage_records)
            cached_queries = sum(1 for u in usage_records if u.response_cached)
            total_cost = sum(u.estimated_cost for u in usage_records)
            total_input_tokens = sum(u.input_tokens for u in usage_records)
            total_output_tokens = sum(u.output_tokens for u in usage_records)
            
            # By query type
            by_type = {}
            for record in usage_records:
                qtype = record.query_type or 'unknown'
                if qtype not in by_type:
                    by_type[qtype] = {'count': 0, 'cost': 0}
                by_type[qtype]['count'] += 1
                by_type[qtype]['cost'] += record.estimated_cost
            
            return {
                'total_queries': total_queries,
                'cached_queries': cached_queries,
                'api_queries': total_queries - cached_queries,
                'total_cost': total_cost,
                'total_input_tokens': total_input_tokens,
                'total_output_tokens': total_output_tokens,
                'by_type': by_type,
                'cache_hit_rate': (cached_queries / total_queries * 100) if total_queries > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting monthly API usage: {e}")
            return {
                'total_queries': 0,
                'cached_queries': 0,
                'api_queries': 0,
                'total_cost': 0.0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'by_type': {},
                'cache_hit_rate': 0
            }
        finally:
            if managed_session:
                session.close()

    def get_similar_questions(self, question_hash, limit=5, session=None):
        """
        Find similar questions by hash (for cache suggestion)
        
        Args:
            question_hash: Hash of the question
            limit: Maximum number of results
            session: Optional SQLAlchemy session
        
        Returns:
            List of similar APIUsage records
        """
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            similar = session.query(APIUsage).filter(
                APIUsage.question_hash == question_hash
            ).order_by(APIUsage.timestamp.desc()).limit(limit).all()
            
            return similar
        except Exception as e:
            logger.error(f"Error finding similar questions: {e}")
            return []
        finally:
            if managed_session:
                session.close()

    # ==================== Due Diligence Methods ====================

    def get_all_dd_projects(self, session=None):
        """Get all DD projects"""
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            projects = session.query(DDProject).order_by(DDProject.created_at.desc()).all()
            return projects
        except Exception as e:
            logger.error(f"Error getting DD projects: {e}")
            return []
        finally:
            if managed_session:
                session.close()

    def add_dd_project(self, project_data: dict, session=None):
        """Add new DD project"""
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            project = DDProject(**project_data)
            session.add(project)
            session.commit()
            session.refresh(project)
            return project
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding DD project: {e}")
            return None
        finally:
            if managed_session:
                session.close()

    def update_dd_project(self, project_id: int, project_data: dict, session=None):
        """Update DD project"""
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            project = session.query(DDProject).filter(DDProject.id == project_id).first()
            if project:
                for key, value in project_data.items():
                    if hasattr(project, key):
                        setattr(project, key, value)
                session.commit()
                session.refresh(project)
            return project
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating DD project: {e}")
            return None
        finally:
            if managed_session:
                session.close()

    def delete_dd_project(self, project_id: int, session=None):
        """Delete DD project"""
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            project = session.query(DDProject).filter(DDProject.id == project_id).first()
            if project:
                session.delete(project)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting DD project: {e}")
            return False
        finally:
            if managed_session:
                session.close()

    def get_dd_project_by_id(self, project_id: int, session=None):
        """Get DD project by ID with relationships"""
        managed_session = session is None
        if managed_session:
            session = self.get_session()
        
        try:
            project = session.query(DDProject).options(
                joinedload(DDProject.scenarios),
                joinedload(DDProject.assumptions)
            ).filter(DDProject.id == project_id).first()
            return project
        except Exception as e:
            logger.error(f"Error getting DD project: {e}")
            return None
        finally:
            if managed_session:
                session.close()


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