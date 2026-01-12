# 📈 市场情报模块使用指南
# Market Intelligence Module User Guide

## 📋 目录

1. [模块概述](#overview)
2. [数据源说明](#data-sources)
3. [使用教程](#tutorial)
4. [数据更新策略](#update-strategy)
5. [最佳实践](#best-practices)
6. [故障排除](#troubleshooting)

---

## 🎯 模块概述 {#overview}

市场情报模块集成了6个免费的官方数据源，提供：

### 核心功能

✅ **市场概览**
- Brisbane和Sunshine Coast工业地产市场实时数据
- 租金趋势分析
- 空置率监控
- 新增供应追踪

✅ **经济指标追踪**
- GDP增长率
- 失业率
- RBA现金利率
- 澳元汇率
- 建筑审批数据

✅ **开发项目监控**
- Queensland开发审批
- 竞争对手项目追踪
- 基础设施项目影响分析

✅ **租金数据管理**
- 手动录入租金数据
- 区域对比分析
- 历史趋势追踪

✅ **竞争对手分析**
- 主要开发商追踪
- 投资组合对比
- 优劣势分析

---

## 🌐 数据源说明 {#data-sources}

### 1. ABS (Australian Bureau of Statistics)

**数据类型：** 宏观经济指标

**包含内容：**
- GDP增长率（季度）
- 失业率（月度）
- 建筑审批数量（月度）

**更新频率：**
- GDP：每季度
- 失业率：每月
- 建筑审批：每月

**如何使用：**
```python
from utils.market_data_collector import MarketDataCollector

collector = MarketDataCollector()

# 获取GDP数据
gdp_data = collector.get_gdp_data()
print(f"当前GDP增长: {gdp_data['current_gdp_growth']}%")

# 获取失业率
unemployment = collector.get_unemployment_data()
print(f"失业率: {unemployment['current_rate']}%")

# 获取建筑审批
approvals = collector.get_building_approvals()
print(f"本月工业审批: {approvals['industrial_approvals_qld']}个")
```

**手动更新方法：**
1. 访问 https://www.abs.gov.au
2. 查找最新数据
3. 在代码中更新数值

**数据来源链接：**
- GDP数据：https://www.abs.gov.au/statistics/economy/national-accounts
- 失业率：https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia
- 建筑审批：https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia

---

### 2. RBA (Reserve Bank of Australia)

**数据类型：** 金融指标

**包含内容：**
- 官方现金利率
- 澳元汇率（AUD/USD, AUD/CNY等）

**更新频率：**
- 现金利率：每月（RBA会议后）
- 汇率：每日

**如何使用：**
```python
# 获取现金利率
cash_rate = collector.get_cash_rate()
print(f"当前利率: {cash_rate['current_rate']}%")
print(f"下次会议: {cash_rate['next_meeting']}")

# 获取汇率
exchange = collector.get_exchange_rate()
print(f"AUD/USD: {exchange['aud_usd']}")
print(f"AUD/CNY: {exchange['aud_cny']}")
```

**数据来源：**
- 现金利率：https://www.rba.gov.au/statistics/cash-rate/
- 汇率：https://www.rba.gov.au/statistics/frequency/exchange-rates.html

---

### 3. Queensland Open Data

**数据类型：** 区域开发数据

**包含内容：**
- 开发审批记录
- 基础设施项目
- 土地规划信息

**更新频率：** 不定期（有新审批时更新）

**如何使用：**
```python
# 获取开发审批
approvals = collector.get_qld_development_approvals(region='Brisbane')
for project in approvals:
    print(f"项目: {project['project_name']}")
    print(f"面积: {project['size_sqm']} sqm")
    print(f"状态: {project['status']}")

# 获取基础设施项目
infra = collector.get_qld_infrastructure_projects()
for proj in infra:
    print(f"{proj['project_name']} - 投资 ${proj['investment']:,.0f}")
```

**数据来源：**
- https://www.data.qld.gov.au

---

### 4. World Bank Open Data

**数据类型：** 国际对比数据

**包含内容：**
- 澳大利亚经济指标
- 全球对比数据

**更新频率：** 年度

**如何使用：**
```python
# 获取World Bank数据
wb_data = collector.get_world_bank_data(indicator='NY.GDP.MKTP.KD.ZG')
print(f"GDP增长: {wb_data['value']}%")
print(f"年份: {wb_data['year']}")
```

**常用指标代码：**
- `NY.GDP.MKTP.KD.ZG` - GDP增长率
- `SL.UEM.TOTL.ZS` - 失业率

**数据来源：**
- https://data.worldbank.org/country/australia

---

### 5. OECD Data

**数据类型：** OECD国家对比

**包含内容：**
- 澳大利亚 vs OECD平均
- 经济指标对比

**更新频率：** 季度

**如何使用：**
```python
# 获取OECD数据
oecd_data = collector.get_oecd_data()
print(f"OECD平均GDP: {oecd_data['gdp_growth_oecd_avg']}%")
print(f"澳大利亚GDP: {oecd_data['australia_gdp_growth']}%")
print(f"差异: {oecd_data['australia_vs_oecd']}%")
```

**数据来源：**
- https://data.oecd.org/australia.htm

---

### 6. Brisbane City Council

**数据类型：** Brisbane本地数据

**包含内容：**
- 开发申请（DA）
- 建筑许可
- 规划信息

**更新频率：** 实时（有新申请时）

**如何使用：**
```python
# 获取开发申请
applications = collector.get_bcc_development_applications()
for app in applications:
    print(f"申请ID: {app['application_id']}")
    print(f"地址: {app['address']}")
    print(f"状态: {app['status']}")
```

**数据来源：**
- https://www.brisbane.qld.gov.au/planning-and-building

---

## 📖 使用教程 {#tutorial}

### 快速开始（5分钟）

#### 步骤1：访问市场情报模块

1. 打开应用
2. 在侧边栏点击 **"📈 Market Intelligence"**
3. 等待页面加载

---

#### 步骤2：收集初始数据

1. 切换到 **"⚙️ Data Management"** 标签
2. 点击 **"🔄 Collect All Data"** 按钮
3. 等待数据收集完成（约10-15秒）
4. 看到 "✅ All market data collected successfully!"

---

#### 步骤3：查看市场概览

1. 返回 **"📊 Market Overview"** 标签
2. 查看关键指标卡片
3. 浏览租金趋势图表
4. 查看空置率对比
5. 检查新增供应管道

---

#### 步骤4：添加租金数据

1. 切换到 **"💰 Rental Data"** 标签
2. 点击 **"➕ Add Rental Data"**
3. 填写表单：
   - 区域：选择 Brisbane CBD / Port of Brisbane 等
   - 物业类型：Industrial Warehouse
   - 平均租金：$120/sqm/year
   - 空置率：3.5%
   - 数据来源：Domain / RealCommercial
4. 点击 **"Save Data"**

---

#### 步骤5：追踪竞争对手

1. 切换到 **"🎯 Competitors"** 标签
2. 点击 **"➕ Add Competitor"**
3. 填写竞争对手信息：
   - 名称：Goodman Group
   - 区域：Brisbane
   - 投资组合规模：500,000 sqm
   - 平均租金：$125/sqm/year
   - 优势：全球网络、大型租户关系
   - 劣势：价格较高
4. 保存

---

### 每周例行工作（15分钟）

**建议每周一早上执行：**

#### 1. 更新自动数据（5分钟）
```
⚙️ Data Management Tab
→ 点击 "🔄 Collect All Data"
→ 等待完成
→ 查看更新摘要
```

#### 2. 检查开发项目（5分钟）
```
🏗️ Development Projects Tab
→ 查看新增审批
→ 追踪竞争对手项目
→ 记录基础设施项目进展
```

#### 3. 更新租金数据（5分钟）
```
💰 Rental Data Tab
→ 检查Domain/RealCommercial最新租金
→ 添加新数据点
→ 查看趋势变化
```

---

### 每月深度分析（30分钟）

**建议每月第一个工作日执行：**

#### 1. 经济指标分析（10分钟）
```
💹 Economic Indicators Tab
→ 查看GDP、失业率变化
→ 分析利率趋势
→ 对比OECD数据
```

#### 2. 竞争对手分析（10分钟）
```
🎯 Competitors Tab
→ 更新竞争对手投资组合
→ 记录新交易活动
→ 分析市场动态
```

#### 3. 市场报告生成（10分钟）
```
📊 Market Overview Tab
→ 截图关键图表
→ 整理数据摘要
→ 准备月度报告
```

---

## 🔄 数据更新策略 {#update-strategy}

### 自动化数据收集

**频率建议：**
- **每日：** 汇率数据（如果需要）
- **每周：** 完整数据收集
- **每月：** 深度数据更新和分析

### 手动数据管理

**需要手动更新的数据：**
- 租金数据（从Domain、RealCommercial等收集）
- 竞争对手信息（从公开报告、新闻等）
- 开发项目详情（从政府网站、新闻等）

### 数据缓存机制

系统使用1小时缓存机制，避免频繁API调用：
- 相同数据在1小时内不会重复获取
- 可以手动刷新获取最新数据
- 缓存数据保存在内存中

---

## 💡 最佳实践 {#best-practices}

### 1. 数据收集

✅ **推荐做法：**
- 每周固定时间收集数据（如周一上午）
- 建立数据收集检查清单
- 记录数据来源和时间戳
- 定期验证数据准确性

❌ **避免做法：**
- 过度频繁的数据收集（浪费资源）
- 忽略数据来源标注
- 使用过时数据做决策

### 2. 租金数据管理

✅ **推荐做法：**
- 记录数据来源（Domain、RealCommercial等）
- 注明样本大小和统计周期
- 区分不同物业类型和面积范围
- 定期更新历史数据

❌ **避免做法：**
- 混合不同来源数据而不标注
- 忽略样本偏差
- 不记录数据收集日期

### 3. 竞争对手分析

✅ **推荐做法：**
- 定期更新竞争对手投资组合
- 记录所有相关交易和活动
- 保持客观分析，避免偏见
- 关注市场动态和趋势

❌ **避免做法：**
- 仅基于单次数据点做判断
- 忽略竞争对手的优势
- 不及时更新信息

### 4. 数据使用

✅ **推荐做法：**
- 结合多个数据源做决策
- 关注趋势而非单点数据
- 定期回顾和更新分析
- 与团队分享关键发现

❌ **避免做法：**
- 过度依赖单一数据源
- 忽略数据的时间性
- 不验证数据准确性

---

## 🔧 故障排除 {#troubleshooting}

### 常见问题

#### 1. 数据收集失败

**症状：** 点击"Collect All Data"后显示错误

**可能原因：**
- API端点暂时不可用
- 网络连接问题
- API格式变化

**解决方法：**
1. 检查网络连接
2. 等待几分钟后重试
3. 检查各个数据源网站是否可访问
4. 查看控制台错误信息
5. 如果问题持续，检查代码中的API端点

---

#### 2. 数据不更新

**症状：** 数据显示过时

**可能原因：**
- 缓存未过期（1小时缓存）
- 数据源未更新
- 手动数据未录入

**解决方法：**
1. 等待缓存过期（1小时）
2. 手动刷新页面
3. 检查数据源网站是否有新数据
4. 手动更新相关数据

---

#### 3. 图表不显示

**症状：** 图表区域空白

**可能原因：**
- 数据不足
- Plotly渲染问题
- 浏览器兼容性

**解决方法：**
1. 检查是否有足够的数据点
2. 刷新页面
3. 清除浏览器缓存
4. 检查浏览器控制台错误

---

#### 4. 数据库错误

**症状：** 无法保存租金数据或竞争对手信息

**可能原因：**
- 数据库连接问题
- 表结构不匹配
- 权限问题

**解决方法：**
1. 检查数据库文件是否存在
2. 查看错误消息详情
3. 运行数据库迁移脚本（如果需要）
4. 检查文件权限

---

### 技术支持

如果遇到其他问题：

1. **查看日志：** 检查应用日志文件
2. **检查代码：** 查看 `utils/market_data_collector.py` 和 `pages/6_📈_Market_Intelligence.py`
3. **数据源状态：** 访问各个数据源网站确认服务状态
4. **文档参考：** 查看各个数据源的API文档

---

## 📚 参考资源

### 官方文档

- **ABS API文档：** https://www.abs.gov.au/about/data-services/application-programming-interfaces-apis
- **RBA统计：** https://www.rba.gov.au/statistics/
- **Queensland Open Data：** https://www.data.qld.gov.au/article/standards-and-guidance/api-introduction
- **World Bank API：** https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- **OECD API：** https://data.oecd.org/api/

### 相关模块

- **资产管理模块：** 管理自有资产信息
- **财务模块：** 财务分析和报表
- **项目模块：** 开发项目跟踪
- **AI助手模块：** 数据分析和洞察

---

## 📝 更新日志

### Version 1.0 (2026-01-XX)

- ✅ 初始版本发布
- ✅ 集成6个数据源
- ✅ 实现数据收集和管理功能
- ✅ 添加市场概览和竞争分析

---

## 🤝 贡献指南

如果你发现数据源问题或有改进建议：

1. 记录问题详情（错误消息、数据源、时间）
2. 检查是否是新问题还是已知问题
3. 如果可能，提供修复建议
4. 更新相关文档

---

**最后更新：** 2026-01-XX  
**维护者：** Asset Management Team  
**版本：** 1.0
