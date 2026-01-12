"""
AI Financial Assistant Module
Uses Claude API to provide intelligent financial analysis and queries
"""

import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv
from models.database import DatabaseManager, Asset

# Load environment variables
load_dotenv()

class AIAssistant:
    """AI-powered financial assistant using Claude"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.db = DatabaseManager()
        self.model = "claude-sonnet-4-20250514"
    
    def get_financial_context(self):
        """
        Gather current financial context from database
        
        Returns:
            Dictionary with key financial metrics and data
        """
        context = {}
        
        try:
            # Cash and flow
            context['cash_balance'] = self.db.get_cash_balance()
            
            now = datetime.now()
            context['current_month'] = now.strftime('%B %Y')
            context['monthly_income'] = self.db.get_monthly_income(now.year, now.month)
            context['monthly_expense'] = self.db.get_monthly_expense(now.year, now.month)
            context['net_cash_flow'] = context['monthly_income'] - context['monthly_expense']
            
            # Assets - query directly using session
            session = self.db.get_session()
            try:
                assets = session.query(Asset).all()
                context['total_assets'] = len(assets)
                context['total_asset_value'] = sum(
                    float(a.current_valuation) if a.current_valuation else 0 
                    for a in assets
                )
            finally:
                self.db.close_session(session)
            
            # Projects
            context['active_projects'] = self.db.get_active_projects_count()
            context['total_budget'] = self.db.get_total_projects_budget()
            context['total_spent'] = self.db.get_total_projects_cost()
            context['budget_remaining'] = context['total_budget'] - context['total_spent']
            
            # Recent activity
            recent_transactions = self.db.get_recent_transactions(10)
            context['recent_transactions'] = [
                {
                    'date': tx.transaction_date.strftime('%Y-%m-%d'),
                    'type': tx.transaction_type.value if hasattr(tx.transaction_type, 'value') else str(tx.transaction_type),
                    'category': tx.category,
                    'amount': abs(float(tx.amount)),
                    'description': tx.description[:50] if tx.description else ''
                }
                for tx in recent_transactions
            ]
            
            # Cashflow trend
            trend = self.db.get_cashflow_trend(6)
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
        """
        Format financial context into a readable string for Claude
        
        Args:
            context: Dictionary with financial data
            
        Returns:
            Formatted string
        """
        if 'error' in context:
            return f"Error: {context['error']}"
        
        formatted = f"""
Current Financial Status ({context['current_month']}):

CASH POSITION:
- Current Balance: ${context['cash_balance']:,.2f}
- This Month Income: ${context['monthly_income']:,.2f}
- This Month Expense: ${context['monthly_expense']:,.2f}
- Net Cash Flow: ${context['net_cash_flow']:,.2f}

ASSET PORTFOLIO:
- Total Assets: {context['total_assets']}
- Total Asset Value: ${context['total_asset_value']:,.2f}

PROJECT PORTFOLIO:
- Active Projects: {context['active_projects']}
- Total Project Budget: ${context['total_budget']:,.2f}
- Total Spent: ${context['total_spent']:,.2f}
- Budget Remaining: ${context['budget_remaining']:,.2f}

RECENT TRANSACTIONS (Last 10):
"""
        
        for tx in context['recent_transactions']:
            formatted += f"\n- {tx['date']}: {tx['type']} - {tx['category']} - ${tx['amount']:,.2f} ({tx['description']})"
        
        formatted += "\n\nCASHFLOW TREND (Last 6 months):\n"
        for month_data in context['cashflow_trend']:
            formatted += f"\n- {month_data['month']}: Income ${month_data['income']:,.0f}, Expense ${month_data['expense']:,.0f}, Net ${month_data['net']:,.0f}"
        
        return formatted
    
    def query(self, user_question, include_context=True):
        """
        Send query to Claude with financial context
        
        Args:
            user_question: User's natural language question
            include_context: Whether to include financial data context
            
        Returns:
            Claude's response text
        """
        try:
            # Build system prompt
            system_prompt = """You are an expert financial advisor and analyst specializing in industrial real estate investment and development. 

You have access to the user's current portfolio data including:
- Asset portfolio (properties owned)
- Active development projects  
- Cash flow and transactions
- Financial metrics

Your role is to:
1. Answer questions about their financial position clearly and accurately
2. Provide insightful analysis of trends and patterns
3. Offer practical recommendations based on the data
4. Flag potential concerns or opportunities
5. Use specific numbers from the data to support your analysis

Be concise, professional, and actionable. Format your responses clearly with bullet points where appropriate.
Always cite specific numbers from the data when making points.
If you notice concerning trends, mention them diplomatically.
"""
            
            # Build user message
            if include_context:
                context = self.get_financial_context()
                context_str = self.format_context_for_claude(context)
                
                user_message = f"""Based on my current financial data below, please answer this question:

{user_question}

MY CURRENT FINANCIAL DATA:
{context_str}
"""
            else:
                user_message = user_question
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract text from response
            answer = response.content[0].text
            
            return answer
            
        except anthropic.APIError as e:
            return f"API Error: {e}"
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_cash_flow(self):
        """
        Quick analysis of cash flow health
        
        Returns:
            Analysis text
        """
        question = "Analyze my current cash flow situation. Is it healthy? Are there any concerns or recommendations?"
        return self.query(question)
    
    def compare_projects(self):
        """
        Compare active projects
        
        Returns:
            Comparison analysis
        """
        question = "Compare my active projects. Which ones are performing well vs poorly? Any concerns about budget overruns or delays?"
        return self.query(question)
    
    def suggest_actions(self):
        """
        Get actionable recommendations
        
        Returns:
            Recommendations text
        """
        question = "Based on my complete financial picture, what are the top 3-5 actions I should take this month? Prioritize by importance."
        return self.query(question)
    
    def identify_trends(self):
        """
        Identify trends in the data
        
        Returns:
            Trend analysis
        """
        question = "Looking at my 6-month cash flow trend and recent transactions, what patterns or trends do you notice? What do they tell us about the business trajectory?"
        return self.query(question)


# Convenience functions for common queries
def quick_financial_health_check():
    """Quick financial health assessment"""
    assistant = AIAssistant()
    return assistant.analyze_cash_flow()

def get_monthly_recommendations():
    """Get monthly action items"""
    assistant = AIAssistant()
    return assistant.suggest_actions()