# I reckon you don't need to split pre-tax and post-tax simulations.
# Instead, just generate distinct output files for pre-tax receipts and post-tax receipts.

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
        self.tax_collectors = [self, SharesTaxCollector()]
        self.taxable_income = []
        for tax_collector in self.tax_collectors:
            for year, taxable_income in enumerate(tax_collector.get_taxable_income()):
                try:
                    self.taxable_income[year] += taxable_income
                except:
                    self.taxable_income.append(taxable_income)

    def get_taxable_income(self):
        income_file = open("input_files/income.txt", "r")
        total_taxable_income = []
        input_line = income_file.readline().split()
        while len(input_line) > 0:
            if len(input_line) == 2:
                week, taxable_income = input_line
                week, taxable_income = int(week), float(taxable_income)
                year = week % 52
                if year >= len(total_taxable_income):
                    total_taxable_income.append(0)
                total_taxable_income[-1] += taxable_income
            input_line = income_file.readline().split()
        return total_taxable_income

    def apply_tax(self):
        tax_file = open("output_files/tax/invoice.txt", "w")
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
            if len(input_line) == 2:
                week, taxable_income = input_line
                week, taxable_income = int(week), float(taxable_income)
                year = week % 52
                if year >= len(total_taxable_income):
                    total_taxable_income.append(0)
                total_taxable_income[-1] += taxable_income
            input_line = tax_receipt.readline().split()
        return total_taxable_income

    def parse_receipts(self):
        pass


class SuperTaxCollector:
    def __init__(self):
        pass

    def apply_tax(self):
        pass

    def parse_receipts(self, tax_receipts):
        pass
