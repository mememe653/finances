# I reckon you don't need to split pre-tax and post-tax simulations.
# Instead, just generate distinct output files for pre-tax receipts and post-tax receipts.

# I think there is technically an error in the way I calculate tax on entry into super.
# Basically, it is calculated as 15% of after-tax amount rather than 15% of before-tax amount.
# I suspect the way I am taxing super is wrong, but have not looked yet.
# Maybe I could apply pre-tax into super in simulator.py file instead?
# Maybe it is close enough to being right that it doesn't really matter.

class TaxCollector:
    def __init__(self, tax_collectors):
        self.tax_collectors = tax_collectors

    def apply_tax(self):
        for tax_collector in self.tax_collectors:
            #tax_collector.parse_receipts()
            tax_collector.apply_tax()


class IncomeTaxCollector:
    def __init__(self):
        self.tax_brackets = [18200, 45000, 120000, 180000]
        self.mtr = [19, 32.5, 37, 45]
        self.tax_collectors = [self, SharesTaxCollector(), SuperTaxCollector()]
        self.taxable_income = []
        for tax_collector in self.tax_collectors:
            for year, taxable_income in enumerate(tax_collector.get_taxable_income()):
                try:
                    self.taxable_income[year] += taxable_income
                except:
                    self.taxable_income.append(taxable_income)
        for year, amount in enumerate(SuperTaxCollector().get_cc_contribs()):
            self.taxable_income[year] -= amount

    def get_taxable_income(self):
        income_file = open("input_files/income.txt", "r")
        total_taxable_income = []
        input_line = income_file.readline().split()
        while len(input_line) > 0:
            week = int(input_line[0])
            year = week // 52
            if year == len(total_taxable_income):
                total_taxable_income.append(0)
            if len(input_line) == 2:
                _, taxable_income = input_line
                taxable_income = float(taxable_income)
                total_taxable_income[year] += taxable_income
            input_line = income_file.readline().split()
        income_file.close()
        return total_taxable_income

    def apply_tax(self):
        tax_file = open("output_files/tax/invoice.txt", "w")
        super_cc_contribs = SuperTaxCollector().get_cc_contribs()
        for year, taxable_income in enumerate(self.taxable_income):
            tax = 0
            idx = 0
            while taxable_income > self.tax_brackets[idx]:
                if idx >= len(self.tax_brackets) - 1:
                    break
                tax += self.mtr[idx] / 100 * (min(taxable_income, self.tax_brackets[idx + 1]) \
                        - self.tax_brackets[idx])
                idx += 1
            if taxable_income > self.tax_brackets[-1]:
                tax += self.mtr[-1] / 100 * (taxable_income - self.tax_brackets[-1])
            tax += 0.15 * super_cc_contribs[year]
            tax_file.write(f"{year} {tax}\n")
        tax_file.close()

    def parse_receipts(self, tax_receipts):
        pass


class SharesTaxCollector:
    def __init__(self):
        pass

    def get_taxable_income(self):
        tax_receipt = open("output_files/tax/shares.txt", "r")
        total_taxable_income = []
        input_line = tax_receipt.readline().split()
        while len(input_line) > 0:
            week = int(input_line[0])
            year = week // 52
            if year == len(total_taxable_income):
                total_taxable_income.append(0)
            if len(input_line) == 2:
                _, taxable_income = input_line
                taxable_income = float(taxable_income)
                total_taxable_income[year] += taxable_income
            input_line = tax_receipt.readline().split()
        tax_receipt.close()
        return total_taxable_income

    def parse_receipts(self):
        pass


class SuperTaxCollector:
    def __init__(self):
        self.taxed_amount = []
        self.untaxed_amount = []
        self.tax_brackets = [18200, 45000, 120000, 180000]
        self.mtr = [19, 32.5, 37, 45]
        self.parse_receipt()

    def get_taxable_income(self):
        input_file = open("input_files/super.txt", "r")
        ncc_amount = []
        input_line = input_file.readline().split()
        while len(input_line) > 0:
            week = int(input_line[0])
            year = week // 52
            if year == len(ncc_amount):
                ncc_amount.append(0)
            if len(input_line) == 4:
                _, command, variant, amount = input_line
                amount = float(amount)
                if variant == "NCC":
                    ncc_amount[year] += amount
            input_line = input_file.readline().split()
        input_file.close()
        return ncc_amount

    def get_cc_contribs(self):
        input_file = open("input_files/super.txt", "r")
        cc_amount = []
        input_line = input_file.readline().split()
        while len(input_line) > 0:
            week = int(input_line[0])
            year = week // 52
            if year == len(cc_amount):
                cc_amount.append(0)
            if len(input_line) == 4:
                _, command, variant, amount = input_line
                amount = float(amount)
                if variant == "CC":
                    cc_amount[year] += amount
            input_line = input_file.readline().split()
        input_file.close()
        return cc_amount

    def parse_receipt(self):
        tax_receipt = open("output_files/tax/super.txt", "r")
        input_line = tax_receipt.readline().split()
        while len(input_line) > 0:
            week = int(input_line[0])
            year = week // 52
            if year >= len(self.taxed_amount):
                self.taxed_amount.append(0)
                self.untaxed_amount.append(0)
            if len(input_line) == 3:
                _, taxed_amount, untaxed_amount = input_line
                taxed_amount = float(taxed_amount)
                untaxed_amount = float(untaxed_amount)
                self.taxed_amount[-1] += taxed_amount
                self.untaxed_amount[-1] += untaxed_amount
            input_line = tax_receipt.readline().split()
        tax_receipt.close()

    def apply_tax(self):
        tax_file = open("output_files/tax/super_invoice.txt", "w")
        total_taxable_income = IncomeTaxCollector().taxable_income
        #total_taxable_income = IncomeTaxCollector().get_taxable_income()
        for year, taxable_income in enumerate(total_taxable_income):
            tax = 0
            idx = 0
            self.taxed_amount[year] += 0.15 * self.untaxed_amount[year]
            tax += 0.15 * self.untaxed_amount[year]
            while idx < len(self.tax_brackets) \
            and taxable_income > self.tax_brackets[idx]:
                idx += 1
            while idx < len(self.tax_brackets) \
            and taxable_income + self.taxed_amount[year] > self.tax_brackets[idx-1]:
                tax += (self.mtr[idx-1] - 30) / 100 * (min(taxable_income + \
                        self.taxed_amount[year], self.tax_brackets[idx]) \
                        - max(taxable_income, self.tax_brackets[idx-1]))
                idx += 1
            if taxable_income + self.taxed_amount[year] > self.tax_brackets[-1]:
                tax += (self.mtr[-1] - 30) / 100 * (taxable_income + \
                        self.taxed_amount[year] - max(taxable_income, self.tax_brackets[-1]))
            tax_file.write(f"{year} {tax}\n")
        tax_file.close()


if __name__ == "__main__":
    tax_collector = SuperTaxCollector()
    tax_collector.apply_tax()
