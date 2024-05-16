# TODO: Do starting balance consistency checking between simulations so you are comparing like for like

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
        for out_cash_file in self.output_cash_files:
            f = open(f"output_files/cash/{out_cash_file}", "r")
            line = f.readline().split()
            while len(line) > 0:
                week = int(line[0])
                amount = float(line[1])
                if week < len(self.out_cash):
                    self.out_cash[week] += amount
                else:
                    self.out_cash.extend(amount)
                line = f.readline().split()
            f.close()

        tax_file = open(f"output_files/tax/{self.output_tax_file}", "r")
        line = tax_file.readline().split()
        while len(line) > 0:
            week = int(line[0])
            amount = float(line[1])
            self.out_cash[week] -= amount
        tax_file.close()

        self.assert_positive_balance()
        f = open(self.final_output_file, "w")
        for week, amount in enumerate(self.out_cash):
            f.write(f"{week} {amount}\n")
        f.close()

    def assert_positive_balance(self):
        for amount in self.out_cash:
            assert amount >= 0
