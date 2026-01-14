"""
AI Financial Assistant Module - Enhanced with Cost Optimization
Uses Claude API with intelligent caching and cost optimization
"""

import anthropic
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from models.database import DatabaseManager

# Load environment variables
load_dotenv()

class AIAssistant:
    """AI-powered financial assistant with cost optimization"""
    
    # Model configurations with fallback options
    MODELS = {
        'sonnet': {
            'name': 'claude-3-5-sonnet-20241022',  # Latest stable version
            'fallback': 'claude-3-5-sonnet-20241022',  # Fallback to 3.5
            'input_cost': 0.003,   # per 1K tokens
            'output_cost': 0.015   # per 1K tokens
        },
        'haiku': {
            'name': 'claude-3-5-haiku-20241022',  # Try Claude 3.5 Haiku first
            'fallback': 'claude-3-haiku-20240307',  # Fallback to 3.0
            'input_cost': 0.00025,  # per 1K tokens (12x cheaper)
            'output_cost': 0.00125  # per 1K tokens (12x cheaper)
        }
    }
    
    # Simple queries that can use Haiku
    SIMPLE_QUERY_KEYWORDS = [
        'what is', 'how much', 'how many', 'show me', 'list',
        'balance', 'total', 'count', 'latest', 'recent'
    ]
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.db = DatabaseManager()
        
        # In-memory cache (session-level)
        self.cache = {}
        
        # Usage tracking (in-memory for this session)
        # Initialize from session_state if available, otherwise start fresh
        import streamlit as st
        if 'ai_stats' not in st.session_state:
            st.session_state.ai_stats = {
                'queries': 0,
                'cost': 0.0,
                'cached': 0
            }
        
        # Sync with session_state
        self.session_queries = st.session_state.ai_stats['queries']
        self.session_cost = st.session_state.ai_stats['cost']
        self.session_cached = st.session_state.ai_stats['cached']
    
    def get_question_hash(self, question):
        """Generate hash for question similarity detection"""
        # Normalize question
        normalized = question.lower().strip()
        # Remove punctuation
        import string
        normalized = normalized.translate(str.maketrans('', '', string.punctuation))
        # Hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def should_use_haiku(self, question):
        """
        Determine if query is simple enough for Haiku
        
        Args:
            question: User's question
            
        Returns:
            Boolean
        """
        question_lower = question.lower()
        
        # Check for simple query keywords
        for keyword in self.SIMPLE_QUERY_KEYWORDS:
            if keyword in question_lower:
                return True
        
        # Short questions (< 50 chars) often simple
        if len(question) < 50:
            return True
        
        return False
    
    def detect_query_type(self, question):
        """Detect query type for context optimization"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['cash', 'flow', 'balance', 'income', 'expense']):
            return 'cash'
        elif any(word in question_lower for word in ['project', 'budget', 'construction', 'development']):
            return 'project'
        elif any(word in question_lower for word in ['asset', 'property', 'portfolio']):
            return 'asset'
        else:
            return 'general'
    
    def get_all_assets(self):
        """Get all assets from database"""
        session = self.db.get_session()
        try:
            from models.database import Asset
            assets = session.query(Asset).all()
            return assets
        finally:
            self.db.close_session(session)
    
    def get_minimal_context(self, query_type='general'):
        """
        Get minimal context based on query type (P2 optimization)
        
        Args:
            query_type: Type of query (cash, project, asset, general)
            
        Returns:
            Formatted context string
        """
        context = {}
        
        try:
            if query_type in ['cash', 'general']:
                # Cash flow only
                context['cash_balance'] = self.db.get_cash_balance()
                now = datetime.now()
                context['monthly_income'] = self.db.get_monthly_income(now.year, now.month)
                context['monthly_expense'] = self.db.get_monthly_expense(now.year, now.month)
                context['net_flow'] = context['monthly_income'] - context['monthly_expense']
            
            if query_type in ['project', 'general']:
                # Projects only
                context['active_projects'] = self.db.get_active_projects_count()
                context['total_budget'] = self.db.get_total_projects_budget()
                context['total_spent'] = self.db.get_total_projects_cost()
            
            if query_type in ['asset', 'general']:
                # Assets only
                assets = self.get_all_assets()
                context['total_assets'] = len(assets)
                context['total_value'] = sum(float(a.current_valuation) if a.current_valuation else 0 for a in assets)
            
        except Exception as e:
            context['error'] = str(e)
        
        return self.format_minimal_context(context, query_type)
    
    def format_minimal_context(self, context, query_type):
        """Format minimal context into readable string"""
        if 'error' in context:
            return f"Error: {context['error']}"
        
        lines = [f"Financial Data ({datetime.now().strftime('%B %Y')}):"]
        
        if 'cash_balance' in context:
            lines.append(f"\nCash: ${context['cash_balance']:,.0f}")
            lines.append(f"Income: ${context['monthly_income']:,.0f}")
            lines.append(f"Expense: ${context['monthly_expense']:,.0f}")
            lines.append(f"Net: ${context['net_flow']:,.0f}")
        
        if 'active_projects' in context:
            lines.append(f"\nProjects: {context['active_projects']} active")
            lines.append(f"Budget: ${context['total_budget']:,.0f}")
            lines.append(f"Spent: ${context['total_spent']:,.0f}")
        
        if 'total_assets' in context:
            lines.append(f"\nAssets: {context['total_assets']} properties")
            lines.append(f"Value: ${context['total_value']:,.0f}")
        
        return "\n".join(lines)
    
    def get_financial_context(self):
        """Get full financial context (for complex queries)"""
        context = {}
        
        try:
            # Cash and flow
            context['cash_balance'] = self.db.get_cash_balance()
            
            now = datetime.now()
            context['current_month'] = now.strftime('%B %Y')
            context['monthly_income'] = self.db.get_monthly_income(now.year, now.month)
            context['monthly_expense'] = self.db.get_monthly_expense(now.year, now.month)
            context['net_cash_flow'] = context['monthly_income'] - context['monthly_expense']
            
            # Assets
            assets = self.get_all_assets()
            context['total_assets'] = len(assets)
            context['total_asset_value'] = sum(float(a.current_valuation) if a.current_valuation else 0 for a in assets)
            
            # Projects
            context['active_projects'] = self.db.get_active_projects_count()
            context['total_budget'] = self.db.get_total_projects_budget()
            context['total_spent'] = self.db.get_total_projects_cost()
            context['budget_remaining'] = context['total_budget'] - context['total_spent']
            
            # Recent activity (limited to 5 for cost)
            recent_transactions = self.db.get_recent_transactions(5)
            context['recent_transactions'] = [
                {
                    'date': tx.transaction_date.strftime('%Y-%m-%d'),
                    'type': tx.transaction_type.value if hasattr(tx.transaction_type, 'value') else str(tx.transaction_type),
                    'category': tx.category,
                    'amount': abs(float(tx.amount))
                }
                for tx in recent_transactions
            ]
            
            # Cashflow trend (3 months for cost optimization)
            trend = self.db.get_cashflow_trend(3)
            context['cashflow_trend'] = [
                {
                    'month': f"{data['year']}-{data['month']:02d}",
                    'income': data['income'],
                    'expense': data['expense'],
                    'net': data['net']
                }
                for data in trend
            ]
            
        except Exception as e:
            context['error'] = f"Error gathering context: {e}"
        
        return context
    
    def format_context_for_claude(self, context):
        """Format financial context into a readable string for Claude"""
        if 'error' in context:
            return f"Error: {context['error']}"
        
        formatted = f"""
