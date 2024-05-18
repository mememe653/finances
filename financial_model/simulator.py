# TODO: Do starting balance consistency checking between simulations so you are comparing like for like.
# TODO: Read tax brackets from file; they should increase with inflation.
# TODO: Add tax support for starting the simulation in the middle of a financial year.

import tax_collector as tax
import super # This could be an error because super is a keyword?
import shares

class Simulator:
    def __init__(self):
        self.starting_balance = 100
        self.output_cash_files = ["shares.txt"]
        self.output_tax_file = "invoice.txt"
        self.final_output_file = "output_files/cash.txt"
        self.out_cash = []

    def simulate(self, num_weeks):
        # Generate input files here

        assets = [shares.Shares("input_files/shares.txt")]
        for asset in assets:
            asset.simulate(num_weeks)

        tax_collectors = [tax.IncomeTaxCollector()]
        tax.TaxCollector(tax_collectors).apply_tax()

        self.parse_receipts()

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

        tax_file = open(f"output_files/tax/{self.output_tax_file}", "r")
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
    Simulator().simulate(104)
