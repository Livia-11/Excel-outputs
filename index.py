import pandas as pd
import numpy as np
import numpy_financial as npf

def calculate_complete_financials():
    # Initial Investment Breakdown (from document)
    initial_investments = {
        'Buildings': 820_000_000,
        'Limestone Equipment': 451_185_381,
        'Staff Salaries (Year 1)': 643_000_000,
        'Laboratory Equipment': 156_639_720,
        'Lime Granulation Equipment': 841_803_796,
        'Training': 60_000_000,
        'Utilities Setup': 184_500_000,
        'Laboratory Installation': 20_136_005,
        'Factory Installation': 34_716_250,
        'Packaging (6 months)': 874_800_000,
        'Fertilizer Plates': 30_000_000,
        'Market Research': 214_000_000,
        'Contingency (5%)': 216_539_058,
    }
    
    total_investment = sum(initial_investments.values())
    
    # Production Parameters
    daily_production = 600  # tons per day
    lime_price_per_kg = 103  # RWF
    working_days_per_year = 323.62  # from document
    annual_production = daily_production * working_days_per_year
    
    # Revenue Calculations
    annual_revenue = annual_production * 1000 * lime_price_per_kg  # converting tons to kg
    
    # ESTIMATED Missing Costs (based on industry standards)
    
    # 1. Raw Material Costs
    # Typically 20-30% of revenue in mining operations
    raw_material_cost_per_ton = lime_price_per_kg * 1000 * 0.25  # 25% of selling price
    annual_raw_material_cost = raw_material_cost_per_ton * annual_production
    
    # 2. Maintenance Costs
    # Usually 3-5% of equipment cost annually
    equipment_value = initial_investments['Limestone Equipment'] + initial_investments['Lime Granulation Equipment']
    annual_maintenance = equipment_value * 0.04  # 4% of equipment value
    
    # 3. Working Capital Requirements
    # Typically 2-3 months of operating costs
    monthly_operating_costs = {
        'Raw Materials': annual_raw_material_cost / 12,
        'Staff Salaries': 643_000_000 / 12,
        'Utilities': 24_000_000 / 12,
        'Packaging Materials': (874_800_000 * 2) / 12,
        'Maintenance': annual_maintenance / 12,
        'Marketing': 214_000_000 / 12,
        'Other Operating': 60_180_000 / 12
    }
    working_capital = sum(monthly_operating_costs.values()) * 3  # 3 months coverage
    
    # 4. Tax Implications
    # Rwanda corporate tax rate is 30%
    tax_rate = 0.30
    
    # 5. Inflation Rate
    # Rwanda's average inflation rate
    inflation_rate = 0.05  # 5% annual inflation
    
    # Complete Annual Operating Costs
    annual_operating_costs = {
        'Raw Materials': annual_raw_material_cost,
        'Staff Salaries': 643_000_000,
        'Utilities': 24_000_000,
        'Packaging Materials': 874_800_000 * 2,
        'Maintenance': annual_maintenance,
        'Marketing': 214_000_000,
        'Other Operating': 60_180_000
    }
    
    total_annual_opex = sum(annual_operating_costs.values())
    
    # Calculate EBIT (Earnings Before Interest and Taxes)
    ebit = annual_revenue - total_annual_opex
    
    # Calculate Tax
    tax = max(0, ebit * tax_rate)
    
    # Calculate Net Operating Profit After Tax (NOPAT)
    nopat = ebit - tax
    
    # Create 10-year cash flow projections
    years = range(11)  # 0 to 10
    discount_rate = 0.13  # 13% as specified
    
    # Initial cash flow (Year 0)
    cash_flows = [-total_investment - working_capital]
    
    # Project future cash flows with inflation adjustment
    for year in range(1, 11):
        revenue_inflated = annual_revenue * (1 + inflation_rate) ** year
        costs_inflated = total_annual_opex * (1 + inflation_rate) ** year
        ebit_inflated = revenue_inflated - costs_inflated
        tax_inflated = max(0, ebit_inflated * tax_rate)
        nopat_inflated = ebit_inflated - tax_inflated
        cash_flows.append(nopat_inflated)
    
    # Add working capital recovery in final year
    cash_flows[-1] += working_capital
    
    # Calculate NPV
    npv = npf.npv(discount_rate, cash_flows)
    
    # Calculate IRR
    irr = npf.irr(cash_flows)
    
    # Calculate Payback Period
    cumulative_cash_flow = np.cumsum(cash_flows)
    payback_period = np.where(cumulative_cash_flow >= 0)[0][0] / 12  # in years
    
    # Create results DataFrame
    results_df = pd.DataFrame({
        'Metric': [
            'Initial Investment (RWF)',
            'Working Capital Required (RWF)',
            'Annual Revenue (RWF)',
            'Annual Operating Costs (RWF)',
            'Annual Raw Material Costs (RWF)',
            'Annual Maintenance Costs (RWF)',
            'First Year NOPAT (RWF)',
            'NPV (RWF)',
            'IRR',
            'Payback Period (Years)'
        ],
        'Value': [
            total_investment,
            working_capital,
            annual_revenue,
            total_annual_opex,
            annual_raw_material_cost,
            annual_maintenance,
            nopat,
            npv,
            irr,
            payback_period
        ]
    })
    
    # Create detailed cash flow DataFrame
    cash_flow_df = pd.DataFrame({
        'Year': years,
        'Cash Flow (RWF)': cash_flows,
        'Cumulative Cash Flow (RWF)': cumulative_cash_flow,
        'Discounted Cash Flow (RWF)': [cf / (1 + discount_rate) ** year for year, cf in zip(years, cash_flows)]
    })
    
    # Create operating costs breakdown DataFrame
    opex_df = pd.DataFrame({
        'Cost Category': list(annual_operating_costs.keys()),
        'Annual Cost (RWF)': list(annual_operating_costs.values()),
        'Percentage of Total': [cost/total_annual_opex * 100 for cost in annual_operating_costs.values()]
    })
    
    return results_df, cash_flow_df, opex_df

# Calculate and format results
results_df, cash_flow_df, opex_df = calculate_complete_financials()

# Format and save results
pd.options.display.float_format = '{:,.2f}'.format
results_df.to_excel('lime_plant_financial_analysis_complete.xlsx', index=False)
cash_flow_df.to_excel('lime_plant_cash_flows_complete.xlsx')