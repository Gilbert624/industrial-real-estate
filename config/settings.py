python"""
系统配置文件
"""

# 数据库配置
DATABASE_URL = "sqlite:///data/assets.db"

# 应用配置
APP_TITLE = "Asset Management System"
APP_VERSION = "0.1.0-dev"
DEVELOPER = "Gilbert - Brisbane Industrial Developer"

# 页面配置
PAGE_ICON = "🏢"
LAYOUT = "wide"

# 业务配置
DEFAULT_CURRENCY = "AUD"
REGIONS = ["Brisbane", "Sunshine Coast"]
ASSET_TYPES = ["Industrial Warehouse", "Land", "Mixed Use"]

# 开发环境
DEBUG = True