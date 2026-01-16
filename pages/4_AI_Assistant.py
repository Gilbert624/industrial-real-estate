"""
AI Assistant Page
Provides natural language queries and intelligent financial analysis using Claude

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
from utils.ai_assistant import AIAssistant
import os
from datetime import datetime
from config.theme import generate_css
from config.i18n import t, get_current_language
import json
from models.database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# 应用专业主题
st.markdown(generate_css('light'), unsafe_allow_html=True)

st.title(f"🤖 {t('ai.title')}")
st.write(t('ai.subtitle'))

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


def build_dd_context(project_id):
    db = DatabaseManager()
    project = db.get_dd_project_by_id(project_id)
    if not project:
        return "No Due Diligence project found for the selected ID."

    assumptions = {a.category: a.assumption_text for a in (project.assumptions or [])}

    def load_json(text):
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return None

    cost = load_json(assumptions.get("cost_breakdown"))
    loan = load_json(assumptions.get("loan_calculation"))
    fm = load_json(assumptions.get("financial_model"))
    scenarios = load_json(assumptions.get("scenarios"))

    lines = [
        f"DD Project: {project.name} (status: {project.status})",
        f"Location: {project.location or 'N/A'} | Property: {project.property_type or 'N/A'}",
    ]

    if project.irr is not None or project.npv is not None:
        lines.append(
            "Key Metrics:"
            f" IRR={project.irr if project.irr is not None else 'N/A'}"
            f", NPV={project.npv if project.npv is not None else 'N/A'}"
            f", Equity Multiple={project.equity_multiple if project.equity_multiple is not None else 'N/A'}"
        )

    if cost and isinstance(cost, dict):
        summary = cost.get("summary", {})
        lines.append(
            "Cost Breakdown:"
            f" Total Dev Cost={summary.get('total_development_cost')}"
            f", Hard={summary.get('total_hard_costs')}"
            f", Soft={summary.get('total_soft_costs')}"
        )

    if loan and isinstance(loan, dict):
        const = loan.get("construction_phase", {}).get("loan_parameters", {})
        inv = loan.get("investment_phase", {}).get("loan_parameters", {})
        equity = loan.get("equity_analysis", {})
        debt_metrics = loan.get("debt_metrics", {})
        lines.append(
            "Loan Summary:"
            f" Construction Loan={const.get('loan_amount')}"
            f", Investment Loan={inv.get('loan_amount')}"
            f", Equity Required={equity.get('total_equity_required')}"
            f", DSCR={debt_metrics.get('dscr')}"
        )

    if fm and isinstance(fm, dict):
        lines.append(
            "Financial Model:"
            f" IRR={fm.get('irr')}"
            f", NPV={fm.get('npv')}"
            f", Equity Multiple={fm.get('equity_multiple')}"
            f", CoC={fm.get('cash_on_cash_return')}"
            f", Profit={fm.get('total_profit')}"
        )

    if scenarios and isinstance(scenarios, dict):
        def scenario_line(key, label):
            data = scenarios.get(key, {})
            if not data:
                return None
            return (
                f"{label}: IRR={data.get('irr')}, "
                f"NPV={data.get('npv')}, EM={data.get('equity_multiple')}"
            )

        scenario_lines = [
            scenario_line("base", "Base"),
            scenario_line("optimistic", "Optimistic"),
            scenario_line("pessimistic", "Pessimistic"),
        ]
        scenario_lines = [line for line in scenario_lines if line]
        if scenario_lines:
            lines.append("Scenarios: " + " | ".join(scenario_lines))

    return "\n".join(lines)

# Create tabs
tab1, tab2 = st.tabs([f"💬 {t('ai.ask_questions')}", f"⚡ {t('ai.quick_analysis')}"])

# ==================== Tab 1: Ask Questions ====================
with tab1:
    st.subheader(f"{t('ai.ask_questions')}")
    st.write("Examples: *'How is my cash flow?'*, *'Which project is over budget?'*, *'What should I focus on this month?'*")
    
    # Chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'dd_context' not in st.session_state:
        st.session_state.dd_context = None
    if 'dd_project_id' not in st.session_state:
        st.session_state.dd_project_id = None

    with st.expander("📌 Due Diligence Results"):
        dd_projects = assistant.db.get_all_dd_projects()
        if not dd_projects:
            st.info("No Due Diligence projects found.")
        else:
            project_options = {f"{p.name} ({p.status})": p.id for p in dd_projects}
            labels = list(project_options.keys())
            default_index = 0
            if st.session_state.dd_project_id in project_options.values():
                default_index = list(project_options.values()).index(
                    st.session_state.dd_project_id
                )
            selected_label = st.selectbox(
                "Select DD Project",
                options=labels,
                index=default_index,
            )
            selected_id = project_options[selected_label]

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Load DD Results", width="stretch"):
                    if hasattr(assistant, "get_dd_context"):
                        st.session_state.dd_context = assistant.get_dd_context(selected_id)
                    else:
                        st.session_state.dd_context = build_dd_context(selected_id)
                    st.session_state.dd_project_id = selected_id
                    st.success("✅ DD results loaded")
            with col2:
                if st.button("Clear DD Results", width="stretch"):
                    st.session_state.dd_context = None
                    st.session_state.dd_project_id = None
                    st.info("DD context cleared.")

        if st.session_state.dd_context:
            st.text_area(
                "Loaded DD Context",
                value=st.session_state.dd_context,
                height=200,
            )
    
    # Question input
    with st.form("question_form", clear_on_submit=True):
        user_question = st.text_area(
            f"{t('ai.your_question')}:",
            placeholder="e.g., Analyze my current financial position and suggest priorities...",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button(f"🚀 {t('ai.ask_claude')}", width='stretch')
        with col2:
            include_context = st.checkbox(t('ai.include_context'), value=True)
            include_dd = st.checkbox(
                "Include DD results",
                value=bool(st.session_state.dd_context),
                disabled=not bool(st.session_state.dd_context),
            )
    
    # Process question
    if submitted and user_question:
        with st.spinner("🤔 Analyzing your data and thinking..."):
            try:
                # Get answer
                dd_context = st.session_state.dd_context if include_dd else None
                answer = assistant.query(
                    user_question,
                    include_context=include_context,
                    extra_context=dd_context,
                )
                
                # Add to history
                st.session_state.chat_history.append({
                    'question': user_question,
                    'answer': answer.get('answer', 'Error'),
                    'metadata': answer
                })
                
                # Display result based on type
                if answer.get('cached'):
                    st.success(f"✅ {t('ai.cached_answer')}")
                elif answer.get('error'):
                    st.error(f"❌ {t('messages.error_occurred')}")
                else:
                    model_emoji = "🚀" if answer.get('model') == 'sonnet' else "⚡"
                    model_name = answer.get('model', 'AI').title()
                    cost = answer.get('cost', 0)
                    
                    st.success(f"✅ {t('ai.answer_from')} Claude {model_name} {model_emoji}")
                    
                    # Show cost info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"💰 {t('ai.cost')}: ${cost:.4f}")
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
        st.subheader(f"💬 {t('ai.conversation_history')}")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['question'][:80]}...", expanded=(i==0)):
                st.write(f"**{t('ai.your_question')}:**")
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
        if st.button(f"🗑️ {t('ai.clear_history')}"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("👆 Ask your first question above!")

# ==================== Tab 2: Quick Analysis ====================
with tab2:
    st.subheader(f"⚡ {t('ai.quick_analysis')}")
    st.write("Get instant insights with pre-configured analysis prompts.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**💰 {t('ai.analyze_cash_flow')}**")
        st.write("Analyze your current cash position, income, expenses, and trends.")
        
        if st.button(f"🔍 {t('ai.analyze_cash_flow')}", width='stretch'):
            with st.spinner("Analyzing cash flow..."):
                try:
                    result = assistant.analyze_cash_flow()
                    st.write("---")
                    st.write("**Analysis:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"{t('messages.error_occurred')}: {e}")
        
        st.write("")
        
        st.write(f"**📊 {t('ai.identify_trends')}**")
        st.write("Identify patterns and trends in your 6-month financial data.")
        
        if st.button(f"📈 {t('ai.identify_trends')}", width='stretch'):
            with st.spinner("Analyzing trends..."):
                try:
                    result = assistant.identify_trends()
                    st.write("---")
                    st.write("**Trends:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"{t('messages.error_occurred')}: {e}")
    
    with col2:
        st.write(f"**🏗️ {t('ai.compare_projects')}**")
        st.write("Compare active projects: performance, budget status, concerns.")
        
        if st.button(f"⚖️ {t('ai.compare_projects')}", width='stretch'):
            with st.spinner("Comparing projects..."):
                try:
                    result = assistant.compare_projects()
                    st.write("---")
                    st.write("**Comparison:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"{t('messages.error_occurred')}: {e}")
        
        st.write("")
        
        st.write(f"**✅ {t('ai.get_recommendations')}**")
        st.write("Get top 3-5 recommended actions based on your complete financial picture.")
        
        if st.button(f"🎯 {t('ai.get_recommendations')}", width='stretch'):
            with st.spinner("Generating recommendations..."):
                try:
                    result = assistant.suggest_actions()
                    st.write("---")
                    st.write("**Recommendations:**")
                    st.write(result.get('answer', result))
                    
                    if not result.get('cached', False) and not result.get('error'):
                        st.caption(f"💰 ${result.get('cost', 0):.4f} | ⚡ {result.get('model', 'haiku').title()} model")
                except Exception as e:
                    st.error(f"{t('messages.error_occurred')}: {e}")

# ==================== Sidebar Info ====================
with st.sidebar:
    st.markdown("""
    <div class="bento-card" style="margin-bottom: 1.5rem;">
        <h3 style="margin-bottom: 1rem; color: var(--primary);">📊 Session Statistics</h3>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    st.header(f"ℹ️ {t('ai.about')}")
    
    st.write(f"**{t('ai.powered_by')}**")
    st.write(f"{t('ai.has_access_to')}")
    st.write("- 💰 Cash balance and flow")
    st.write("- 📊 Asset portfolio")
    st.write("- 🏗️ Active projects")
    st.write("- 💳 Recent transactions")
    st.write("- 📈 3-month trends")
    
    st.write("---")
    
    st.write(f"**{t('ai.tips_title')}:**")
    st.write("✅ Be specific in your questions")
    st.write("✅ Ask about trends, not just numbers")
    st.write("✅ Request actionable advice")
    st.write("✅ Compare time periods or projects")
    
    st.write("---")
    
    st.write(f"**{t('ai.example_questions')}:**")
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
