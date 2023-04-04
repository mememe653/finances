# Have verified this against online mortgage repayment calculator, it is correct
def monthly_repayment(loan_amount, interest_rate, loan_term_yrs):
    monthly_interest_rate = interest_rate / 12
    num_payments = loan_term_yrs * 12
    return (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / \
            ((1 + monthly_interest_rate) ** num_payments - 1)

if __name__ == "__main__":
    print(monthly_repayment(400000, 0.04, 30))
