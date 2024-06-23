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

class Parameters:
    def shares():
        return {
                "annual_ror": 10,
                "starting_balance": 135000
            }

    def super():
        return {
                "annual_ror": 10,
                #"starting_balance": 17000
                "starting_balance": 1
            }

    def home():
        return {
                "annual_ror": 8
            }

    def home_loan():
        return {
                "annual_interest_rate": 6
            }

    def car_loan():
        return {
                "annual_interest_rate": 6
            }

    def hecs():
        return {
                "annual_indexation_rate": 4
            }


class InflationAdjuster:
    def __init__(self, annual_inflation_rate):
        self.weekly_inflation_rate = (math.exp(math.log(1 + self.interest_rate / 100) / 52) - 1) \
                                        * 100

    def apply_inflation(self, amount, time):
        return amount * self.weekly_inflation_rate ** time


class Simulator:
    def __init__(self):
        self.starting_balance = 100
        self.output_cash_files = ["shares.txt",
                                    "super.txt",
                                    "home.txt",
                                    "home_loan.txt",
                                    "car_loan.txt",
                                    "hecs.txt"]
        self.output_tax_files = ["invoice.txt",
                                    "super_invoice.txt"]
        self.final_output_file = "output_files/cash.txt"
        #TODO:Adjust for inflation when generating input files
        #TODO:Add support for inflation in tax brackets
        starting_balance = 8000
        self.out_cash = [starting_balance]

    def simulate(self, num_weeks):
        self.generate_input_files(num_weeks)

        assets = [shares.Shares("input_files/shares.txt", Parameters.shares()),
                    superannuation.Super("input_files/super.txt", Parameters.super()),
                    home.Home("input_files/home.txt", Parameters.home()),
                    home_loan.HomeLoan("input_files/home_loan.txt", Parameters.home_loan()),
                    car_loan.CarLoan("input_files/car_loan.txt", Parameters.car_loan()),
                    hecs.Hecs("input_files/hecs.txt", Parameters.hecs())]
        for asset in assets:
            asset.simulate(num_weeks)

        tax_collectors = [tax.IncomeTaxCollector(),
                            tax.SuperTaxCollector()]
        tax.TaxCollector(tax_collectors).apply_tax()

        self.parse_receipts()

        self.print_final_report(num_weeks)

    def generate_input_files(self, num_weeks):
        # Miscellaneous expenses
        misc_file_gen = misc.InputFileGenerator(num_weeks)

        # Income
        in_file_gen = income.InputFileGenerator(num_weeks)
        weekly_income = int(75000 / 52)
        for week in range(num_weeks):
            in_file_gen.add(week, weekly_income)
        in_file_gen.write()

        #amount = 1
        #week = 0
        #misc_file_gen.add(week, amount)

        # Shares
        in_file_gen = shares.InputFileGenerator(num_weeks)
        #amount = 1
        #week = 0
        #in_file_gen.buy(amount, week)
        total_amount = 0
        for week in range(15, 2 * 52):
            in_file_gen.buy(1000, week)
            total_amount += 1000
        in_file_gen.sell(135000 + total_amount, 2 * 52)
        in_file_gen.write()

        # Super
        in_file_gen = superannuation.InputFileGenerator(num_weeks)
        super_amount = 0.11 * weekly_income
        variant = "CC"
        week = 0
        #for week in range(num_weeks):
            #in_file_gen.buy(super_amount, variant, week)
            #misc_file_gen.add(week, -0.15 * super_amount)
        for week in range(15):
            in_file_gen.buy(1000, "CC", week)
        in_file_gen.sell(15000 + 2700, 2 * 52)
        #in_file_gen.buy(1, "CC", 0)
        in_file_gen.write()

        # Home
        in_file_gen = home.InputFileGenerator(num_weeks)
        amount = 500000
        week = 2 * 52
        #amount = 1
        #week = 0
        in_file_gen.buy(amount, week)
        #in_file_gen.sell(3 * 52)
        in_file_gen.write()

        # Home loan
        in_file_gen = home_loan.InputFileGenerator(num_weeks)
        amount = 300000
        start_week = 2 * 52
        duration_years = 30
        #amount = 1
        #start_week = 0
        #duration_years = 1
        in_file_gen.buy(amount, start_week, duration_years)
        in_file_gen.write()

        # Car loan
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        #amount = 30000
        #balloon_payment = 5000
        #start_week = 10 * 52
        #duration_years = 5
        amount = 1
        balloon_payment = 0
        start_week = 0
        duration_years = 1
        in_file_gen.buy(amount, balloon_payment, start_week, duration_years)
        in_file_gen.write()

        # HECS
        in_file_gen = hecs.InputFileGenerator(num_weeks)
        #amount = 25000
        #start_week = 0
        amount = 1
        start_week = 0
        in_file_gen.buy(amount, start_week)
        #in_file_gen.pay(10000, 52)
        in_file_gen.write()

        misc_file_gen.write()

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
    num_weeks = 1040
    Simulator().simulate(num_weeks)
