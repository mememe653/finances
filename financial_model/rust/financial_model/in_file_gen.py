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
                self.in_file.write(f"{week} START ALL {self.buy_all_list[week]['duration']}\n")
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
        self.buy_all_list[time].append({
            "duration": duration,
        })
    
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
    params["inflation_rate"] = 4
    params["home_appreciation_rate"] = 8
    params["home_loan_interest_rate"] = 6
    params["car_loan_interest_rate"] = 8
    params["hecs_indexation_rate"] = 4
    params["shares_ror"] = 10
    params["super_ror"] = 10

    write_params_file(params)

    num_weeks = 35 * 52

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

    #for week in range(10):
        #superannuation_file_gen.buy_all("CC", week)
    #superannuation_file_gen.sell(25000, 100)

    for week in range(10):
        shares_file_gen.buy_all(week)
    shares_file_gen.sell_all(100)

    #misc_file_gen.add(-135000, 0)
    #shares_file_gen.buy(135000, 0)
    #shares_file_gen.sell_all(53)



    #misc_file_gen.add(-8000, 0)
    #home_file_gen.buy(500000, 0)
    #home_file_gen.sell(52)
    #home_loan_file_gen.buy(300000, 0, 30)
    #home_loan_file_gen.pay(10000, 52)
    #car_loan_file_gen.buy(20000, 10000, 0, 1)
    #shares_file_gen.buy(100000, 1)
    #shares_file_gen.sell(10000, 53)
    #superannuation_file_gen.buy(10000, "CC", 1)
    #superannuation_file_gen.sell(1000, 53)
    #for week in range(num_weeks):
        #superannuation_file_gen.buy(0.11 * 1442, "SG", week)
        #superannuation_file_gen.buy(1000, "NCC", week)
    #superannuation_file_gen.sell(10000, 26)
    #hecs_file_gen.pay(1000, 1)

    income_file_gen.write()
    misc_file_gen.write()
    home_file_gen.write()
    home_loan_file_gen.write()
    car_loan_file_gen.write()
    shares_file_gen.write()
    superannuation_file_gen.write(income_file_gen)
    hecs_file_gen.write()
