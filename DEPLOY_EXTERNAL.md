# 外部部署指南

**最后更新**: 2026-01-13  
**状态**: ✅ 准备就绪

## 部署平台选项

### 1. Streamlit Cloud (推荐)

Streamlit Cloud 是 Streamlit 官方提供的免费托管服务。

#### 前置要求
- ✅ GitHub 账号
- ✅ 代码已推送到 GitHub 仓库
- ✅ 所有依赖在 `requirements.txt` 中

#### 部署步骤

1. **准备 GitHub 仓库**
   ```bash
   # 确保所有更改已提交
   git add .
   git commit -m "准备外部部署 - 添加 Market Intelligence 方法"
   git push origin main
   ```

2. **访问 Streamlit Cloud**
   - 前往 https://streamlit.io/cloud
   - 使用 GitHub 账号登录

3. **创建新应用**
   - 点击 "New app"
   - 选择您的 GitHub 仓库
   - 选择分支: `main`
   - 主文件路径: `app.py`
   - 点击 "Deploy"

4. **配置 Secrets**
   在 Streamlit Cloud 控制台的 "Secrets" 部分添加：
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
   
   [database]
   type = "sqlite"
   path = "industrial_real_estate.db"
   
   [app]
   env = "production"
   debug = false
   ```

5. **等待部署**
   - 部署通常需要 2-5 分钟
   - 查看日志确认无错误
   - 部署完成后会显示应用 URL

#### 优势
- ✅ 免费使用
- ✅ 自动 HTTPS
- ✅ 自动更新（Git push 后自动重新部署）
- ✅ 内置日志和监控

---

### 2. Heroku

#### 前置要求
- Heroku 账号
- Heroku CLI 已安装

#### 部署步骤

1. **创建 Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

2. **创建 setup.sh**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = \$PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

3. **部署到 Heroku**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

---

### 3. Docker 部署

#### 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 构建和运行

```bash
docker build -t asset-management .
docker run -p 8501:8501 asset-management
```

---

### 4. AWS / GCP / Azure

这些平台需要更多配置，建议参考各平台的 Streamlit 部署文档。

---

## 部署前检查清单

### ✅ 代码检查
- [ ] 所有文件已提交到 Git
- [ ] `requirements.txt` 包含所有依赖
- [ ] 无硬编码的敏感信息（API Keys 等）
- [ ] 数据库路径使用环境变量或配置

### ✅ 配置文件
- [ ] `.streamlit/config.toml` 存在
- [ ] `.streamlit/secrets.toml.example` 存在（作为参考）
- [ ] `.gitignore` 正确配置（排除敏感文件）

### ✅ 功能验证
- [ ] 本地测试通过
- [ ] 所有页面可以正常访问
- [ ] 数据库连接正常
- [ ] API 调用正常（如果使用）

### ✅ 部署准备
- [ ] 运行 `./deploy.sh` 检查通过
- [ ] 准备 Secrets 配置
- [ ] 了解部署平台的限制和配额

---

## 部署后验证

部署完成后，请验证以下功能：

### 基础功能
- [ ] 应用可以正常访问
- [ ] 所有页面可以加载
- [ ] 无控制台错误

### 数据库功能
- [ ] 可以查看资产列表
- [ ] 可以添加/编辑资产
- [ ] 财务数据可以正常显示
- [ ] 项目数据可以正常显示

### Market Intelligence 功能
- [ ] 开发项目列表可以加载
- [ ] 租金数据可以显示
- [ ] 竞争对手分析可以查看
- [ ] 可以添加新的数据

### AI Assistant
- [ ] AI Assistant 可以正常使用（需要 API Key）

---

## 常见问题

### 1. 部署失败 - 依赖问题

**问题**: `ModuleNotFoundError`

**解决**:
- 检查 `requirements.txt` 是否包含所有依赖
- 确保版本号兼容
- 查看部署日志中的详细错误

### 2. 数据库连接错误

**问题**: 无法连接数据库

**解决**:
- 确认数据库文件路径正确
- 检查文件权限
- 考虑使用 PostgreSQL（生产环境推荐）

### 3. API Key 错误

**问题**: AI Assistant 无法工作

**解决**:
- 确认在部署平台的 Secrets 中配置了 `ANTHROPIC_API_KEY`
- 检查环境变量名称是否匹配
- 验证 API Key 是否有效

### 4. 缓存问题

**问题**: 数据未更新

**解决**:
- 清除 Streamlit 缓存（UI 右上角）
- 检查缓存 TTL 设置
- 重新部署应用

---

## 性能优化建议

### 1. 数据库优化
- 使用 PostgreSQL 替代 SQLite（更好的并发性能）
- 添加适当的索引
- 定期清理旧数据

### 2. 缓存策略
- 合理设置缓存 TTL
- 使用 `@st.cache_data` 缓存查询结果
- 使用 `@st.cache_resource` 缓存资源

### 3. 代码优化
- 减少不必要的重新计算
- 优化数据库查询
- 使用分页加载大量数据

---

## 监控和维护

### 日志查看
- Streamlit Cloud: 控制台 → Logs
- Heroku: `heroku logs --tail`
- Docker: `docker logs <container-id>`

### 备份策略
- 定期备份数据库
- 使用版本控制管理代码
- 保存重要的配置文件

### 更新流程
1. 本地测试更改
2. 提交到 Git
3. 推送到远程仓库
4. 等待自动部署（Streamlit Cloud）
5. 验证功能正常

---

## 支持

如有问题，请查看：
- `DEPLOYMENT.md` - 详细部署文档
- `DEPLOYMENT_CHECKLIST.md` - 部署清单
- `README.md` - 项目说明

---

**部署就绪！** 🚀
