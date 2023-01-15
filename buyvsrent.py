# Need to account for the fact that my wage will grow, at least as fast as inflation
# Need to pay CGT on some of my shares after renting to buy the house before retirement

# A better and fairer way of comparing renting vs buying would be to assume 30% of my
# income goes toward all housing expenses.
# Then you can assume that you make the same amount of money renting vs buying through
# investing in shares, because you will have the same amount to invest in shares in 
# either case.
# Then compare the amount of money lost in each case.
# For renting, this means the 30% of income spent on housing, and also CGT to buy a
# house before retirement.
# For buying, this means the amount of interest I pay on the home loan (plus utilities?), 
# home maintenance costs, and whether the interest is tax-deductible where I live.
# Basically, see the Khan Academy video about buying vs renting!

WEEKS_PER_YEAR = 52
ANNUAL_INFLATION_RATE = 0.04
ANNUAL_HOUSE_APPRECIATION_RATE = 0.06
ANNUAL_SHARE_RATE_OF_RETURN = 0.08

# https://money.stackexchange.com/questions/10066/how-do-i-convert-an-annual-inflation-rate-into-a-monthly-rate
# Is this in fact correct? Is the rate multiplicative or additive?
def annual_to_weekly_rate(annual_rate):
    return (1 + annual_rate) ** (1 / WEEKS_PER_YEAR) - 1

# https://www.mymove.com/mortgage/mortgage-calculation/
def calculate_mortgage_repayment(loan_amt, annual_interest_rate, num_payments):
    interest_rate = annual_to_weekly_rate(annual_interest_rate)
    payment = loan_amt * (interest_rate * (1 + interest_rate) ** num_payments) \
            / ((1 + interest_rate) ** num_payments - 1)
    return payment

def rent(weekly_rent, weekly_utilities, weekly_income, num_yrs):
    debt = 0
    credit = 0
    # I am assuming for now that my wage grows at the same rate as inflation
    weekly_credit = weekly_income - weekly_rent - weekly_utilities
    for i in range(num_yrs * WEEKS_PER_YEAR):
        debt += weekly_rent + weekly_utilities
        debt *= 1 + annual_to_weekly_rate(ANNUAL_INFLATION_RATE)
        weekly_credit *= 1 + annual_to_weekly_rate(ANNUAL_INFLATION_RATE)
        credit += weekly_credit
        credit *= 1 + annual_to_weekly_rate(ANNUAL_SHARE_RATE_OF_RETURN)
    return debt, credit

def buy(house_purchase_price, annual_interest_rate, weekly_income, num_yrs):
    loan = 0.8 * house_purchase_price
    num_payments = num_yrs * WEEKS_PER_YEAR
    payment = calculate_mortgage_repayment(loan, annual_interest_rate, num_payments)
    weekly_interest_rate = annual_to_weekly_rate(annual_interest_rate)
    total_interest = 0
    for _ in range(num_payments):
        interest = loan * weekly_interest_rate
        principal = payment - interest
        total_interest += interest
        loan -= principal
    house_value = house_purchase_price * (1 + ANNUAL_HOUSE_APPRECIATION_RATE) ** num_yrs
    credit = 0
    weekly_rate_of_return = annual_to_weekly_rate(ANNUAL_SHARE_RATE_OF_RETURN)
    for _ in range(num_yrs * WEEKS_PER_YEAR):
        credit += weekly_income - payment
        credit *= (1 + weekly_rate_of_return)
    credit += house_value
    debt = total_interest
    return debt, credit

def calculate_home_loan(weekly_repayment, weekly_interest_rate, num_payments):
    loan = weekly_repayment * ((1 + weekly_interest_rate) ** num_payments - 1) \
            / (weekly_interest_rate * (1 + weekly_interest_rate) ** num_payments)
    return loan

