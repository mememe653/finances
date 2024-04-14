import math

def invest(amount, num_weeks, rate_of_return, brokerage):
    weekly_ror = 100 * (math.exp(math.log(1 + rate_of_return / 100) / 52) - 1)
    return (amount - brokerage) * (1 + weekly_ror / 100) ** num_weeks

if __name__ == "__main__":
    annual_ror = 10
    brokerage = 9.5

    num_additional_weeks = 1000

    amount1 = invest(2000, 52 + num_additional_weeks, annual_ror, brokerage) \
            + invest(2000, 50 + num_additional_weeks, annual_ror, brokerage) \
            + invest(2000, 48 + num_additional_weeks, annual_ror, brokerage)
    amount2 = invest(4000, 50 + num_additional_weeks, annual_ror, brokerage) \
            + invest(2000, 48 + num_additional_weeks, annual_ror, brokerage)
    amount3 = invest(6000, 48 + num_additional_weeks, annual_ror, brokerage)

    print(f"Amount 1 = {amount1}")
    print(f"Amount 2 = {amount2}")
    print(f"Amount 3 = {amount3}")
