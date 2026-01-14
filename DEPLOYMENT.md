# Streamlit Cloud 部署指南

## 准备工作

### 1. 准备GitHub仓库

确保您的代码已推送到GitHub：
```bash
# 如果还没有远程仓库
git remote add origin https://github.com/您的用户名/industrial-real-estate.git
git branch -M main
git push -u origin main
```

### 2. 准备必要文件

确保以下文件存在且正确：

- ✅ `requirements.txt` - 所有依赖
- ✅ `app.py` - 主应用入口
- ✅ `.streamlit/config.toml` - 配置文件
- ✅ `.gitignore` - 忽略敏感文件

### 3. 创建secrets配置

创建 `.streamlit/secrets.toml`（本地测试用，不提交到Git）：
```toml
# API Keys
ANTHROPIC_API_KEY = "your_api_key_here"

# Database (生产环境可以用PostgreSQL)
[database]
type = "sqlite"
path = "production_data.db"

# App Config
[app]
env = "production"
debug = false
```

## 部署步骤

### Step 1: 访问Streamlit Cloud

1. 前往 https://streamlit.io/cloud
2. 点击 "Sign up" 或 "Sign in"
3. 使用GitHub账号登录

### Step 2: 创建新应用

1. 点击 "New app"
2. 选择您的GitHub仓库
3. 选择分支（main）
4. 选择主文件（app.py）
5. 点击 "Deploy"

### Step 3: 配置Secrets

在Streamlit Cloud控制台：

1. 进入应用设置
2. 找到 "Secrets" 部分
3. 粘贴您的secrets配置：
```toml
ANTHROPIC_API_KEY = "sk-ant-your-actual-key"

[database]
type = "sqlite"
path = "production_data.db"

[app]
env = "production"
debug = false
```

4. 保存

#### 验证 API Key 配置

**在 Streamlit Cloud 中验证：**

1. 在 Streamlit Cloud 控制台
2. 点击 "Settings" → "Secrets"
3. 确认有以下配置：
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. 确认 API key 格式正确（应以 `sk-ant-` 开头）

**在 Anthropic 控制台验证：**

1. 访问 https://console.anthropic.com
2. 登录您的账户
3. 进入 "API Keys" 页面
4. 检查 API key 状态：
   - ✅ 确认 key 是 "Active" 状态
   - ✅ 确认有足够的额度（credits）
   - ✅ 确认 key 没有过期

**本地验证（可选）：**

运行验证脚本测试 API key 是否有效：
```bash
python verify_api_key.py
```

如果 API key 有问题：
- 在 Anthropic 控制台重新生成新的 API key
- 更新 Streamlit Cloud Secrets 中的配置
- 重新部署应用

### Step 4: 等待部署完成

- 部署通常需要2-5分钟
- 可以在日志中查看进度
- 部署完成后会显示应用URL

### Step 5: 测试应用

访问您的应用URL：
```
https://your-app-name.streamlit.app
```

## 性能优化

### 缓存策略

应用已实现 Streamlit 缓存机制以提升性能：

#### 1. 数据缓存 (`@st.cache_data`)

用于缓存数据库查询结果，减少重复查询：

```python
@st.cache_data(ttl=3600)  # 缓存1小时
def load_data():
    # 缓存1小时的数据查询
    pass

@st.cache_data(ttl=300)  # 缓存5分钟
def get_recent_transactions():
    # 缓存5分钟，因为交易数据更新较频繁
    pass
```

**缓存时间建议：**
- 投资组合指标：1小时 (3600秒)
- 筛选选项：1小时 (3600秒)
- 趋势数据：1小时 (3600秒)
- 最近交易：5分钟 (300秒)

#### 2. 资源缓存 (`@st.cache_resource`)

用于缓存数据库连接等资源，避免重复创建：

```python
@st.cache_resource
def init_connection():
    # 永久缓存资源（数据库连接、模型等）
    pass
```

**适用场景：**
- 数据库连接
- 机器学习模型
- 外部API客户端
- 其他需要保持状态的资源

### 清除缓存

在开发或测试时，可以通过以下方式清除缓存：

1. **Streamlit UI**: 点击右上角的 "⋮" → "Clear cache"
2. **代码中**: 使用 `st.cache_data.clear()` 或 `st.cache_resource.clear()`
3. **重新部署**: 在 Streamlit Cloud 上重新部署会自动清除缓存

### 监控性能

应用包含性能监控工具 (`utils/performance.py`)，在开发模式下可以查看：
- CPU 使用率
- 内存使用率
- 磁盘使用率
- 函数执行时间

启用方式：设置环境变量 `DEBUG=True`

## 故障排查

### 常见问题

1. **部署失败**
   - 检查 `requirements.txt` 是否包含所有依赖
   - 查看部署日志中的错误信息
   - 确保 `app.py` 文件存在且可执行

2. **数据库连接错误**
   - 确认数据库文件路径正确
   - 检查文件权限
   - 考虑使用 PostgreSQL 替代 SQLite（生产环境推荐）

3. **API Key 错误**
   - 确认在 Streamlit Cloud Secrets 中正确配置了 API Key
   - 检查环境变量名称是否匹配（必须是 `ANTHROPIC_API_KEY`）
   - 验证步骤：
     1. 在 Streamlit Cloud 控制台：Settings → Secrets
     2. 确认有：`ANTHROPIC_API_KEY = "sk-ant-..."`
     3. 访问 https://console.anthropic.com 检查 API key 状态
     4. 确认 API key 是有效的、未过期的、且有足够额度
   - 如果 API key 无效，需要重新生成并更新 Secrets
   - 运行 `python verify_api_key.py` 进行本地验证

4. **缓存问题**
   - 如果数据未更新，尝试清除缓存
   - 检查 TTL 设置是否合理
   - 确认缓存键（函数参数）是否正确

### 日志查看

在 Streamlit Cloud 控制台：
1. 进入应用设置
2. 点击 "Logs" 标签
3. 查看实时日志输出

## 生产环境建议

1. **数据库**: 使用 PostgreSQL 替代 SQLite（更好的并发性能）
2. **缓存**: 根据数据更新频率调整 TTL
3. **监控**: 定期检查应用性能和资源使用
4. **备份**: 定期备份数据库和重要数据
5. **安全**: 确保所有敏感信息都在 Secrets 中配置
