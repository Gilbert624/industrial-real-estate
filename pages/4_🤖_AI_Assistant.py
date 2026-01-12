"""
AI Assistant Page
Provides natural language queries and intelligent financial analysis using Claude

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
from utils.ai_assistant import AIAssistant
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #1e3a5f;
        font-weight: 600;
    }
    h2, h3 {
        color: #2c5282;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 AI Financial Assistant")
st.write("Ask questions about your portfolio in natural language, or use quick analysis tools.")

# Check API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    st.error("⚠️ **ANTHROPIC_API_KEY not configured**")
    st.write("Please add your Claude API key to the `.env` file:")
    st.code("ANTHROPIC_API_KEY=sk-ant-...", language="bash")
    st.write("Get your API key from: https://console.anthropic.com")
    st.stop()

# Initialize AI assistant
try:
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = AIAssistant()
    
    assistant = st.session_state.ai_assistant
    
except Exception as e:
    st.error(f"❌ Error initializing AI Assistant: {e}")
    st.write("Please check your API key configuration.")
    st.stop()

# Create tabs
tab1, tab2 = st.tabs(["💬 Ask Questions", "⚡ Quick Analysis"])

# ==================== Tab 1: Ask Questions ====================
with tab1:
    st.subheader("Ask Me Anything About Your Finances")
    st.write("Examples: *'How is my cash flow?'*, *'Which project is over budget?'*, *'What should I focus on this month?'*")
    
    # Chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Question input
    with st.form("question_form", clear_on_submit=True):
        user_question = st.text_area(
            "Your Question:",
            placeholder="e.g., Analyze my current financial position and suggest priorities...",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("🚀 Ask Claude", use_container_width=True)
        with col2:
            include_context = st.checkbox("Include financial data context", value=True)
    
    # Process question
    if submitted and user_question:
        with st.spinner("🤔 Analyzing your data and thinking..."):
            try:
                # Get answer
                answer = assistant.query(user_question, include_context=include_context)
                
                # Add to history
                st.session_state.chat_history.append({
                    'question': user_question,
                    'answer': answer.get('answer', 'Error'),
                    'metadata': answer
                })
                
                # Display result based on type
                if answer.get('cached'):
                    st.success("✅ Answer retrieved from cache (instant & free!)")
                elif answer.get('error'):
                    st.error("❌ Error occurred")
                else:
                    model_emoji = "🚀" if answer.get('model') == 'sonnet' else "⚡"
                    model_name = answer.get('model', 'AI').title()
                    cost = answer.get('cost', 0)
                    
                    st.success(f"✅ Answer from Claude {model_name} {model_emoji}")
                    
                    # Show cost info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"💰 Cost: ${cost:.4f}")
                    with col2:
                        st.caption(f"📊 Tokens: {answer.get('input_tokens',0)+answer.get('output_tokens',0)}")
                    with col3:
                        if answer.get('model') == 'haiku':
                            st.caption("⚡ Optimized for cost")
                        else:
                            st.caption("🚀 Full analysis")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.write("---")
        st.subheader("💬 Conversation History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['question'][:80]}...", expanded=(i==0)):
                st.write("**Your Question:**")
                st.write(chat['question'])
                
                st.write("**Claude's Answer:**")
                st.write(chat['answer'])
                
                # Show metadata if available
                if 'metadata' in chat and chat['metadata']:
                    metadata = chat['metadata']
                    if metadata.get('cached'):
                        st.caption("✅ From cache (free)")
                    elif not metadata.get('error'):
                        cost = metadata.get('cost', 0)
                        model = metadata.get('model', 'unknown')
                        st.caption(f"💰 ${cost:.4f} | Model: {model.title()}")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("👆 Ask your first question above!")

# ==================== Tab 2: Quick Analysis ====================
with tab2:
    st.subheader("⚡ One-Click Analysis Tools")
    st.write("Get instant insights with pre-configured analysis prompts.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**💰 Cash Flow Analysis**")
        st.write("Analyze your current cash position, income, expenses, and trends.")
        
        if st.button("🔍 Analyze Cash Flow", use_container_width=True):
            with st.spinner("Analyzing cash flow..."):
                try:
                    result = assistant.analyze_cash_flow()
                    st.write("---")
                    st.write("**Analysis:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.write("")
        
        st.write("**📊 Trend Analysis**")
        st.write("Identify patterns and trends in your 6-month financial data.")
        
        if st.button("📈 Identify Trends", use_container_width=True):
            with st.spinner("Analyzing trends..."):
                try:
                    result = assistant.identify_trends()
                    st.write("---")
                    st.write("**Trends:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.write("**🏗️ Project Comparison**")
        st.write("Compare active projects: performance, budget status, concerns.")
        
        if st.button("⚖️ Compare Projects", use_container_width=True):
            with st.spinner("Comparing projects..."):
                try:
                    result = assistant.compare_projects()
                    st.write("---")
                    st.write("**Comparison:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.write("")
        
        st.write("**✅ Action Items**")
        st.write("Get top 3-5 recommended actions based on your complete financial picture.")
        
        if st.button("🎯 Get Recommendations", use_container_width=True):
            with st.spinner("Generating recommendations..."):
                try:
                    result = assistant.suggest_actions()
                    st.write("---")
                    st.write("**Recommendations:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==================== Sidebar Info ====================
with st.sidebar:
    st.header("📊 Session Statistics")
    
    # 获取session统计
    if 'ai_assistant' in st.session_state:
        assistant = st.session_state.ai_assistant
        stats = assistant.get_session_stats()
        
        # 显示统计
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Queries",
                stats['queries'],
                help="API calls this session"
            )
            st.metric(
                "Cached",
                stats['cached'],
                f"{stats['cache_rate']:.0f}%",
                help="Cache hit rate"
            )
        
        with col2:
            st.metric(
                "Cost",
                f"${stats['cost']:.3f}",
                help="Estimated cost this session"
            )
            savings = stats['cached'] * 0.022
            st.metric(
                "Saved",
                f"${savings:.3f}",
                help="Savings from cache"
            )
        
        # 成本提示
        if stats['cost'] > 0.50:
            st.warning("⚠️ Session cost > $0.50")
        elif stats['cost'] > 0:
            st.success(f"💡 {stats['queries']} queries for ${stats['cost']:.3f}")
        
        # 优化提示
        with st.expander("💡 Cost Optimization Tips"):
            st.write("**Active Optimizations:**")
            st.write("✅ Smart caching (instant, free)")
            st.write("✅ Auto model selection (Haiku/Sonnet)")
            st.write("✅ Minimal context for simple queries")
            st.write("✅ Reduced historical data")
            st.write(f"\n**This Session:**")
            st.write(f"- Average: ${stats['cost']/max(stats['queries'],1):.4f}/query")
            st.write(f"- Cache rate: {stats['cache_rate']:.0f}%")
    else:
        st.info("Start a conversation to see statistics")
    
    st.write("---")
    
    st.header("ℹ️ About AI Assistant")
    
    st.write("**Powered by Claude (Sonnet 4 & Haiku)**")
    st.write("This assistant has access to your:")
    st.write("- 💰 Cash balance and flow")
    st.write("- 📊 Asset portfolio")
    st.write("- 🏗️ Active projects")
    st.write("- 💳 Recent transactions")
    st.write("- 📈 3-month trends")
    
    st.write("---")
    
    st.write("**Tips for Best Results:**")
    st.write("✅ Be specific in your questions")
    st.write("✅ Ask about trends, not just numbers")
    st.write("✅ Request actionable advice")
    st.write("✅ Compare time periods or projects")
    
    st.write("---")
    
    st.write("**Example Questions:**")
    st.code("""
- How is my cash flow trending?
- Which project needs attention?
- Am I over/under budget overall?
- What are my biggest expenses?
- Should I be concerned about anything?
- What should I prioritize this month?
    """, language="text")
    
    st.write("---")
    
    # API usage info
    st.caption("💡 Smart caching reduces costs")
    st.caption("⚡ Haiku model used for simple queries (12x cheaper)")
    st.caption("📊 Responses typically take 3-10 seconds")
    
    st.markdown("---")
    st.markdown("*© 2025 Gilbert Industrial Real Estate Development | Brisbane, Queensland, Australia*")
