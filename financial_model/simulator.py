# TODO: Do starting balance consistency checking between simulations so you are comparing like for like.
# TODO: Read tax brackets from file; they should increase with inflation.

import tax_collector as tax
import income
import misc
import superannuation
import shares
import home
import home_loan
import car_loan
import hecs

import math

def create_inflation_adjuster(annual_inflation_rate):
    def apply_inflation(amount, time):
        weekly_inflation_rate = (math.exp(math.log(1 + annual_inflation_rate / 100) / 52) - 1) \
                                    * 100
        return amount * (1 + weekly_inflation_rate / 100) ** time
    return apply_inflation

def reset_input_files(num_weeks, inputs):
    if "SHARES" in inputs:
        in_file_gen = shares.InputFileGenerator(num_weeks)
        amount = 1
        week = 0
        in_file_gen.buy(amount, week)
        in_file_gen.write()
    if "SUPER" in inputs:
        in_file_gen = superannuation.InputFileGenerator(num_weeks)
        amount = 1
        week = 0
        in_file_gen.buy(amount, "CC", week)
        in_file_gen.write()
    if "HOME" in inputs:
        in_file_gen = home.InputFileGenerator(num_weeks)
        amount = 1
        week = 0
        in_file_gen.buy(amount, week)
        in_file_gen.write()
    if "HOME_LOAN" in inputs:
        in_file_gen = home_loan.InputFileGenerator(num_weeks)
        amount = 1
        start_week = 0
        duration_years = 1
        in_file_gen.buy(amount, start_week, duration_years)
        in_file_gen.write()
    if "CAR_LOAN" in inputs:
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        amount = 1
        balloon_payment = 0
        start_week = 0
        duration_years = 1
        in_file_gen.buy(amount, balloon_payment, start_week, duration_years)
        in_file_gen.write()
    if "HECS" in inputs:
        in_file_gen = hecs.InputFileGenerator(num_weeks)
        amount = 1
        start_week = 0
        in_file_gen.buy(amount, start_week)
        in_file_gen.write()


