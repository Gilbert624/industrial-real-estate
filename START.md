# 启动应用指南

## 问题说明

如果遇到 `ModuleNotFoundError` 错误（如 `No module named 'plotly'`），这是因为 Streamlit 没有使用虚拟环境。

## 解决方案

### 方法 1: 使用启动脚本（推荐）

```bash
./run.sh
```

### 方法 2: 手动激活虚拟环境

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 启动 Streamlit
streamlit run app.py
```

### 方法 3: 直接使用虚拟环境中的 Python

```bash
venv/bin/streamlit run app.py
```

## 验证依赖

所有必需的依赖包已安装在虚拟环境中：
- ✅ plotly (6.5.1)
- ✅ sqlalchemy (2.0.45)
- ✅ anthropic (0.75.0)
- ✅ streamlit (1.52.2)
- ✅ pandas (2.3.3)
- ✅ numpy (2.4.0)

## 注意事项

⚠️ **重要**: 确保始终使用虚拟环境运行应用，否则会找不到已安装的依赖包。
