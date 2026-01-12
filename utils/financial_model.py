"""
Financial Modeling Engine for Industrial Real Estate Development
Includes development phase with construction loans and capitalized interest
"""

import numpy as np
from numpy_financial import irr, npv
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

@dataclass
class DevelopmentPhase:
    """Development phase cash flows"""
    total_development_cost: float  # Land + Construction + Fees
    equity_contribution: float
    debt_amount: float
    construction_loan_rate: float
    construction_duration_months: int
    draw_schedule: List[float]  # % of construction cost per period
    capitalized_interest: float
    
@dataclass
class OperatingPhase:
    """Operating phase cash flows"""
    annual_noi: List[float]  # Net Operating Income per year
    debt_service: List[float]  # Annual debt service
    cash_flow_before_tax: List[float]
    
@dataclass
class ExitPhase:
    """Exit phase cash flows"""
    exit_value: float
    remaining_loan_balance: float
    equity_proceeds: float
    total_return: float

class FinancialModel:
    """
    Complete financial modeling engine for real estate development
    
    Phases:
    1. Development (acquisition + construction)
    2. Operating (rental income)
    3. Exit (sale)
    """
    
    def __init__(self, project_params: dict):
        """
        Initialize with project parameters
        
        Args:
            project_params: Dictionary with all project parameters
        """
        self.params = project_params
        self.discount_rate = 0.12  # Default 12% for NPV
        
    def calculate_total_development_cost(self) -> Dict:
        """
        Calculate total development cost including all fees and contingency
        
        Returns:
            Dictionary with cost breakdown
        """
        land_cost = self.params.get('purchase_price', 0)
        acquisition_costs = self.params.get('acquisition_costs', 0)
        construction_cost = self.params.get('construction_cost', 0)
        contingency_pct = self.params.get('contingency_percentage', 10) / 100
        
        # Hard costs
        hard_costs = construction_cost
        contingency = hard_costs * contingency_pct
        
        # Soft costs (typically 5-10% of hard costs)
        soft_costs_pct = 0.07  # 7% default
        soft_costs = hard_costs * soft_costs_pct
        
        # Total development cost
        total_land = land_cost + acquisition_costs
        total_construction = hard_costs + contingency + soft_costs
        total_development_cost = total_land + total_construction
        
        return {
            'land_cost': land_cost,
            'acquisition_costs': acquisition_costs,
            'total_land': total_land,
            'hard_costs': hard_costs,
            'contingency': contingency,
            'soft_costs': soft_costs,
            'total_construction': total_construction,
            'total_development_cost': total_development_cost
        }
    
    def calculate_financing_structure(self, total_cost: float) -> Dict:
        """
        Calculate equity and debt amounts based on LTV
        
        Args:
            total_cost: Total development cost
            
        Returns:
            Dictionary with financing breakdown
        """
        equity_pct = self.params.get('equity_percentage', 30) / 100
        debt_pct = self.params.get('debt_percentage', 70) / 100
        
        equity_required = total_cost * equity_pct
        debt_amount = total_cost * debt_pct
        
        # Construction loan (typically higher rate)
        construction_rate = self.params.get('interest_rate', 6.0) / 100 + 0.015  # +150bps
        
        # Permanent loan (for post-completion)
        perm_rate = self.params.get('interest_rate', 6.0) / 100
        loan_term = self.params.get('loan_term_years', 25)
        
        return {
            'equity_required': equity_required,
            'debt_amount': debt_amount,
            'construction_loan_rate': construction_rate,
            'permanent_loan_rate': perm_rate,
            'loan_term_years': loan_term
        }
    
    def calculate_construction_draws(self) -> List[Dict]:
        """
        Calculate construction loan draw schedule
        
        Returns:
            List of monthly draws during construction
        """
        construction_duration = self.params.get('construction_duration_months', 12)
        cost_breakdown = self.calculate_total_development_cost()
        total_construction = cost_breakdown['total_construction']
        
        financing = self.calculate_financing_structure(cost_breakdown['total_development_cost'])
        debt_amount = financing['debt_amount']
        
        # Typical draw schedule (S-curve pattern)
        # Month 1-2: 5% each (mobilization)
        # Month 3-10: 10% each (peak construction)
        # Month 11-12: 7.5% each (finishing)
        
        if construction_duration <= 12:
            draw_schedule = [0.05, 0.05, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.075, 0.075][:construction_duration]
        else:
            # For longer projects, distribute evenly
            draw_schedule = [1.0 / construction_duration] * construction_duration
        
        # Normalize to 100%
        total_pct = sum(draw_schedule)
        draw_schedule = [d / total_pct for d in draw_schedule]
        
        # Calculate monthly draws
        draws = []
        cumulative_draw = 0
        cumulative_interest = 0
        
        for month in range(construction_duration):
            draw_pct = draw_schedule[month]
            draw_amount = total_construction * draw_pct
            cumulative_draw += draw_amount
            
            # Calculate interest on outstanding balance
            monthly_rate = financing['construction_loan_rate'] / 12
            interest = cumulative_draw * monthly_rate
            cumulative_interest += interest
            
            draws.append({
                'month': month + 1,
                'draw_pct': draw_pct * 100,
                'draw_amount': draw_amount,
                'cumulative_draw': cumulative_draw,
                'monthly_interest': interest,
                'cumulative_interest': cumulative_interest,
                'outstanding_balance': cumulative_draw + cumulative_interest
            })
        
        return draws
    
    def calculate_annual_noi(self) -> List[float]:
        """
        Calculate Net Operating Income for each year
        
        Returns:
            List of annual NOI
        """
        monthly_rent = self.params.get('estimated_monthly_rent', 0)
        rent_growth_rate = self.params.get('rent_growth_rate', 3.0) / 100
        occupancy_rate = self.params.get('occupancy_rate', 95.0) / 100
        opex_ratio = self.params.get('operating_expense_ratio', 30.0) / 100
        holding_period = self.params.get('holding_period_years', 10)
        construction_duration = self.params.get('construction_duration_months', 12)
        
        # First year is partial (after construction)
        months_in_year_1 = 12 - construction_duration
        
        noi_list = []
        
        for year in range(holding_period + 1):  # +1 for partial first year
            if year == 0:
                # Partial first year
                if months_in_year_1 <= 0:
                    noi_list.append(0)
                    continue
                
                annual_rent = monthly_rent * 12
                effective_rent = annual_rent * occupancy_rate * (months_in_year_1 / 12)
                opex = effective_rent * opex_ratio
                noi = effective_rent - opex
                noi_list.append(noi)
            else:
                # Full years with rent growth
                annual_rent = monthly_rent * 12 * ((1 + rent_growth_rate) ** year)
                effective_rent = annual_rent * occupancy_rate
                opex = effective_rent * opex_ratio
                noi = effective_rent - opex
                noi_list.append(noi)
        
        return noi_list
    
    def calculate_debt_service(self, loan_amount: float, rate: float, term: int) -> float:
        """
        Calculate annual debt service (mortgage payment)
        
        Args:
            loan_amount: Principal amount
            rate: Annual interest rate (decimal)
            term: Loan term in years
            
        Returns:
            Annual debt service payment
        """
        if rate == 0 or term == 0:
            return 0
        
        monthly_rate = rate / 12
        num_payments = term * 12
        
        # Monthly payment formula
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                         ((1 + monthly_rate)**num_payments - 1)
        
        annual_payment = monthly_payment * 12
        return annual_payment
    
    def calculate_loan_balance(self, original_loan: float, rate: float, term: int, years_elapsed: int) -> float:
        """
        Calculate remaining loan balance after certain years
        
        Args:
            original_loan: Original loan amount
            rate: Annual interest rate
            term: Total loan term in years
            years_elapsed: Years since loan start
            
        Returns:
            Remaining balance
        """
        if years_elapsed >= term:
            return 0
        
        monthly_rate = rate / 12
        num_payments = term * 12
        payments_made = years_elapsed * 12
        
        # Remaining balance formula
        remaining_payments = num_payments - payments_made
        
        monthly_payment = original_loan * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                         ((1 + monthly_rate)**num_payments - 1)
        
        remaining_balance = monthly_payment * ((1 + monthly_rate)**remaining_payments - 1) / \
                           (monthly_rate * (1 + monthly_rate)**remaining_payments)
        
        return remaining_balance
    
    def calculate_exit_value(self, final_noi: float) -> float:
        """
        Calculate property value at exit based on cap rate
        
        Args:
            final_noi: NOI in final year
            
        Returns:
            Exit value
        """
        exit_cap_rate = self.params.get('exit_cap_rate', 6.5) / 100
        
        if exit_cap_rate == 0:
            return 0
        
        exit_value = final_noi / exit_cap_rate
        return exit_value
    
    def build_complete_cash_flow(self) -> Dict:
        """
        Build complete cash flow model from development through exit
        
        Returns:
            Dictionary with all cash flows and metrics
        """
        # Development costs
        costs = self.calculate_total_development_cost()
        total_dev_cost = costs['total_development_cost']
        
        # Financing
        financing = self.calculate_financing_structure(total_dev_cost)
        equity_required = financing['equity_required']
        
        # Construction phase
        draws = self.calculate_construction_draws()
        capitalized_interest = draws[-1]['cumulative_interest'] if draws else 0
        
        # Total loan including capitalized interest
        total_loan_at_completion = financing['debt_amount'] + capitalized_interest
        
        # Operating phase
        noi_list = self.calculate_annual_noi()
        
        # Permanent loan debt service
        perm_loan_payment = self.calculate_debt_service(
            total_loan_at_completion,
            financing['permanent_loan_rate'],
            financing['loan_term_years']
        )
        
        # Build annual cash flows
        holding_period = self.params.get('holding_period_years', 10)
        annual_cash_flows = []
        
        # Year 0: Development phase (negative cash flow = equity investment)
        annual_cash_flows.append({
            'year': 0,
            'period': 'Development',
            'equity_invested': -equity_required,
            'noi': 0,
            'debt_service': 0,
            'cash_flow': -equity_required,
            'cumulative_cash_flow': -equity_required
        })
        
        cumulative_cf = -equity_required
        
        # Operating years
        for year in range(1, holding_period + 1):
            noi = noi_list[year] if year < len(noi_list) else noi_list[-1]
            cash_flow = noi - perm_loan_payment
            cumulative_cf += cash_flow
            
            annual_cash_flows.append({
                'year': year,
                'period': 'Operating',
                'equity_invested': 0,
                'noi': noi,
                'debt_service': perm_loan_payment,
                'cash_flow': cash_flow,
                'cumulative_cash_flow': cumulative_cf
            })
        
        # Exit year
        final_noi = noi_list[-1]
        exit_value = self.calculate_exit_value(final_noi)
        remaining_loan = self.calculate_loan_balance(
            total_loan_at_completion,
            financing['permanent_loan_rate'],
            financing['loan_term_years'],
            holding_period
        )
        
        equity_proceeds = exit_value - remaining_loan
        exit_cash_flow = equity_proceeds
        
        annual_cash_flows.append({
            'year': holding_period,
            'period': 'Exit',
            'equity_invested': 0,
            'noi': final_noi,
            'debt_service': 0,
            'exit_value': exit_value,
            'loan_payoff': remaining_loan,
            'equity_proceeds': equity_proceeds,
            'cash_flow': exit_cash_flow,
            'cumulative_cash_flow': cumulative_cf + exit_cash_flow
        })
        
        return {
            'development_costs': costs,
            'financing': financing,
            'construction_draws': draws,
            'capitalized_interest': capitalized_interest,
            'total_loan_at_completion': total_loan_at_completion,
            'annual_cash_flows': annual_cash_flows,
            'exit_value': exit_value,
            'remaining_loan': remaining_loan,
            'equity_proceeds': equity_proceeds
        }
    
    def calculate_returns(self) -> Dict:
        """
        Calculate all return metrics
        
        Returns:
            Dictionary with IRR, NPV, multiples, etc.
        """
        cash_flow_model = self.build_complete_cash_flow()
        annual_cfs = cash_flow_model['annual_cash_flows']
        
        # Extract cash flows for IRR/NPV calculation
        cash_flows = []
        for cf in annual_cfs:
            if cf['period'] == 'Exit':
                # Combine operating CF + exit proceeds
                cash_flows.append(cf['cash_flow'])
            else:
                cash_flows.append(cf['cash_flow'])
        
        # Calculate IRR
        try:
            project_irr = irr(cash_flows) * 100  # Convert to percentage
        except:
            project_irr = None
        
        # Calculate NPV
        try:
            project_npv = npv(self.discount_rate, cash_flows)
        except:
            project_npv = None
        
        # Equity Multiple
        equity_invested = abs(annual_cfs[0]['equity_invested'])
        equity_returned = cash_flow_model['equity_proceeds']
        
        if equity_invested > 0:
            equity_multiple = equity_returned / equity_invested
        else:
            equity_multiple = None
        
        # Cash-on-Cash (Year 1)
        if len(annual_cfs) > 1 and equity_invested > 0:
            year_1_cf = annual_cfs[1]['cash_flow']
            cash_on_cash = (year_1_cf / equity_invested) * 100
        else:
            cash_on_cash = None
        
        # Average DSCR
        dscr_list = []
        for cf in annual_cfs:
            if cf['period'] == 'Operating' and cf['debt_service'] > 0:
                dscr = cf['noi'] / cf['debt_service']
                dscr_list.append(dscr)
        
        avg_dscr = sum(dscr_list) / len(dscr_list) if dscr_list else None
        
        # Profit margin
        total_dev_cost = cash_flow_model['development_costs']['total_development_cost']
        exit_value = cash_flow_model['exit_value']
        
        if total_dev_cost > 0:
            profit_margin = ((exit_value - total_dev_cost) / total_dev_cost) * 100
        else:
            profit_margin = None
        
        return {
            'irr': project_irr,
            'npv': project_npv,
            'equity_multiple': equity_multiple,
            'cash_on_cash_return': cash_on_cash,
            'avg_dscr': avg_dscr,
            'profit_margin': profit_margin,
            'total_equity_invested': equity_invested,
            'total_equity_returned': equity_returned,
            'total_profit': equity_returned - equity_invested,
            'cash_flow_model': cash_flow_model
        }


def format_currency(amount: float) -> str:
    """Format number as currency"""
    if amount is None:
        return "N/A"
    return f"${amount:,.0f}"

def format_percentage(rate: float) -> str:
    """Format number as percentage"""
    if rate is None:
        return "N/A"
    return f"{rate:.2f}%"
