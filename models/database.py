"""
Database models and manager for Industrial Real Estate Management System
工业地产管理系统数据库模型和管理器

Last updated: 2026-01-13
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, func, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

# ==================== Core Models ====================

class Asset(Base):
    """资产模型"""
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    asset_type = Column(String(100))
    region = Column(String(100))
    address = Column(Text)
    land_area_sqm = Column(Float)
    building_area_sqm = Column(Float)
    current_valuation = Column(Float)
    acquisition_date = Column(DateTime)
    status = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    """交易模型"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_type = Column(String(50), nullable=False)
    category = Column(String(100))
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    """项目模型"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    project_type = Column(String(100))
    location = Column(String(200))
    budget = Column(Float)
    actual_cost = Column(Float)
    completion_percentage = Column(Float, default=0)
    start_date = Column(DateTime)
    estimated_completion = Column(DateTime)
    status = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DDProject(Base):
    """尽职调查项目模型"""
    __tablename__ = 'dd_projects'
    
    id = Column(Integer, primary_key=True)
    project_name = Column(String(200), nullable=False)
    location = Column(String(200))
    property_type = Column(String(100))
    purchase_price = Column(Float)
    status = Column(String(50), default='Under Review')
    
    # Parameters (JSON stored as Text)
    parameters = Column(Text)
    
    # Calculated metrics (JSON stored as Text)
    metrics = Column(Text)
    
    # Scenarios (JSON stored as Text)
    scenarios = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== Market Intelligence Models ====================

class MarketIndicator(Base):
    """市场指标数据"""
    __tablename__ = 'market_indicators'
    
    id = Column(Integer, primary_key=True)
    indicator_type = Column(String(100))
    region = Column(String(100))
    value = Column(Float)
    previous_value = Column(Float, nullable=True)
    change_percentage = Column(Float, nullable=True)
    period = Column(String(50))
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100))
    source_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DevelopmentProject(Base):
    """开发项目追踪"""
    __tablename__ = 'development_projects'
    
    id = Column(Integer, primary_key=True)
    project_name = Column(String(200))
    developer = Column(String(200), nullable=True)
    location = Column(String(200))
    region = Column(String(100))
    project_type = Column(String(100))
    size_sqm = Column(Float, nullable=True)
    estimated_value = Column(Float, nullable=True)
    status = Column(String(100))
    approval_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    is_competitor = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RentalData(Base):
    """租金数据"""
    __tablename__ = 'rental_data'
    
    id = Column(Integer, primary_key=True)
    region = Column(String(100))
    property_type = Column(String(100))
    size_category = Column(String(50))
    average_rent_per_sqm = Column(Float)
    min_rent = Column(Float, nullable=True)
    max_rent = Column(Float, nullable=True)
    vacancy_rate = Column(Float, nullable=True)
    sample_size = Column(Integer, nullable=True)
    period = Column(String(50))
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InfrastructureProject(Base):
    """基础设施项目"""
    __tablename__ = 'infrastructure_projects'
    
    id = Column(Integer, primary_key=True)
    project_name = Column(String(200))
    region = Column(String(100))
    project_type = Column(String(100))
    investment_amount = Column(Float, nullable=True)
    status = Column(String(100))
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    impact_on_industrial = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompetitorAnalysis(Base):
    """竞争对手分析"""
    __tablename__ = 'competitor_analysis'
    
    id = Column(Integer, primary_key=True)
    competitor_name = Column(String(200))
    region = Column(String(100))
    portfolio_size_sqm = Column(Float, nullable=True)
    number_of_properties = Column(Integer, nullable=True)
    average_rent = Column(Float, nullable=True)
    occupancy_rate = Column(Float, nullable=True)
    recent_activity = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    period = Column(String(50))
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== Database Manager ====================

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path=None):
        """Initialize database manager"""
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'industrial_real_estate.db')
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建所有表
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ Database tables initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing database tables: {e}")
    
    def _get_session(self):
        """获取数据库会话（私有方法）"""
        return self.Session()
    
    def get_session(self):
        """获取数据库会话（公共方法）"""
        return self.Session()
    
    # ==================== Asset Methods ====================
    
    def add_asset(self, asset_data):
        """添加资产"""
        session = self._get_session()
        try:
            asset = Asset(**asset_data)
            session.add(asset)
            session.commit()
            return asset
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_assets(self, session=None):
        """获取所有资产"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            return session.query(Asset).all()
        finally:
            if close_session:
                session.close()
    
    def get_all_assets_for_dropdown(self, session=None):
        """获取所有资产用于下拉菜单（返回字典列表）"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            assets = session.query(Asset).all()
            return [{'id': asset.id, 'name': asset.name} for asset in assets]
        finally:
            if close_session:
                session.close()
    
    def get_asset_by_id(self, asset_id):
        """根据ID获取资产"""
        session = self._get_session()
        try:
            return session.query(Asset).filter(Asset.id == asset_id).first()
        finally:
            session.close()
    
    def update_asset(self, asset_id, asset_data):
        """更新资产"""
        session = self._get_session()
        try:
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            if asset:
                for key, value in asset_data.items():
                    setattr(asset, key, value)
                session.commit()
            return asset
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_asset(self, asset_id):
        """删除资产"""
        session = self._get_session()
        try:
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            if asset:
                session.delete(asset)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== Transaction Methods ====================
    
    def add_transaction(self, transaction_data):
        """添加交易"""
        session = self._get_session()
        try:
            transaction = Transaction(**transaction_data)
            session.add(transaction)
            session.commit()
            return transaction
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_transactions(self, session=None):
        """获取所有交易"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            return session.query(Transaction).order_by(Transaction.date.desc()).all()
        finally:
            if close_session:
                session.close()
    
    def get_recent_transactions(self, limit=10, session=None):
        """获取最近的交易"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            return session.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()
        finally:
            if close_session:
                session.close()
    
    def get_cash_balance(self, session=None):
        """获取现金余额"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            transactions = session.query(Transaction).all()
            balance = 0
            for t in transactions:
                if t.transaction_type == 'Income':
                    balance += t.amount
                else:
                    balance -= t.amount
            return balance
        finally:
            if close_session:
                session.close()
    
    def get_monthly_income(self, year, month, session=None):
        """获取指定年月的收入总和"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            result = session.query(func.sum(Transaction.amount)).filter(
                Transaction.transaction_type == 'Income',
                extract('year', Transaction.date) == year,
                extract('month', Transaction.date) == month
            ).scalar()
            return float(result) if result else 0.0
        finally:
            if close_session:
                session.close()
    
    def get_monthly_expense(self, year, month, session=None):
        """获取指定年月的支出总和（返回绝对值）"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            result = session.query(func.sum(Transaction.amount)).filter(
                Transaction.transaction_type == 'Expense',
                extract('year', Transaction.date) == year,
                extract('month', Transaction.date) == month
            ).scalar()
            # 支出可能以负数存储，返回绝对值
            return abs(float(result)) if result else 0.0
        finally:
            if close_session:
                session.close()
    
    def get_cashflow_trend(self, months=6, session=None):
        """获取现金流趋势数据（最近N个月）"""
        from datetime import timedelta
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            trend_data = []
            current_date = datetime.now()
            
            for i in range(months):
                # 计算目标月份
                target_date = current_date - timedelta(days=30 * (months - i - 1))
                year = target_date.year
                month = target_date.month
                
                # 查询收入
                income_result = session.query(func.sum(Transaction.amount)).filter(
                    Transaction.transaction_type == 'Income',
                    extract('year', Transaction.date) == year,
                    extract('month', Transaction.date) == month
                ).scalar()
                income = float(income_result) if income_result else 0.0
                
                # 查询支出
                expense_result = session.query(func.sum(Transaction.amount)).filter(
                    Transaction.transaction_type == 'Expense',
                    extract('year', Transaction.date) == year,
                    extract('month', Transaction.date) == month
                ).scalar()
                # 支出可能以负数存储，返回绝对值
                expense = abs(float(expense_result)) if expense_result else 0.0
                
                # 计算净现金流
                net = income - expense
                
                trend_data.append({
                    'year': year,
                    'month': month,
                    'income': income,
                    'expense': expense,
                    'net': net
                })
            
            return trend_data
        finally:
            if close_session:
                session.close()
    
    # ==================== Project Methods ====================
    
    def add_project(self, project_data):
        """添加项目"""
        session = self._get_session()
        try:
            project = Project(**project_data)
            session.add(project)
            session.commit()
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_projects(self, session=None):
        """获取所有项目"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            return session.query(Project).all()
        finally:
            if close_session:
                session.close()
    
    def get_active_projects_count(self, session=None):
        """获取活跃项目数量"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            return session.query(Project).filter(
                Project.status.in_(['Planning', 'Construction', 'Under Review'])
            ).count()
        finally:
            if close_session:
                session.close()
    
    def get_total_projects_budget(self, session=None):
        """获取所有项目的总预算"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            result = session.query(func.sum(Project.budget)).scalar()
            return float(result) if result else 0.0
        finally:
            if close_session:
                session.close()
    
    def get_total_projects_cost(self, session=None):
        """获取所有项目的总成本"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            result = session.query(func.sum(Project.actual_cost)).scalar()
            return float(result) if result else 0.0
        finally:
            if close_session:
                session.close()
    
    def get_average_completion(self, session=None):
        """获取所有项目的平均完成度"""
        close_session = False
        if session is None:
            session = self._get_session()
            close_session = True
        
        try:
            result = session.query(func.avg(Project.completion_percentage)).scalar()
            return float(result) if result else 0.0
        finally:
            if close_session:
                session.close()
    
    def update_project(self, project_id, project_data):
        """更新项目"""
        session = self._get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                for key, value in project_data.items():
                    setattr(project, key, value)
                session.commit()
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_project(self, project_id):
        """删除项目"""
        session = self._get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                session.delete(project)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== DD Project Methods ====================
    
    def add_dd_project(self, project_data):
        """添加DD项目"""
        session = self._get_session()
        try:
            project = DDProject(**project_data)
            session.add(project)
            session.commit()
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_dd_projects(self):
        """获取所有DD项目"""
        session = self._get_session()
        try:
            return session.query(DDProject).order_by(DDProject.created_at.desc()).all()
        finally:
            session.close()
    
    def get_dd_project_by_id(self, project_id):
        """根据ID获取DD项目"""
        session = self._get_session()
        try:
            return session.query(DDProject).filter(DDProject.id == project_id).first()
        finally:
            session.close()
    
    def update_dd_project(self, project_id, project_data):
        """更新DD项目"""
        session = self._get_session()
        try:
            project = session.query(DDProject).filter(DDProject.id == project_id).first()
            if project:
                for key, value in project_data.items():
                    setattr(project, key, value)
                session.commit()
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_dd_project(self, project_id):
        """删除DD项目"""
        session = self._get_session()
        try:
            project = session.query(DDProject).filter(DDProject.id == project_id).first()
            if project:
                session.delete(project)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== Market Intelligence Methods ====================
    
    def add_market_indicator(self, indicator_data):
        """添加市场指标"""
        session = self._get_session()
        try:
            indicator = MarketIndicator(**indicator_data)
            session.add(indicator)
            session.commit()
            return indicator
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_latest_indicators(self, indicator_type=None, region=None, limit=10):
        """获取最新的市场指标"""
        session = self._get_session()
        try:
            query = session.query(MarketIndicator).order_by(MarketIndicator.date.desc())
            
            if indicator_type:
                query = query.filter(MarketIndicator.indicator_type == indicator_type)
            if region:
                query = query.filter(MarketIndicator.region == region)
            
            return query.limit(limit).all()
        finally:
            session.close()
    
    def add_development_project(self, project_data):
        """添加开发项目"""
        session = self._get_session()
        try:
            project = DevelopmentProject(**project_data)
            session.add(project)
            session.commit()
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_development_projects(self, region=None, status=None, is_competitor=None):
        """获取开发项目"""
        session = self._get_session()
        try:
            query = session.query(DevelopmentProject).order_by(DevelopmentProject.created_at.desc())
            
            if region:
                query = query.filter(DevelopmentProject.region == region)
            if status:
                query = query.filter(DevelopmentProject.status == status)
            if is_competitor is not None:
                query = query.filter(DevelopmentProject.is_competitor == is_competitor)
            
            return query.all()
        finally:
            session.close()
    
    def add_rental_data(self, rental_data):
        """添加租金数据"""
        session = self._get_session()
        try:
            rental = RentalData(**rental_data)
            session.add(rental)
            session.commit()
            return rental
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_rental_data(self, region=None, property_type=None, limit=10):
        """获取租金数据"""
        session = self._get_session()
        try:
            query = session.query(RentalData).order_by(RentalData.date.desc())
            
            if region:
                query = query.filter(RentalData.region == region)
            if property_type:
                query = query.filter(RentalData.property_type == property_type)
            
            return query.limit(limit).all()
        finally:
            session.close()
    
    def add_infrastructure_project(self, project_data):
        """添加基础设施项目"""
        session = self._get_session()
        try:
            project = InfrastructureProject(**project_data)
            session.add(project)
            session.commit()
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_infrastructure_projects(self, region=None):
        """获取基础设施项目"""
        session = self._get_session()
        try:
            query = session.query(InfrastructureProject).order_by(InfrastructureProject.created_at.desc())
            
            if region:
                query = query.filter(InfrastructureProject.region == region)
            
            return query.all()
        finally:
            session.close()
    
    def add_competitor_analysis(self, analysis_data):
        """添加竞争对手分析"""
        session = self._get_session()
        try:
            analysis = CompetitorAnalysis(**analysis_data)
            session.add(analysis)
            session.commit()
            return analysis
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_competitor_analysis(self, region=None):
        """获取竞争对手分析"""
        session = self._get_session()
        try:
            query = session.query(CompetitorAnalysis).order_by(CompetitorAnalysis.date.desc())
            
            if region:
                query = query.filter(CompetitorAnalysis.region == region)
            
            return query.all()
        finally:
            session.close()
