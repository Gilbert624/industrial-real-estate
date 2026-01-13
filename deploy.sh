#!/bin/bash
# 外部部署脚本 - Streamlit Cloud / 其他平台

set -e  # 遇到错误立即退出

echo "🚀 开始外部部署准备..."
echo ""

# 检查必要文件
echo "📋 检查必要文件..."

files=(
    "app.py"
    "requirements.txt"
    ".streamlit/config.toml"
    ".gitignore"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失！"
        exit 1
    fi
done

echo ""
echo "🔍 验证依赖..."

# 检查 requirements.txt
if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt 存在"
    echo "  依赖包数量: $(wc -l < requirements.txt)"
else
    echo "  ❌ requirements.txt 缺失！"
    exit 1
fi

echo ""
echo "🗄️  检查数据库配置..."

# 检查数据库文件是否在 .gitignore 中
if grep -q "*.db" .gitignore; then
    echo "  ✅ 数据库文件已在 .gitignore 中"
else
    echo "  ⚠️  警告: 数据库文件可能未在 .gitignore 中"
fi

echo ""
echo "🔐 检查配置文件..."

if [ -f ".streamlit/config.toml" ]; then
    echo "  ✅ Streamlit 配置文件存在"
else
    echo "  ❌ Streamlit 配置文件缺失！"
    exit 1
fi

if [ -f ".streamlit/secrets.toml.example" ]; then
    echo "  ✅ Secrets 示例文件存在"
    echo "  ⚠️  注意: 需要在部署平台配置 secrets"
else
    echo "  ⚠️  Secrets 示例文件不存在"
fi

echo ""
echo "📦 准备部署包..."

# 检查 Git 状态
if [ -d ".git" ]; then
    echo "  ✅ Git 仓库已初始化"
    
    # 检查未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "  ⚠️  警告: 有未提交的更改"
        echo "  建议先提交更改:"
        echo "    git add ."
        echo "    git commit -m '准备部署'"
        echo "    git push"
    else
        echo "  ✅ 所有更改已提交"
    fi
else
    echo "  ⚠️  警告: 未检测到 Git 仓库"
    echo "  建议初始化 Git 仓库用于部署"
fi

echo ""
echo "✅ 部署准备完成！"
echo ""
echo "📝 下一步:"
echo "  1. 确保代码已推送到 GitHub"
echo "  2. 在 Streamlit Cloud 创建新应用"
echo "  3. 配置 Secrets (API Keys 等)"
echo "  4. 等待部署完成"
echo ""
echo "📚 详细说明请查看 DEPLOYMENT.md"
