ANNUAL_HOUSE_APPRECIATION_RATE = 0.06
ANNUAL_SHARE_RATE_OF_RETURN = 0.065

def windfall_comparison(windfall_amount, annual_interest_rate, num_yrs):
    shares = windfall_amount
    loan = windfall_amount
    cgt_discount = 0.5
    tax_rate = 0.45
    for i in range(num_yrs):
        shares *= 1 + ANNUAL_SHARE_RATE_OF_RETURN
        loan *= 1 + annual_interest_rate
        loan_interest = loan - windfall_amount
        cgt = (shares - windfall_amount) * cgt_discount * tax_rate
        shares_profit = shares - cgt - windfall_amount
        print(f'{i+1} years:')
        print(f'Interest = ${loan_interest}')
        print(f'Profit = ${shares_profit}')
        print()

def defensive_repayment(loan_amount, start_interest_rate, end_interest_rate, 
        total_payment):
    first_payment = 0.4 * total_payment
    second_payment = total_payment - first_payment
    loan = loan_amount
    loan *= (1 + start_interest_rate)
    loan -= first_payment
    loan *= (1 + end_interest_rate)
    loan -= second_payment
    return loan


if __name__ == '__main__':
    windfall_amount = 100000
    annual_interest_rate = 0.05
    num_yrs = 30
    windfall_comparison(windfall_amount, annual_interest_rate, num_yrs)

    loan_amount = 100000
    start_interest_rate = 0.05
    end_interest_rate = 0.07
    total_payment = 20000
    loan = defensive_repayment(loan_amount, start_interest_rate, end_interest_rate,
            total_payment)
    print(f'Start interest rate = {start_interest_rate}')
    print(f'End interest rate = {end_interest_rate}')
    print(f'Loan = ${loan}')

    print()

    temp = start_interest_rate
    start_interest_rate = end_interest_rate
    end_interest_rate = temp
    loan = defensive_repayment(loan_amount, start_interest_rate, end_interest_rate, 
            total_payment)
    print(f'Start interest rate = {start_interest_rate}')
    print(f'End interest rate = {end_interest_rate}')
    print(f'Loan = ${loan}')
