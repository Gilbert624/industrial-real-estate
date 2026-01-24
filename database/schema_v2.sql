-- Schema v2 for Industrial Real Estate Asset Management
-- Targets SQLite
PRAGMA foreign_keys = ON;

-- ============================================================
-- Core Entities
-- ============================================================

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    asset_type TEXT,
    status TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    suburb TEXT,
    state TEXT,
    postcode TEXT,
    region TEXT,
    land_area_sqm REAL,
    building_area_sqm REAL,
    warehouse_area_sqm REAL,
    office_area_sqm REAL,
    clear_height_meters REAL,
    power_capacity_kva REAL,
    loading_docks INTEGER,
    car_parking_spaces INTEGER,
    purchase_price NUMERIC(15, 2),
    purchase_date DATE,
    current_valuation NUMERIC(15, 2),
    valuation_date DATE,
    zoning TEXT,
    council TEXT,
    description TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    project_name TEXT NOT NULL,
    project_code TEXT UNIQUE,
    status TEXT,
    description TEXT,
    scope_of_work TEXT,
    planned_start_date DATE,
    actual_start_date DATE,
    planned_completion_date DATE,
    actual_completion_date DATE,
    total_budget NUMERIC(15, 2),
    actual_cost NUMERIC(15, 2),
    contingency_budget NUMERIC(15, 2),
    project_manager TEXT,
    contractor TEXT,
    architect TEXT,
    engineer TEXT,
    key_milestones TEXT,
    da_number TEXT,
    da_approval_date DATE,
    building_approval_date DATE,
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    project_id INTEGER,
    transaction_date DATE NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'AUD',
    gst_amount NUMERIC(15, 2) DEFAULT 0,
    category TEXT,
    expense_category TEXT,
    description TEXT NOT NULL,
    reference_number TEXT,
    vendor_payee TEXT,
    payment_method TEXT,
    bank_account TEXT,
    is_reconciled BOOLEAN NOT NULL DEFAULT 0,
    reconciliation_date DATE,
    notes TEXT,
    attachments TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- ============================================================
-- Consultants & Quotes
-- ============================================================

CREATE TABLE IF NOT EXISTS consultants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    email TEXT,
    phone TEXT,
    specialty TEXT,
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultant_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultant_id INTEGER NOT NULL,
    asset_id INTEGER,
    project_id INTEGER,
    quote_date DATE,
    valid_until DATE,
    amount NUMERIC(15, 2),
    currency TEXT NOT NULL DEFAULT 'AUD',
    status TEXT,
    scope TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultant_id) REFERENCES consultants(id),
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- ============================================================
-- Monthly Expenses
-- ============================================================

CREATE TABLE IF NOT EXISTS monthly_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    project_id INTEGER,
    expense_month INTEGER NOT NULL,
    expense_year INTEGER NOT NULL,
    category TEXT,
    amount NUMERIC(15, 2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'AUD',
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- ============================================================
-- Import History
-- ============================================================

CREATE TABLE IF NOT EXISTS import_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    file_name TEXT,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    records_imported INTEGER NOT NULL DEFAULT 0,
    status TEXT,
    error_message TEXT,
    checksum TEXT,
    notes TEXT
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_projects_asset ON projects(asset_id);
CREATE INDEX IF NOT EXISTS idx_projects_asset_id ON projects(asset_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

CREATE INDEX IF NOT EXISTS idx_transactions_asset ON transactions(asset_id);
CREATE INDEX IF NOT EXISTS idx_transactions_project ON transactions(project_id);
CREATE INDEX IF NOT EXISTS idx_transactions_asset_id ON transactions(asset_id);
CREATE INDEX IF NOT EXISTS idx_transactions_project_id ON transactions(project_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);

CREATE INDEX IF NOT EXISTS idx_consultant_quotes_consultant_id ON consultant_quotes(consultant_id);
CREATE INDEX IF NOT EXISTS idx_consultant_quotes_asset_id ON consultant_quotes(asset_id);
CREATE INDEX IF NOT EXISTS idx_consultant_quotes_project_id ON consultant_quotes(project_id);

CREATE INDEX IF NOT EXISTS idx_monthly_expenses_asset_id ON monthly_expenses(asset_id);
CREATE INDEX IF NOT EXISTS idx_monthly_expenses_project_id ON monthly_expenses(project_id);
CREATE INDEX IF NOT EXISTS idx_monthly_expenses_period ON monthly_expenses(expense_year, expense_month);