# Note that I have done this wrong, because I am directly summing costs
# at different time periods, which I should not do because the value of money changes
# over time due to inflation. Similarly for buy_better()?
# I think I should convert all costs to present-day money, for fair comparison.
def rent_better(weekly_income, house_purchase_price, num_yrs):
    weekly_rent = 0.3 * weekly_income
    cost = 0
    for _ in range(num_yrs * WEEKS_PER_YEAR):
        cost += weekly_rent
        cost *= 1 + annual_to_weekly_rate(ANNUAL_INFLATION_RATE)
    house_price = house_purchase_price * (1 + ANNUAL_HOUSE_APPRECIATION_RATE) ** num_yrs
    tax_bracket = 0.45
    cgt_discount = 0.5
    cgt = 1 / (1 - cgt_discount * tax_bracket) * house_price - house_price
    cost += cgt
    return cost

# https://www.mymove.com/mortgage/mortgage-calculation/
# Also consider the opportunity cost of not investing the house deposit in shares
def buy_better(weekly_income, annual_interest_rate, num_yrs):
    weekly_repayment = 0.3 * weekly_income
    weekly_interest_rate = annual_to_weekly_rate(annual_interest_rate)
    num_payments = num_yrs * WEEKS_PER_YEAR
    loan = calculate_home_loan(weekly_repayment, weekly_interest_rate, num_payments)
    total_interest = 0
    for _ in range(num_payments):
        interest = loan * weekly_interest_rate
        principal = weekly_repayment - interest
        total_interest += interest
        loan -= principal
    cost = total_interest
    return cost


if __name__ == '__main__':
    weekly_rent = 150
    weekly_utilities = 150
    weekly_income = 1000
    num_yrs = 30
    debt, credit = rent(weekly_rent, weekly_utilities, weekly_income, num_yrs)
    print('============')
    print('  Renting')
    print('============')
    print()
    print(f'Weekly rent = ${weekly_rent}')
    print(f'Weekly utilities = ${weekly_utilities}')
    print(f'Weekly income = ${weekly_income}')
    print(f'Number of years = {num_yrs}')
    print()
    print(f'+ ${credit}')
    print(f'- ${debt}')
    print(f'= ${credit - debt}')
    
    print()
    print()
    print()

    house_purchase_price = 500000
    annual_interest_rate = 0.04
    weekly_income = 1000
    num_yrs = 30
    debt, credit = buy(house_purchase_price, annual_interest_rate, weekly_income, num_yrs)
    print('============')
    print('   Buying')
    print('============')
    print()
    print(f'House purchase price = ${house_purchase_price}')
    print(f'Annual interest rate = ${annual_interest_rate}')
    print(f'Weekly income = ${weekly_income}')
    print(f'Number of years = {num_yrs}')
    print()
    print(f'+ ${credit}')
    print(f'- ${debt}')
    print(f'= ${credit - debt}')

    print()
    print()
    print()

    weekly_income = 1000
    annual_interest_rate = 0.04
    num_yrs = 30

    weekly_repayment = 0.3 * weekly_income
    weekly_interest_rate = annual_to_weekly_rate(annual_interest_rate)
    num_payments = num_yrs * WEEKS_PER_YEAR

    loan = calculate_home_loan(weekly_repayment, weekly_interest_rate, num_payments)

    house_price = loan / 0.8

    cost = rent_better(weekly_income, house_price, num_yrs)
    print('==================')
    print(' Renting (better)')
    print('==================')
    print()
    print(f'Weekly income = ${weekly_income}')
    print(f'House purchase price = ${house_price}')
    print(f'Number of years = {num_yrs}')
    print()
    print(f'- ${cost}')

    print()
    print()
    print()

    cost = buy_better(weekly_income, annual_interest_rate, num_yrs)
    print('=================')
    print(' Buying (better)')
    print('=================')
    print()
    print(f'Weekly income = ${weekly_income}')
    print(f'Annual interest rate = {annual_interest_rate}')
    print(f'Number of years = {num_yrs}')
    print()
    print(f'-  ${cost}')
