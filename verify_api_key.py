#!/usr/bin/env python3
"""
验证 Anthropic API Key 配置

此脚本用于验证 ANTHROPIC_API_KEY 是否正确配置且有效。
可以用于本地测试和 Streamlit Cloud 部署前验证。
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_api_key_set():
    """检查 API Key 是否已设置"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 未找到")
        print("\n配置方法：")
        print("1. 本地开发：在 .env 文件中添加：")
        print("   ANTHROPIC_API_KEY=sk-ant-...")
        print("\n2. Streamlit Cloud：")
        print("   - 进入应用 Settings → Secrets")
        print("   - 添加：ANTHROPIC_API_KEY = \"sk-ant-...\"")
        return None
    
    # 检查格式
    if not api_key.startswith('sk-ant-'):
        print(f"⚠️  API Key 格式可能不正确（应该以 'sk-ant-' 开头）")
        print(f"   当前值：{api_key[:10]}...")
        return api_key
    
    print(f"✅ API Key 已配置（格式正确）")
    print(f"   前缀：{api_key[:10]}...")
    return api_key

def test_api_connection(api_key):
    """测试 API 连接"""
    try:
        import anthropic
    except ImportError:
        print("❌ anthropic 包未安装")
        print("   请运行：pip install anthropic")
        return False
    
    print("\n🔍 测试 API 连接...")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # 发送一个简单的测试请求
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # 使用最便宜的模型进行测试
            max_tokens=10,
            messages=[
                {"role": "user", "content": "Say 'OK' if you can read this."}
            ]
        )
        
        answer = response.content[0].text.strip()
        print(f"✅ API 连接成功！")
        print(f"   响应：{answer}")
        print(f"   使用的 tokens: {response.usage.input_tokens} 输入 / {response.usage.output_tokens} 输出")
        return True
        
    except anthropic.AuthenticationError as e:
        print(f"❌ API Key 认证失败")
        print(f"   错误：{e}")
        print("\n可能的原因：")
        print("1. API Key 无效或已过期")
        print("2. API Key 格式不正确")
        print("3. 请访问 https://console.anthropic.com 检查 API Key 状态")
        return False
        
    except anthropic.RateLimitError as e:
        print(f"⚠️  API 请求被限流")
        print(f"   错误：{e}")
        print("   （API Key 有效，但可能需要等待）")
        return True  # Key 是有效的，只是被限流
        
    except anthropic.APIError as e:
        print(f"❌ API 请求失败")
        print(f"   错误类型：{type(e).__name__}")
        print(f"   错误信息：{e}")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误")
        print(f"   错误类型：{type(e).__name__}")
        print(f"   错误信息：{e}")
        return False

def check_streamlit_secrets():
    """检查 Streamlit Secrets 配置（如果可用）"""
    try:
        import streamlit as st
        # 在 Streamlit 环境中，可以检查 secrets
        if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
            print("\n✅ Streamlit Secrets 中已配置 API Key")
            return True
        else:
            print("\n⚠️  Streamlit Secrets 中未找到 API Key")
            return False
    except:
        # 不在 Streamlit 环境中
        pass
    return None

def main():
    """主函数"""
    print("=" * 70)
    print("Anthropic API Key 验证工具")
    print("=" * 70)
    
    # 步骤 1: 检查 API Key 是否设置
    api_key = check_api_key_set()
    if not api_key:
        print("\n" + "=" * 70)
        sys.exit(1)
    
    # 步骤 2: 测试 API 连接
    success = test_api_connection(api_key)
    
    # 步骤 3: 检查 Streamlit Secrets（如果适用）
    check_streamlit_secrets()
    
    # 总结
    print("\n" + "=" * 70)
    if success:
        print("✅ 验证完成：API Key 配置正确且有效")
        print("\n下一步：")
        print("1. 如果这是本地测试，API Key 已就绪")
        print("2. 如果准备部署到 Streamlit Cloud：")
        print("   - 访问 https://share.streamlit.io/")
        print("   - 进入应用 Settings → Secrets")
        print("   - 添加相同的 API Key")
        print("   - 格式：ANTHROPIC_API_KEY = \"sk-ant-...\"")
    else:
        print("❌ 验证失败：请检查 API Key 配置")
        print("\n故障排查：")
        print("1. 确认 API Key 从 https://console.anthropic.com 获取")
        print("2. 检查 API Key 是否有效且未过期")
        print("3. 确认 API Key 有足够的额度")
        print("4. 检查网络连接")
    print("=" * 70)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
