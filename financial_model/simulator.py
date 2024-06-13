# TODO: Do starting balance consistency checking between simulations so you are comparing like for like.
# TODO: Read tax brackets from file; they should increase with inflation.
# TODO: Add tax support for starting the simulation in the middle of a financial year.

import tax_collector as tax
import superannuation
import shares
import home_loan
import car_loan
import hecs

class Parameters:
    def shares():
        return {
                "annual_ror": 10
            }

    def super():
        return {
                "annual_ror": 10
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


class Simulator:
    def __init__(self):
        self.starting_balance = 100
        self.output_cash_files = ["shares.txt",
                                    "super.txt",
                                    "home_loan.txt",
                                    "car_loan.txt",
                                    "hecs.txt"]
        self.output_tax_files = ["invoice.txt",
                                    "super_invoice.txt"]
        self.final_output_file = "output_files/cash.txt"
        self.out_cash = []

    def simulate(self, num_weeks):
        self.generate_input_files(num_weeks)

        assets = [shares.Shares("input_files/shares.txt", Parameters.shares()),
                    superannuation.Super("input_files/super.txt", Parameters.super()),
                    home_loan.HomeLoan("input_files/home_loan.txt", Parameters.home_loan()),
                    car_loan.CarLoan("input_files/car_loan.txt", Parameters.car_loan()),
                    hecs.Hecs("input_files/hecs.txt", Parameters.hecs())]
        for asset in assets:
            asset.simulate(num_weeks)

        tax_collectors = [tax.IncomeTaxCollector(),
                            tax.SuperTaxCollector()]
        tax.TaxCollector(tax_collectors).apply_tax()

        self.parse_receipts()

    def generate_input_files(self, num_weeks):
        # Income
        in_file_gen = income.InputFileGenerator(num_weeks)
        amount = 1000
        for week in range(num_weeks):
            in_file_gen.add(week, amount)
        in_file_gen.write()

        # Shares
        in_file_gen = shares.InputFileGenerator(num_weeks)
        amount = 135000
        week = 0
        in_file_gen.buy(amount, week)
        in_file_gen.write()

        # Super
        in_file_gen = superannuation.InputFileGenerator(num_weeks)
        amount = 15000
        variant = "CC"
        week = 0
        in_file_gen.buy(amount, variant, week)
        in_file_gen.write()

        # Home loan
        in_file_gen = home_loan.InputFileGenerator(num_weeks)
        amount = 300000
        start_week = 2 * 52
        duration_years = 30
        in_file_gen.buy(amount, start_week, duration_years)
        in_file_gen.write()

        # Car loan
        in_file_gen = car_loan.InputFileGenerator(num_weeks)
        amount = 30000
        balloon_payment = 0
        start_week = 10 * 52
        duration_years = 10
        in_file_gen.buy(amount, balloon_payment, start_week, duration_years)
        in_file_gen.write()

        # HECS
        in_file_gen = hecs.InputFileGenerator(num_weeks)
        amount = 25000
        start_week = 0
        in_file_gen.buy(amount, start_week)
        in_file_gen.write()

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
                week = int(line[0])
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

        self.assert_positive_balance()
        f = open(self.final_output_file, "w")
        for week, amount in enumerate(self.out_cash):
            f.write(f"{week} {amount}\n")
        f.close()

    def assert_positive_balance(self):
        for amount in self.out_cash:
            assert amount >= 0


if __name__ == "__main__":
    #Simulator().simulate(104)
