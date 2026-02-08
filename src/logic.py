# src/logic.py

def format_currency(amount):
    return f"${int(amount):,}"

def calculate_taxes(gross_salary, state):
    """Calculate monthly net pay after federal and state taxes"""
    fed_tax = 0.22
    no_tax_states = ['TX', 'FL', 'WA', 'NV', 'TN', 'NH', 'SD', 'WY', 'AK']
    state_tax = 0.00 if state in no_tax_states else 0.05
    monthly_net = (gross_salary * (1 - (fed_tax + state_tax))) / 12
    return int(monthly_net)

def calculate_net_monthly(gross_salary, debt_amount=0, state='TX'):
    """
    Calculate monthly net income after taxes and student loan payments.
    Uses standard 10-year repayment plan for student loans.
    """
    # Calculate taxes
    monthly_net = calculate_taxes(gross_salary, state)
    
    # Calculate monthly loan payment (10-year standard repayment at 5% interest)
    if debt_amount > 0:
        # Monthly payment formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        # Where P = principal, r = monthly rate, n = number of payments
        monthly_rate = 0.05 / 12  # 5% annual rate
        n_payments = 120  # 10 years
        monthly_loan_payment = debt_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
        monthly_net -= monthly_loan_payment
    
    return int(monthly_net)

def calculate_thriving_score(monthly_net, rent, col_index):
    """
    UPDATED LOGIC: REAL PURCHASING POWER
    Scores cities on a 0-100 scale based on actual quality of life
    """
    if monthly_net <= 0:
        return 0
    
    # 1. Rent Burden Score (0-35 points)
    # Ideal: Rent < 25% of income = 35 points
    # Acceptable: Rent 25-30% = 25-35 points  
    # Warning: Rent 30-40% = 10-25 points
    # Critical: Rent > 40% = 0-10 points
    rent_ratio = rent / monthly_net
    if rent_ratio <= 0.25:
        rent_score = 35
    elif rent_ratio <= 0.30:
        rent_score = 35 - ((rent_ratio - 0.25) / 0.05) * 10  # 35 to 25
    elif rent_ratio <= 0.40:
        rent_score = 25 - ((rent_ratio - 0.30) / 0.10) * 15  # 25 to 10
    else:
        rent_score = max(0, 10 - ((rent_ratio - 0.40) * 20))
    
    # 2. Discretionary Income Score (0-40 points)
    # This is money left after rent, adjusted for cost of living
    raw_savings = monthly_net - rent
    
    # Adjust for purchasing power (COL normalization)
    real_savings = raw_savings / (col_index / 100) if col_index > 0 else raw_savings
    
    # Score based on real discretionary income
    # $0 = 0 points, $2,000 = 20 points, $4,000 = 30 points, $6,000+ = 40 points
    if real_savings <= 0:
        savings_score = 0
    elif real_savings < 2000:
        savings_score = (real_savings / 2000) * 20
    elif real_savings < 4000:
        savings_score = 20 + ((real_savings - 2000) / 2000) * 10
    elif real_savings < 6000:
        savings_score = 30 + ((real_savings - 4000) / 2000) * 10
    else:
        # Cap at 40 but give credit for exceptional savings
        savings_score = min(40, 40 + ((real_savings - 6000) / 10000) * 5)
    
    # 3. Cost of Living Bonus (0-25 points)
    # Lower COL = bonus points (your money goes further)
    # COL 100 (NYC) = 0 bonus, COL 50 = 25 bonus
    col_bonus = max(0, (100 - col_index) / 2)
    
    # Total Score
    total_score = rent_score + savings_score + col_bonus
    
    return int(max(0, min(100, total_score)))

def get_thriving_score(monthly_net, rent_index, col_index):
    """Wrapper for backward compatibility"""
    return calculate_thriving_score(monthly_net, rent_index, col_index)

def project_savings(monthly_net, rent, col_index, lifestyle='Balanced'):
    """
    Calculate projected monthly savings based on lifestyle choice.
    
    Args:
        monthly_net: Monthly net income after taxes
        rent: Monthly rent cost
        col_index: Cost of living index
        lifestyle: 'Frugal', 'Balanced', or 'Boujee'
    
    Returns:
        Monthly savings amount
    """
    # Lifestyle multipliers for discretionary spending
    lifestyle_multipliers = {
        'Frugal': 0.5,    # 50% of discretionary on fun
        'Balanced': 0.7,   # 70% of discretionary on fun
        'Fancy': 0.9      # 90% of discretionary on fun (going into debt)
    }
    
    multiplier = lifestyle_multipliers.get(lifestyle, 0.7)
    
    # Base living expenses (food, utilities, etc) scaled by COL
    base_expenses = (col_index / 100) * 1200
    
    # Discretionary income
    discretionary = monthly_net - rent - base_expenses
    
    # Spending based on lifestyle
    spending = discretionary * multiplier
    
    # Savings is what's left
    savings = monthly_net - rent - base_expenses - spending
    
    return int(savings)

def project_5yr_wealth(monthly_net, rent, col_index):
    """
    Calculates 5-Year Cumulative Wealth.
    Assumes: 
    - Salary grows 5% per year
    - Rent grows 3% per year
    """
    cumulative_wealth = 0
    current_net = monthly_net
    current_rent = rent
    living_expenses = (col_index / 100) * 1200  # Baseline food/fun

    savings_rate = 0.7  # Assume balanced lifestyle for projection
    
    wealth_timeline = []
    
    for year in range(1, 6):
        yearly_savings = (current_net - current_rent - living_expenses) * 12 * savings_rate
        cumulative_wealth += yearly_savings
        wealth_timeline.append(cumulative_wealth)
        
        # Growth for next year
        current_net *= 1.05  # 5% Raise
        current_rent *= 1.03  # 3% Rent Hike
        living_expenses *= 1.03  # Inflation
        
    return wealth_timeline[-1]  # Return total after 5 years