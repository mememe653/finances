import math

def apply_inflation(amount, time, annual_inflation_rate):
    weekly_inflation_rate = (math.exp(math.log(1 + annual_inflation_rate / 100) / 52) - 1) * 100
    return amount * (1 + weekly_inflation_rate / 100) ** time


def write_params_file(params):
    in_file = open("input_files/params.txt", "w")
    in_file.write(f"INFLATION_RATE {params['inflation_rate']}\n")
    in_file.write(f"HOME_APPRECIATION_RATE {params['home_appreciation_rate']}\n")
    in_file.write(f"HOME_LOAN_INTEREST_RATE {params['home_loan_interest_rate']}\n")
    in_file.write(f"CAR_LOAN_INTEREST_RATE {params['car_loan_interest_rate']}\n")
    in_file.write(f"HECS_INDEXATION_RATE {params['hecs_indexation_rate']}\n")
    in_file.write(f"SHARES_ROR {params['shares_ror']}\n")
    in_file.write(f"SUPER_ROR {params['super_ror']}\n")
    in_file.close()


def write_tax_brackets_file(initial_tax_brackets, num_weeks, annual_inflation_rate):
    in_file = open("input_files/tax_brackets.txt", "w")
    for week in range(num_weeks):
        for bracket in initial_tax_brackets:
            in_file.write(f"{apply_inflation(bracket, week, annual_inflation_rate)} ")
        in_file.write("\n")
    in_file.close()


class Home:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/home.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.buy_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} BUY {transaction}\n")
            if week in self.sell_list:
                for _ in self.sell_list[week]:
                    self.in_file.write(f"{week} SELL\n")
        self.in_file.close()

    def buy(self, amount, time):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append(apply_inflation(amount, time, self.inflation_rate))

    def sell(self, time):
        if time not in self.sell_list:
            self.sell_list[time] = []
        self.sell_list[time].append(time)


class HomeLoan:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/home_loan.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.buy_list = {}
        self.buy_all_list = {}
        self.pay_list = {}
        self.pay_all_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} START {transaction['amount']} " \
                                        f"{transaction['duration']}\n")
            if week in self.pay_list:
                for transaction in self.pay_list[week]:
                    self.in_file.write(f"{week} PAY {transaction}\n")
            if week in self.buy_all_list:
                self.in_file.write(f"{week} START ALL {self.buy_all_list[week]}\n")
            if week in self.pay_all_list:
                self.in_file.write(f"{week} PAY ALL\n")
        self.in_file.close()

    def buy(self, amount, time, duration):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
            "duration": duration,
        })

    def buy_all(self, time, duration):
        if time not in self.buy_all_list:
            self.buy_all_list[time] = []
        self.buy_all_list[time] = duration
    
    def pay(self, amount, time):
        if time not in self.pay_list:
            self.pay_list[time] = []
        self.pay_list[time].append(apply_inflation(amount, time, self.inflation_rate))

    def pay_all(self, time):
        if time not in self.pay_all_list:
            self.pay_all_list[time] = []
        self.pay_all_list[time] = time


class CarLoan:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/car_loan.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.buy_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} START {transaction['amount']} " \
                                        f"{transaction['balloon_payment']} " \
                                        f"{transaction['duration']}\n")
        self.in_file.close()

    def buy(self, amount, balloon_payment, time, duration):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
            "balloon_payment": apply_inflation(balloon_payment, time, self.inflation_rate),
            "duration": duration,
        })


class Hecs:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/hecs.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.pay_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.pay_list:
                for transaction in self.pay_list[week]:
                    self.in_file.write(f"{week} PAY {transaction['amount']}\n")
        self.in_file.close()

    def pay(self, amount, time):
        if time not in self.pay_list:
            self.pay_list[time] = []
        self.pay_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
        })


class Shares:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/shares.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.buy_list = {}
        self.buy_all_list = {}
        self.sell_list = {}
        self.sell_all_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} BUY {transaction['amount']}\n")
            if week in self.sell_list:
                for transaction in self.sell_list[week]:
                    self.in_file.write(f"{week} SELL {transaction['amount']}\n")
            if week in self.buy_all_list:
                self.in_file.write(f"{week} BUY ALL\n")
            if week in self.sell_all_list:
                self.in_file.write(f"{week} SELL ALL\n")
        self.in_file.close()

    def buy(self, amount, time):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
        })

    def buy_all(self, time):
        if time not in self.buy_all_list:
            self.buy_all_list[time] = []
        self.buy_all_list[time] = time

    def sell(self, amount, time):
        if time not in self.sell_list:
            self.sell_list[time] = []
        self.sell_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
        })

    def sell_all(self, time):
        if time not in self.sell_all_list:
            self.sell_all_list[time] = []
        self.sell_all_list[time] = time


