"""Test financial model calculations"""

from utils.financial_model import FinancialModel, format_currency, format_percentage

# 测试项目参数
test_params = {
    'purchase_price': 5000000,
    'acquisition_costs': 250000,
    'construction_cost': 10000000,
    'construction_duration_months': 18,
    'contingency_percentage': 10.0,
    'equity_percentage': 30.0,
    'debt_percentage': 70.0,
    'interest_rate': 6.0,
    'loan_term_years': 25,
    'estimated_monthly_rent': 150000,
    'rent_growth_rate': 3.0,
    'occupancy_rate': 95.0,
    'operating_expense_ratio': 30.0,
    'holding_period_years': 10,
    'exit_cap_rate': 6.5
}

print("="*60)
print("FINANCIAL MODEL TEST")
print("="*60)

# 创建模型
model = FinancialModel(test_params)

# 测试1: 开发成本
print("\n1️⃣ DEVELOPMENT COSTS:")
costs = model.calculate_total_development_cost()
print(f"   Land + Acquisition: {format_currency(costs['total_land'])}")
print(f"   Construction: {format_currency(costs['total_construction'])}")
print(f"   Total Development: {format_currency(costs['total_development_cost'])}")

# 测试2: 融资结构
print("\n2️⃣ FINANCING STRUCTURE:")
financing = model.calculate_financing_structure(costs['total_development_cost'])
print(f"   Equity Required: {format_currency(financing['equity_required'])}")
print(f"   Debt Amount: {format_currency(financing['debt_amount'])}")
print(f"   Construction Rate: {format_percentage(financing['construction_loan_rate']*100)}")

# 测试3: 施工贷款提款
print("\n3️⃣ CONSTRUCTION LOAN DRAWS:")
draws = model.calculate_construction_draws()
print(f"   Duration: {len(draws)} months")
print(f"   Total Drawn: {format_currency(draws[-1]['cumulative_draw'])}")
print(f"   Capitalized Interest: {format_currency(draws[-1]['cumulative_interest'])}")
print(f"\n   First 3 months:")
for i in range(min(3, len(draws))):
    d = draws[i]
    print(f"   Month {d['month']}: Draw {format_currency(d['draw_amount'])} | Interest {format_currency(d['monthly_interest'])}")

# 测试4: 年度NOI
print("\n4️⃣ ANNUAL NOI:")
noi_list = model.calculate_annual_noi()
print(f"   Year 1 (partial): {format_currency(noi_list[0])}")
print(f"   Year 2: {format_currency(noi_list[1])}")
print(f"   Year 10: {format_currency(noi_list[-1])}")

# 测试5: 完整现金流
print("\n5️⃣ COMPLETE CASH FLOW MODEL:")
cf_model = model.build_complete_cash_flow()
print(f"   Total Loan at Completion: {format_currency(cf_model['total_loan_at_completion'])}")
print(f"   Exit Value: {format_currency(cf_model['exit_value'])}")
print(f"   Equity Proceeds: {format_currency(cf_model['equity_proceeds'])}")

# 测试6: 回报指标
print("\n6️⃣ RETURN METRICS:")
returns = model.calculate_returns()
print(f"   IRR: {format_percentage(returns['irr'])}")
print(f"   NPV: {format_currency(returns['npv'])}")
print(f"   Equity Multiple: {returns['equity_multiple']:.2f}x")
print(f"   Cash-on-Cash: {format_percentage(returns['cash_on_cash_return'])}")
print(f"   Avg DSCR: {returns['avg_dscr']:.2f}x")
print(f"   Profit Margin: {format_percentage(returns['profit_margin'])}")

print("\n7️⃣ INVESTMENT SUMMARY:")
print(f"   Total Invested: {format_currency(returns['total_equity_invested'])}")
print(f"   Total Returned: {format_currency(returns['total_equity_returned'])}")
print(f"   Total Profit: {format_currency(returns['total_profit'])}")

print("\n" + "="*60)
print("✅ All calculations completed successfully!")
print("="*60)