class Simulator:
    def __init__(self):
        self.output_cash_files = ["shares.txt",
                                    "super.txt",
                                    "home.txt",
                                    "home_loan.txt",
                                    "car_loan.txt",
                                    "hecs.txt"]
        self.output_tax_files = ["invoice.txt",
                                    "super_invoice.txt"]
        self.final_output_file = "output_files/cash.txt"
        sim_params = self.get_params()
        self.cash_params, self.shares_params, self.super_params, self.home_params, \
                self.home_loan_params, self.car_loan_params, self.hecs_params \
                = sim_params
        #TODO:Adjust for inflation when generating input files
        #TODO:Add support for inflation in tax brackets
        #TODO:Re-initialise all input files when generating them instead of commenting code out
        #     Could re-write them with initial values at end of generate_input_files()
        #TODO:Create an experiments Python file from which I can import my experiments so I don't delete the code
        self.out_cash = [self.cash_params["STARTING_BALANCE"]]
        #TODO:Add annual inflation rate parameter to input_files/params.txt
        self.apply_inflation = create_inflation_adjuster(3)

    def simulate(self, num_weeks):
        self.generate_input_files(num_weeks)

        assets = [shares.Shares("input_files/shares.txt", self.shares_params),
                    superannuation.Super("input_files/super.txt", self.super_params),
                    home.Home("input_files/home.txt", self.home_params),
                    home_loan.HomeLoan("input_files/home_loan.txt", self.home_loan_params),
                    car_loan.CarLoan("input_files/car_loan.txt", self.car_loan_params),
                    hecs.Hecs("input_files/hecs.txt", self.hecs_params)]
        for asset in assets:
            asset.simulate(num_weeks)

        tax_collectors = [tax.IncomeTaxCollector(),
                            tax.SuperTaxCollector()]
        tax.TaxCollector(tax_collectors).apply_tax()

        self.parse_receipts()

        self.print_final_report(num_weeks)

    def get_params(self):
        params_file = open("input_files/params.txt", "r")
        cash_params = {}
        shares_params = {}
        super_params = {}
        home_params = {}
        home_loan_params = {}
        car_loan_params = {}
        hecs_params = {}
        input_line = params_file.readline()
        while len(input_line) > 0:
            input_line = input_line.split()
            if len(input_line) == 3:
                asset, param_name, param_value = input_line
                if asset == "CASH":
                    cash_params[param_name] = int(param_value)
                if asset == "SHARES":
                    shares_params[param_name] = int(param_value)
                if asset == "SUPER":
                    super_params[param_name] = int(param_value)
                if asset == "HOME":
                    home_params[param_name] = int(param_value)
                if asset == "HOME_LOAN":
                    home_loan_params[param_name] = int(param_value)
                if asset == "CAR_LOAN":
                    car_loan_params[param_name] = int(param_value)
                if asset == "HECS":
                    hecs_params[param_name] = int(param_value)
            input_line = params_file.readline()
        params_file.close()
        return cash_params, shares_params, super_params, home_params, home_loan_params, \
                car_loan_params, hecs_params

    def generate_tax_brackets(self, num_weeks):
        params_file = open("input_files/tax_brackets.txt", "w")
        tax_brackets = [18200, 45000, 120000, 180000]
        mtr = [19, 32.5, 37, 45]
        for year in range(num_weeks // 52):
            params_file.write(f"{year} RATES ")
            for rate in mtr:
                params_file.write(f"{rate} ")
            params_file.write("\n")
            params_file.write(f"{year} BRACKETS ")
            for bracket in tax_brackets:
                #params_file.write(f"{bracket} ")
                params_file.write(f"{self.apply_inflation(bracket, 52 * year)} ")
            params_file.write("\n")
            params_file.write("\n")
        params_file.close()
    
    def generate_hecs_brackets(self, num_weeks):
        params_file = open("input_files/hecs_brackets.txt", "w")
        repayment_rates = [0, 1, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, \
                            8, 8.5, 9, 9.5, 10]
        income_brackets = [51550, 59518, 63089, 66875, 70888, 75140, \
                            79649, 84429, 89494, 94865, 100557, 106590, \
                            112985, 119764, 126950, 134568, 142642, 151200]
        for week in range(num_weeks):
            params_file.write(f"{week} RATES ")
            for rate in repayment_rates:
                params_file.write(f"{rate} ")
            params_file.write("\n")
            params_file.write(f"{week} BRACKETS ")
            for bracket in income_brackets:
                #params_file.write(f"{bracket} ")
                params_file.write(f"{self.apply_inflation(bracket, week)} ")
            params_file.write("\n")
            params_file.write("\n")
        params_file.close()

    def comprehensive_experiment(self, num_weeks):
        misc_file_gen = misc.InputFileGenerator(num_weeks)

        # Income
        income_file_gen = income.InputFileGenerator(num_weeks)
        weekly_income = int(75000 / 52)
        for week in range(num_weeks):
            income_file_gen.add(week, self.apply_inflation(weekly_income, week))
        home_loan_start_year = 2
        weekly_expenses = 500
        for week in range(home_loan_start_year * 52, num_weeks):
            misc_file_gen.add(week, self.apply_inflation(weekly_expenses, week))

        # Super
        super_file_gen = superannuation.InputFileGenerator(num_weeks)
        employer_super_contribution = 0.11 * weekly_income
        for week in range(num_weeks):
            super_file_gen.buy(self.apply_inflation(employer_super_contribution, week), "CC", week)
        for week in range(15):
            super_file_gen.buy(self.apply_inflation(employer_super_contribution, week) \
                                + 1000, "CC", week)
        for week in range(1 * 52, 1 * 52 + 15):
            super_file_gen.buy(self.apply_inflation(employer_super_contribution, week) \
                                + 1000, "CC", week)
        #for week in range(15):
            #super_file_gen.buy(1000, "CC", week)
        #for week in range(1 * 52, 1 * 52 + 15):
            #super_file_gen.buy(1000, "CC", week)
        #fhss_yearly_cap = 15000
        #super_file_gen.buy(fhss_yearly_cap, "CC", 0)
        #super_file_gen.buy(fhss_yearly_cap, "CC", 1 * 52)
        fhss_yearly_cap = 15000
        fhss_total_earnings = 3992 # This number is correct, at least until I change parameters
        super_file_gen.sell(2 * fhss_yearly_cap + fhss_total_earnings, home_loan_start_year * 52)
        #super_cc_yearly_cap = 30000
        #num_contribs = 8
        #for year in range(home_loan_start_year + 1, home_loan_start_year + 1 + num_contribs):
            #week = year * 52
            #super_file_gen.buy(self.apply_inflation(super_cc_yearly_cap, week), "CC", week)

        # Home
        home_file_gen = home.InputFileGenerator(num_weeks)
        home_purchase_price = 500000
        home_file_gen.buy(home_purchase_price, home_loan_start_year * 52)
        misc_file_gen.add(home_loan_start_year * 52, -200000)

        # Home Loan
        home_loan_file_gen = home_loan.InputFileGenerator(num_weeks)
        loan_amount = 0.8 * home_purchase_price
        loan_duration_years = 30
        home_loan_file_gen.buy(loan_amount, home_loan_start_year * 52, loan_duration_years)

        # Car Loan
        car_loan_file_gen = car_loan.InputFileGenerator(num_weeks)
        balloon_payment = 0
        start_week = 10 * 52
        loan_duration_years = 5
        loan_amount = self.apply_inflation(25000, start_week)
        car_loan_file_gen.buy(loan_amount, balloon_payment, start_week, loan_duration_years)

        misc_file_gen.write()
        income_file_gen.write()
        super_file_gen.write()
        home_file_gen.write()
        home_loan_file_gen.write()
        car_loan_file_gen.write()

        #reset_inputs = ["SHARES",
                        #"CAR_LOAN"]
        #reset_input_files(num_weeks, reset_inputs)

    def generate_input_files(self, num_weeks):
        self.comprehensive_experiment(num_weeks)
        #self.car_loan_experiment1(num_weeks)
        #self.car_loan_experiment2(num_weeks)
        #self.car_loan_experiment3(num_weeks)
        #self.car_loan_experiment4(num_weeks)

        # Income
        #in_file_gen = income.InputFileGenerator(num_weeks)
        #weekly_income = int(75000 / 52)
        #for week in range(num_weeks):
            ##in_file_gen.add(week, weekly_income)
            #in_file_gen.add(week, self.inflation_adjuster.apply_inflation(weekly_income, week))
        #misc_file_gen.add(0, self.cash_params["STARTING_BALANCE"])
        #in_file_gen.write()

        ##amount = 1
        ##week = 0
        ##misc_file_gen.add(week, amount)

        # Shares
        #in_file_gen = shares.InputFileGenerator(num_weeks)
        ##amount = 1
        ##week = 0
        ##in_file_gen.buy(amount, week)
        #total_amount = 0
        #for week in range(5 * 52):
            #amount = self.inflation_adjuster.apply_inflation(weekly_income, week)
            #in_file_gen.buy(amount, week)
            #total_amount += amount
        #in_file_gen.sell(total_amount, 5 * 52)
        ##total_amount = 0
        ##for week in range(15, 2 * 52):
            ##in_file_gen.buy(1000, week)
            ##total_amount += 1000
        ##in_file_gen.sell(135000 + total_amount, 2 * 52)
        #in_file_gen.write()

        # Super
        #in_file_gen = superannuation.InputFileGenerator(num_weeks)
        ##super_amount = 0.11 * weekly_income
        ##variant = "CC"
        ##week = 0
        ##for week in range(num_weeks):
            ##in_file_gen.buy(super_amount, variant, week)
            ##misc_file_gen.add(week, -0.15 * super_amount)
        ##for week in range(15):
            ##in_file_gen.buy(1000, "CC", week)
        ##in_file_gen.sell(15000 + 2700, 2 * 52)
        #in_file_gen.buy(1, "CC", 0)
        #in_file_gen.write()

        # Home
        #in_file_gen = home.InputFileGenerator(num_weeks)
        ##amount = 500000
        ##week = 2 * 52
        #amount = 1
        #week = 0
        #in_file_gen.buy(amount, week)
        ##in_file_gen.sell(3 * 52)
        #in_file_gen.write()

        # Home loan
        #in_file_gen = home_loan.InputFileGenerator(num_weeks)
        ##amount = 300000
        ##start_week = 2 * 52
        ##duration_years = 30
        #amount = 1
        #start_week = 0
        #duration_years = 1
        #in_file_gen.buy(amount, start_week, duration_years)
        #in_file_gen.write()

        # Car loan
        #in_file_gen = car_loan.InputFileGenerator(num_weeks)
        #balloon_payment = 0
        #start_week = 17
        #duration_years = 5
        #amount = 25000
        ##amount = self.inflation_adjuster.apply_inflation(amount, start_week)
        ##amount = 1
        ##balloon_payment = 0
        ##start_week = 0
        ##duration_years = 1
        #in_file_gen.buy(amount, balloon_payment, start_week, duration_years)
        #in_file_gen.write()

        # HECS
        #in_file_gen = hecs.InputFileGenerator(num_weeks)
        ##amount = 25000
        ##start_week = 0
        #amount = 1
        #start_week = 0
        #in_file_gen.buy(amount, start_week)
        ##in_file_gen.pay(10000, 52)
        #in_file_gen.write()

        #misc_file_gen.write()

        # HECS brackets
        self.generate_hecs_brackets(num_weeks)

        # Tax brackets
        self.generate_tax_brackets(num_weeks)

    def parse_receipts(self):
        income_file = open("input_files/income.txt", "r")
        line = income_file.readline().split()
        while len(line) > 0:
            week = int(line[0])
            if len(line) == 2:
                amount = float(line[1])
            else:
                amount = 0
            if week < len(self.out_cash):
                self.out_cash[week] += amount
            else:
                self.out_cash.append(amount)
            line = income_file.readline().split()
        income_file.close()

        misc_file = open("input_files/misc.txt", "r")
        line = misc_file.readline().split()
        while len(line) > 0:
            week = int(line[0])
            if len(line) == 2:
                amount = float(line[1])
            else:
                amount = 0
            if week < len(self.out_cash):
                self.out_cash[week] += amount
            else:
                self.out_cash.append(amount)
            line = misc_file.readline().split()
        misc_file.close()

        for out_cash_file in self.output_cash_files:
            f = open(f"output_files/cash/{out_cash_file}", "r")
            line = f.readline().split()
            while len(line) > 0:
                week = int(line[0])
                if len(line) == 2:
                    amount = float(line[1])
                else:
                    amount = 0
                if week < len(self.out_cash):
                    self.out_cash[week] += amount
                else:
                    self.out_cash.append(amount)
                line = f.readline().split()
            f.close()

        for output_tax_file in self.output_tax_files:
            tax_file = open(f"output_files/tax/{output_tax_file}", "r")
            line = tax_file.readline().split()
            while len(line) > 0:
                year = int(line[0])
                week = (year + 1) * 52 - 1
                try:
                    amount = float(line[1])
                except:
                    amount = 0
                self.out_cash[week] -= amount
                line = tax_file.readline().split()
            tax_file.close()

        for week in range(len(self.out_cash)):
            if week != 0:
                self.out_cash[week] += self.out_cash[week - 1]

        f = open(self.final_output_file, "w")
        for week, amount in enumerate(self.out_cash):
            f.write(f"{week} {amount}\n")
        f.close()

        self.assert_positive_balance()

    def assert_positive_balance(self):
        for amount in self.out_cash:
            #print(amount)
            assert amount >= 0
    
    def car_loan_experiment1(self, num_weeks):
        misc_file_gen = misc.InputFileGenerator(num_weeks)
        misc_file_gen.add(0, -60) # Because HECS
        tax = [15312, 15925, 16562, 17224, 17913]
        tax = [yearly_tax / 52 for yearly_tax in tax]

        # Experiment 1 - Buying car without loan
        # Parameters
        loan_duration_years = 5
        weekly_expenses = 0

        # Income
        in_file_gen = income.InputFileGenerator(num_weeks)
        weekly_income = int(75000 / 52)
        misc_file_gen.add(0, self.cash_params["STARTING_BALANCE"])
        for week in range(num_weeks):
            in_file_gen.add(week, self.apply_inflation(weekly_income, week))
            misc_file_gen.add(week, self.apply_inflation(weekly_expenses, week))
        in_file_gen.write()

        # Shares
        in_file_gen = shares.InputFileGenerator(num_weeks)
        total_amount = 0
        for week in range(loan_duration_years * 52):
            amount = self.apply_inflation(weekly_income - weekly_expenses, week) - tax[week // 52]
            in_file_gen.buy(amount, week)
            total_amount += amount
        in_file_gen.sell(total_amount, loan_duration_years * 52 - 1)
        in_file_gen.write()

        # Car loan
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        balloon_payment = 0
        start_week = 0
        amount = 1
        in_file_gen.buy(amount, balloon_payment, start_week, loan_duration_years)
        in_file_gen.write()
        misc_file_gen.write()

        reset_inputs = ["SUPER",
                        "HOME",
                        "HOME_LOAN",
                        "HECS"]
        reset_input_files(num_weeks, reset_inputs)

    def car_loan_experiment2(self, num_weeks):
        misc_file_gen = misc.InputFileGenerator(num_weeks)
        misc_file_gen.add(0, -60) # Because HECS
        tax = [15312, 15925, 16562, 17224, 17913]
        tax = [yearly_tax / 52 for yearly_tax in tax]

        # Experiment 2 - Buying car with loan
        # Parameters
        loan_duration_years = 5
        balloon_payment = 0
        weekly_loan_repayment = 123 # Need to set this manually
        weekly_expenses = 0

        # Income
        in_file_gen = income.InputFileGenerator(num_weeks)
        weekly_income = int(75000 / 52)
        for week in range(num_weeks):
            in_file_gen.add(week, self.apply_inflation(weekly_income, week))
            misc_file_gen.add(week, self.apply_inflation(weekly_expenses, week))
        in_file_gen.write()

        # Shares
        in_file_gen = shares.InputFileGenerator(num_weeks)
        total_amount = 0
        amount = self.cash_params["STARTING_BALANCE"]
        #in_file_gen.buy(amount, 0)
        #total_amount += amount
        for week in range(loan_duration_years * 52):
            amount += self.apply_inflation(weekly_income, week) \
                    - self.apply_inflation(weekly_expenses, week) \
                    - weekly_loan_repayment \
                    - tax[week // 52]
            in_file_gen.buy(amount, week)
            total_amount += amount
            amount = 0
        in_file_gen.sell(total_amount, loan_duration_years * 52 - 1)
        in_file_gen.write()

        # Car loan
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        start_week = 0
        amount = self.cash_params["STARTING_BALANCE"]
        in_file_gen.buy(amount, balloon_payment, start_week, loan_duration_years)
        in_file_gen.write()

        misc_file_gen.write()

        reset_inputs = ["SUPER",
                        "HOME",
                        "HOME_LOAN",
                        "HECS"]
        reset_input_files(num_weeks, reset_inputs)

    def car_loan_experiment3(self, num_weeks):
        misc_file_gen = misc.InputFileGenerator(num_weeks)
        misc_file_gen.add(0, -60) # Because HECS
        tax = [15444, 15925, 16562, 17224, 17913, 18629]
        tax = [yearly_tax / 52 for yearly_tax in tax]

        # Experiment 3 - Saving up to buy car without loan
        # Parameters
        car_cost = 25000
        num_shares_for_car = 24926
        loan_duration_years = 5
        weekly_expenses = 0

        # Income
        in_file_gen = income.InputFileGenerator(num_weeks)
        weekly_income = int(75000 / 52)
        for week in range(num_weeks):
            in_file_gen.add(week, self.apply_inflation(weekly_income, week))
            misc_file_gen.add(week, self.apply_inflation(weekly_expenses, week))
        in_file_gen.write()

        # Shares
        in_file_gen = shares.InputFileGenerator(num_weeks)
        bought_car = False
        total_amount = 0
        for week in range(num_weeks):
            amount = self.apply_inflation(weekly_income - weekly_expenses, week) - tax[week // 52]
            in_file_gen.buy(amount, week)
            total_amount += amount
            if total_amount >= num_shares_for_car and not bought_car:
                print(self.apply_inflation(car_cost, week))
                in_file_gen.sell(num_shares_for_car, week)
                misc_file_gen.add(week, self.apply_inflation(car_cost, week))
                bought_car = True
        total_amount -= num_shares_for_car
        in_file_gen.sell(total_amount, num_weeks - 1)
        in_file_gen.write()

        # Car loan
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        balloon_payment = 0
        start_week = 0
        amount = 1
        in_file_gen.buy(amount, balloon_payment, start_week, loan_duration_years)
        in_file_gen.write()

        misc_file_gen.write()

        reset_inputs = ["SUPER",
                        "HOME",
                        "HOME_LOAN",
                        "HECS"]
        reset_input_files(num_weeks, reset_inputs)

    def car_loan_experiment4(self, num_weeks):
        misc_file_gen = misc.InputFileGenerator(num_weeks)
        misc_file_gen.add(0, -60) # Because HECS
        tax = [15444, 15925, 16562, 17224, 17913, 18629]
        tax = [yearly_tax / 52 for yearly_tax in tax]

        # Experiment 4 - Buying car with loan then saving afterwards
        # Parameters
        car_cost = 25000
        loan_duration_years = 5
        balloon_payment = 0
        weekly_loan_repayment = 115 # Need to set this manually
        weekly_expenses = 0

        # Income
        in_file_gen = income.InputFileGenerator(num_weeks)
        weekly_income = int(75000 / 52)
        for week in range(num_weeks):
            in_file_gen.add(week, self.apply_inflation(weekly_income, week))
            misc_file_gen.add(week, self.apply_inflation(weekly_expenses, week))
        in_file_gen.write()

        # Shares
        in_file_gen = shares.InputFileGenerator(num_weeks)
        total_amount = 0
        amount = self.cash_params["STARTING_BALANCE"]
        for week in range(loan_duration_years * 52):
            amount += self.apply_inflation(weekly_income, week) \
                    - self.apply_inflation(weekly_expenses, week) \
                    - weekly_loan_repayment \
                    - tax[week // 52]
            in_file_gen.buy(amount, week)
            total_amount += amount
            amount = 0
        for week in range(loan_duration_years * 52, num_weeks):
            amount = self.apply_inflation(weekly_income - weekly_expenses, week) - tax[week // 52]
            in_file_gen.buy(amount, week)
            total_amount += amount
        in_file_gen.sell(total_amount, num_weeks - 1)
        in_file_gen.write()

        # Car loan
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        start_week = 0
        amount = car_cost
        in_file_gen.buy(amount, balloon_payment, start_week, loan_duration_years)
        in_file_gen.write()

        misc_file_gen.write()

        reset_inputs = ["SUPER",
                        "HOME",
                        "HOME_LOAN",
                        "HECS"]
        reset_input_files(num_weeks, reset_inputs)

    def print_final_report(self, num_weeks):
        out_cash_file = open("output_files/cash.txt", "r")

        out_shares_file = open("output_files/shares.txt", "r")
        out_super_file = open("output_files/super.txt", "r")
        out_home_file = open("output_files/home.txt", "r")
        out_home_loan_file = open("output_files/home_loan.txt", "r")
        out_car_loan_file = open("output_files/car_loan.txt", "r")
        out_hecs_file = open("output_files/hecs.txt", "r")

        print("---------------")
        print("Debts")
        print("---------------")
        for line in out_home_loan_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"Home Loan = {formatted_amount}")
        for line in out_car_loan_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"Car Loan = {formatted_amount}")
        for line in out_hecs_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"HECS = {formatted_amount}")

        print()
        print("---------------")
        print("Assets")
        print("---------------")
        for line in out_shares_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"Shares = {formatted_amount}")
        for line in out_home_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"Home = {formatted_amount}")

        print()
        print("---------------")
        print("Cash")
        print("---------------")
        for line in out_super_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"Super = {formatted_amount}")
        for line in out_cash_file:
            pass
        week, amount = line.split()
        if int(week) == num_weeks - 1:
            formatted_amount = "${:,.2f}".format(float(amount))
            print(f"Cash = {formatted_amount}")


if __name__ == "__main__":
    num_weeks = 34 * 52
    Simulator().simulate(num_weeks)
