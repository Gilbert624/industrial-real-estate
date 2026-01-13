#!/bin/bash
# 启动脚本 - 确保使用虚拟环境

cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app.py