class Superannuation:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/super.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.sg_rate = 11
        self.buy_cc_list = {}
        self.buy_all_cc_list = {}
        self.buy_ncc_list = {}
        self.buy_all_ncc_list = {}
        self.sell_list = {}
        self.sell_all_list = {}

    def write(self, income_file_gen):
        for week in range(self.num_weeks):
            if week in income_file_gen.income_list:
                for transaction in income_file_gen.income_list[week]:
                    self.in_file.write(f"{week} BUY SG {self.sg_rate / 100 * transaction['amount']}\n")
            if week in self.buy_cc_list:
                for transaction in self.buy_cc_list[week]:
                    self.in_file.write(f"{week} BUY CC {transaction['amount']}\n")
            if week in self.buy_ncc_list:
                for transaction in self.buy_ncc_list[week]:
                    self.in_file.write(f"{week} BUY NCC {transaction['amount']}\n")
            if week in self.buy_all_cc_list:
                self.in_file.write(f"{week} BUY CC ALL\n")
            if week in self.buy_all_ncc_list:
                self.in_file.write(f"{week} BUY NCC ALL\n")
            if week in self.sell_list:
                for transaction in self.sell_list[week]:
                    self.in_file.write(f"{week} SELL {transaction['amount']}\n")
            if week in self.sell_all_list:
                self.in_file.write(f"{week} SELL ALL\n")
        self.in_file.close()

    def buy(self, amount, variant, time):
        if variant == "CC":
            if time not in self.buy_cc_list:
                self.buy_cc_list[time] = []
            self.buy_cc_list[time].append({
                "amount": apply_inflation(amount, time, self.inflation_rate),
            })
        elif variant == "NCC":
            if time not in self.buy_ncc_list:
                self.buy_ncc_list[time] = []
            self.buy_ncc_list[time].append({
                "amount": apply_inflation(amount, time, self.inflation_rate),
            })

    def buy_all(self, variant, time):
        if variant == "CC":
            if time not in self.buy_all_cc_list:
                self.buy_all_cc_list[time] = []
            self.buy_all_cc_list[time] = time
        elif variant == "NCC":
            if time not in self.buy_all_ncc_list:
                self.buy_all_ncc_list[time] = []
            self.buy_all_ncc_list[time] = time

    def sell(self, amount, time):
        if time not in self.sell_list:
            self.sell_list[time] = []
        self.sell_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
        })

    def sell_all(self, time):
        if time not in self.sell_all_list:
            self.sell_all_list[time] = []
        self.sell_all_list[time] = time


class Income:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/income.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.income_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.income_list:
                for transaction in self.income_list[week]:
                    self.in_file.write(f"{week} {transaction['amount']}\n")
        self.in_file.close()

    def add(self, amount, time):
        if time not in self.income_list:
            self.income_list[time] = []
        self.income_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
        })


class Misc:
    def __init__(self, num_weeks, annual_inflation_rate):
        self.in_file = open("input_files/misc.txt", "w")
        self.num_weeks = num_weeks
        self.inflation_rate = annual_inflation_rate
        self.buy_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} {transaction['amount']}\n")
        self.in_file.close()

    def add(self, amount, time):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": apply_inflation(amount, time, self.inflation_rate),
        })


