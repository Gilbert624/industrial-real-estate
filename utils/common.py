实用工具函数
"""

def format_currency(amount):
    """格式化货币显示"""
    return f"${amount:,.0f} AUD"

def get_system_info():
    """获取系统信息"""
    return {
        "version": "0.1.0-dev",
        "developer": "Gilbert - Brisbane",
        "region": "Queensland, Australia"
    }