Financial Status ({context['current_month']}):

CASH: ${context['cash_balance']:,.0f}
Income: ${context['monthly_income']:,.0f} | Expense: ${context['monthly_expense']:,.0f} | Net: ${context['net_cash_flow']:,.0f}

ASSETS: {context['total_assets']} properties worth ${context['total_asset_value']:,.0f}

PROJECTS: {context['active_projects']} active
Budget: ${context['total_budget']:,.0f} | Spent: ${context['total_spent']:,.0f}

RECENT TRANSACTIONS:
"""
        
        for tx in context['recent_transactions']:
            formatted += f"{tx['date']}: {tx['type']} ${tx['amount']:,.0f} - {tx['category']}\n"
        
        formatted += "\nCASHFLOW (3 months):\n"
        for month_data in context['cashflow_trend']:
            formatted += f"{month_data['month']}: Net ${month_data['net']:,.0f}\n"
        
        return formatted
    
    def estimate_tokens(self, text):
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    def calculate_cost(self, input_tokens, output_tokens, model_type='sonnet'):
        """Calculate estimated cost"""
        model_config = self.MODELS[model_type]
        input_cost = (input_tokens / 1000) * model_config['input_cost']
        output_cost = (output_tokens / 1000) * model_config['output_cost']
        return input_cost + output_cost
    
    def query(self, user_question, include_context=True, force_model=None):
        """
        Send query to Claude with optimizations
        
        Args:
            user_question: User's natural language question
            include_context: Whether to include financial data
            force_model: Force specific model ('sonnet' or 'haiku')
            
        Returns:
            Dictionary with response and metadata
        """
        # P1: Generate question hash for cache
        question_hash = self.get_question_hash(user_question)
        
        # P1: Check cache first
        if question_hash in self.cache:
            self.session_cached += 1
            # Update session_state
            import streamlit as st
            st.session_state.ai_stats['cached'] = self.session_cached
            return {
                'answer': self.cache[question_hash],
                'cached': True,
                'cost': 0,
                'session_stats': self.get_session_stats()
            }
        
        try:
            # P2: Determine model to use
            if force_model:
                model_type = force_model
            else:
                model_type = 'haiku' if self.should_use_haiku(user_question) else 'sonnet'
            
            model_config = self.MODELS[model_type]
            model_name = model_config['name']
            
            # System prompt (shorter for cost)
            system_prompt = """You are a financial advisor for industrial real estate. Be concise and specific. Cite numbers from the data."""
            
            # P2: Build optimized user message
            if include_context:
                # Detect query type for minimal context
                query_type = self.detect_query_type(user_question)
                
                if model_type == 'haiku' or len(user_question) < 100:
                    # Use minimal context for simple queries
                    context_str = self.get_minimal_context(query_type)
                else:
                    # Use full context for complex queries
                    context = self.get_financial_context()
                    context_str = self.format_context_for_claude(context)
                
                user_message = f"Question: {user_question}\n\nData:\n{context_str}"
            else:
                user_message = user_question
            
            # Try primary model, fallback to secondary if 404
            response = None
            last_error = None
            try:
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=1000 if model_type == 'haiku' else 2000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
            except anthropic.APIError as e:
                # If 404 and we have a fallback, try it
                if '404' in str(e) and 'fallback' in model_config:
                    try:
                        response = self.client.messages.create(
                            model=model_config['fallback'],
                            max_tokens=1000 if model_type == 'haiku' else 2000,
                            system=system_prompt,
                            messages=[
                                {"role": "user", "content": user_message}
                            ]
                        )
                        model_name = model_config['fallback']  # Update to fallback model
                    except Exception as fallback_error:
                        last_error = fallback_error
                else:
                    raise e
            
            if response is None:
                raise last_error if last_error else Exception("Failed to get API response")
            
            # Extract answer
            answer = response.content[0].text
            
            # Use actual token counts from API response
            # Anthropic API returns usage object with input_tokens and output_tokens
            if hasattr(response, 'usage') and response.usage:
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
            else:
                # Fallback to estimation if usage not available
                input_tokens = self.estimate_tokens(system_prompt + user_message)
                output_tokens = self.estimate_tokens(answer)
            
            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, model_type)
            
            # P1: Cache the result
            self.cache[question_hash] = answer
            
            # Update session stats - IMPORTANT: Update before returning
            self.session_queries += 1
            self.session_cost += cost
            
            # Sync with session_state to persist across reruns
            import streamlit as st
            st.session_state.ai_stats['queries'] = self.session_queries
            st.session_state.ai_stats['cost'] = self.session_cost
            st.session_state.ai_stats['cached'] = self.session_cached
            
            return {
                'answer': answer,
                'cached': False,
                'cost': cost,
                'model': model_type,
                'model_name': model_name,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'session_stats': self.get_session_stats()
            }
            
        except anthropic.APIError as e:
            # Still count as a query attempt (but no cost)
            self.session_queries += 1
            # Sync with session_state
            import streamlit as st
            st.session_state.ai_stats['queries'] = self.session_queries
            st.session_state.ai_stats['cached'] = self.session_cached
            return {
                'answer': f"API Error: {e}",
                'cached': False,
                'error': True,
                'cost': 0
            }
        except Exception as e:
            # Still count as a query attempt (but no cost)
            self.session_queries += 1
            # Sync with session_state
            import streamlit as st
            st.session_state.ai_stats['queries'] = self.session_queries
            st.session_state.ai_stats['cached'] = self.session_cached
            return {
                'answer': f"Error: {e}",
                'cached': False,
                'error': True,
                'cost': 0
            }
    
    def get_session_stats(self):
        """Get current session statistics"""
        # Sync from session_state first to ensure we have latest values
        import streamlit as st
        if 'ai_stats' in st.session_state:
            self.session_queries = st.session_state.ai_stats['queries']
            self.session_cost = st.session_state.ai_stats['cost']
            self.session_cached = st.session_state.ai_stats['cached']
        
        return {
            'queries': self.session_queries,
            'cached': self.session_cached,
            'cost': self.session_cost,
            'cache_rate': (self.session_cached / max(self.session_queries + self.session_cached, 1)) * 100
        }
    
    def analyze_cash_flow(self):
        """Quick cash flow analysis"""
        return self.query("Analyze my current cash flow. Is it healthy? Any concerns?", force_model='haiku')
    
    def compare_projects(self):
        """Compare active projects"""
        return self.query("Compare my active projects. Which need attention?")
    
    def suggest_actions(self):
        """Get action recommendations"""
        return self.query("What are my top 3 priorities this month?")
    
    def identify_trends(self):
        """Identify trends"""
        return self.query("What trends do you see in my 3-month cash flow?", force_model='haiku')