if __name__ == "__main__":
    params = {}
    params["inflation_rate"] = 3
    params["home_appreciation_rate"] = 7
    params["home_loan_interest_rate"] = 6
    params["car_loan_interest_rate"] = 12
    params["hecs_indexation_rate"] = 4
    params["shares_ror"] = 10
    params["super_ror"] = 10

    write_params_file(params)

    num_weeks = 35 * 52 + 2

    initial_tax_brackets = [18200, 45000, 135000, 190000]
    write_tax_brackets_file(initial_tax_brackets, num_weeks, params["inflation_rate"])

    income_file_gen = Income(num_weeks, params["inflation_rate"])
    misc_file_gen = Misc(num_weeks, params["inflation_rate"])
    home_file_gen = Home(num_weeks, params["inflation_rate"])
    home_loan_file_gen = HomeLoan(num_weeks, params["inflation_rate"])
    car_loan_file_gen = CarLoan(num_weeks, params["inflation_rate"])
    shares_file_gen = Shares(num_weeks, params["inflation_rate"])
    superannuation_file_gen = Superannuation(num_weeks, params["inflation_rate"])
    hecs_file_gen = Hecs(num_weeks, params["inflation_rate"])

    for week in range(num_weeks):
        income_file_gen.add(1442, week)

    misc_file_gen.add(-140000, 0)
    shares_file_gen.buy(140000, 0)

    #misc_file_gen.add(-8000, 0)

    for week in range(1, 3 * 52):
        if week in range(1, 1 + 10):
            superannuation_file_gen.buy_all("CC", week)
        elif week in range(1 * 52, 1 * 52 + 10):
            superannuation_file_gen.buy_all("CC", week)
        elif week in range(2 * 52, 2 * 52 + 10):
            superannuation_file_gen.buy_all("CC", week)
        else:
            shares_file_gen.buy_all(week)

    superannuation_file_gen.sell_all(3 * 52)
    #NOTE:Dad said $100k towards first home, have only tried simulating with $200k thus far
    #misc_file_gen.add(-200000, 3 * 52)
    misc_file_gen.add(-100000, 3 * 52)
    home_file_gen.buy(500000, 3 * 52)

    # Note that Options 1,2,3 assume a world where I can contribute
    # $30k into super per year.
    # A better comparison might be how to best allocate a fixed amount of money,
    # holding everything else constant, if I have not maxed out my yearly super contribution.
    # What I need to do is figure out the priorities of where to invest my money.

    # Option 1: 17592137 7866836
    #home_loan_file_gen.buy(400000, 3 * 52, 30)
    #shares_file_gen.buy_all(3 * 52 + 1)
    #for week in range(3 * 52 + 2, num_weeks - 4):
        #if week % 52 >= 2 and week % 52 < 22:
            #superannuation_file_gen.buy_all("CC", week)
        #else:
            #shares_file_gen.buy_all(week)
    #car_loan_file_gen.buy(30000, 0, 10 * 52, 5)
    #shares_file_gen.sell_all(num_weeks - 4)

    # Option 2: 16696309 8431254
    #home_loan_file_gen.buy(300000, 3 * 52, 30)
    #shares_file_gen.buy_all(3 * 52 + 1)
    #for week in range(3 * 52 + 2, num_weeks - 4):
        #if week % 52 >= 2 and week % 52 < 22:
            #superannuation_file_gen.buy_all("CC", week)
        #else:
            #shares_file_gen.buy_all(week)
    #car_loan_file_gen.buy(30000, 0, 10 * 52, 5)
    #shares_file_gen.sell_all(num_weeks - 4)

    # Option 3: 17468912 8038111
    #home_loan_file_gen.buy(400000, 3 * 52, 30)
    #shares_file_gen.buy_all(3 * 52 + 1)
    #for week in range(3 * 52 + 2, num_weeks - 4):
        #if week % 52 >= 2 and week % 52 < 22:
            #superannuation_file_gen.buy_all("CC", week)
        #elif week == 10 * 52:
            #shares_file_gen.sell(30000, 10 * 52)
            #misc_file_gen.add(30000, 10 * 52)
        #else:
            #shares_file_gen.buy_all(week)
    #shares_file_gen.sell_all(num_weeks - 4)

    # Option 11:
    home_loan_file_gen.buy(350000, 3 * 52, 30)
    shares_file_gen.buy_all(3 * 52 + 1)

    # Super 350000: 10679919 + 4480138 = 15160057
    # Super 400000: 11115493 + 4205141 = 15320634
    # Home loan 400000: 11116844 + 4184006 = 15300850
    # Choose one of the lines below
    superannuation_file_gen.buy_all("CC", 3 * 52 + 2)
    #home_loan_file_gen.pay_all(3 * 52 + 2)
    #shares_file_gen.buy_all(3 * 52 + 2)

    for week in range(3 * 52 + 3, num_weeks - 4):
        if week % 52 >= 3 and week % 52 < 23:
            misc_file_gen.add(500, week)
            superannuation_file_gen.buy_all("CC", week)
        elif week == 10 * 52:
            shares_file_gen.sell(30000, 10 * 52)
            misc_file_gen.add(30000, 10 * 52)
        else:
            misc_file_gen.add(500, week)
            shares_file_gen.buy_all(week)
    shares_file_gen.sell_all(num_weeks - 4)








    # 500 796677
    #misc_file_gen.add(30000, 60)
    #for week in range(60, 60 + 5 * 52):
        #shares_file_gen.buy_all(week)
    #shares_file_gen.sell_all(60 + 5 * 52)

    # 500 797560 Car Loan Interest Rate 8
    # 500 793525 Car Loan Interest Rate 12
    # 500 792029 Car Loan Interest Rate 12 Balloon Payment 10000 car_loan_file_gen.buy(20000, 10000, 60, 5)
    #for week in range(60, 60 + 5 * 52):
        #shares_file_gen.buy_all(week)
    #shares_file_gen.sell_all(60 + 5 * 52)

    income_file_gen.write()
    misc_file_gen.write()
    home_file_gen.write()
    home_loan_file_gen.write()
    car_loan_file_gen.write()
    shares_file_gen.write()
    superannuation_file_gen.write(income_file_gen)
    hecs_file_gen.write()


    # Consider making maximum CC contributions over a few years from your shares unless
    # that is a CGT event? Maybe who cares if it is a CGT event since you would need to
    # have one eventually to do anything with those shares, and maybe better to have it
    # earlier than later so you can get it into the good tax environment of super?

    # So it looks like my highest priority should be putting money into super.
    # It may make sense to reduce my home loan to the point where I can contribute the
    # maximum amount in super each year without having to spend my shares. Because that
    # is less risky. Once you have put enough into super to retire on, you can start
    # investing the rest in shares. And you have a low weekly mortgage repayment still,
    # and there is no risk with this strategy. It is also better from a lifestyle
    # perspective, because with lower mortgage repayments, I will have the cash in hand
    # which I can choose to either spend or invest.
