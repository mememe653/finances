# Super contributions are taxed at 15%, I think at the time of putting the money in?
# You get taxed 15% on yearly earnings?
# Zero tax after converting to account-based pension.
# Returns from the stock market are about 10% per annum on average
# Concessional contributions include employer contributions, salary sacrifice, personal direct contributions
# Concessional contribution cap is $27.5k per annum. Compulsory employer contribution forms part of this limit.
# So if your employer contributes $7.5k, you will have $20k remaining in your limit for that year.
# You can also use unused concessional contributions for up to the past 5 years under the carry-forward rule
# provided your total super balance on June 30 of the previous financial year was below $500k.
# NCCs are personal (after-tax) contributions that you don't get a deduction on.
# NCCs do not incur the 15% tax when it is added to your super fund because you would then be paying tax twice.
# The cap on NCCs is $110k per annum.
# You can also use the bring-forward arrangement to put in up to $330k at once.
# NCCs miss out on the immediate tax savings on entry to super. However, they still get a lower tax rate
# on earnings each year, and a zero tax rate after converting to an account-based pension in retirement.
# Super accumulation accounts are taxed at 15% on income, 15% on short-term capital gains, 10% on long-term capital gains.
# With an account-based pension, there is zero tax on investment earnings (both income and capital gains),
# zero tax on the income you receive, and zero tax on lump sum withdrawals.
# Super is taxed at 15% on the way in.

# While you can make NCCs to withdraw under FHSS, you miss out on almost all of the benefits of the scheme.
# Under the FHSS scheme using concessional contributions:
# On the way into super, it will be taxed at 15%.
# On the way out, you pay tax at 30% below your marginal tax rate + medicare levy (on the remaining 85%).
# Compulsory employer contributions do not count as eligible contributions under FHSS, only voluntary contributions count.
# The two ways to add voluntary payments to super are salary sacrifice and personal contribution.
# Under FHSS, you can add voluntary contributions up to $15k per year, and this must be within existing
# contribution caps, up to a combined maximum of $50k over multiple years. This can be through either 
# concessional or non-concessional contributions.
# If you have unused concessional contributions from previous years to be able to contribute over $15k
# voluntarily in one financial year, only the first $15k of contributions in any financial year will count
# towards FHSS. If you have $50k worth of unused concessional contributions from previous years, you
# cannot contribute it all in one year and have it all count towards FHSS.
# You can also withdraw associated earnings under FHSS.
# Definitely re-read the link below on FHSS:
# https://passiveinvestingaustralia.com/first-home-super-saver-scheme/

# Carry-forward contributions are where you can use unused concessional contributions from up to the 5 previous
# years to get more into super and reduce your tax in the current financial year.
# To be eligible to make carry-forward contributions, your total super balance at 30 June of the previous
# financial year must be less than $500k.
# To find out how much unused concessional contributions you have, log into the MyGov ATO site and go to the
# superannuation tab.
# Your concessional cap is allocated as follows:
# Any concessional contribution you make up to the concessional cap will be taken from your current year's
# concessional cap. Above the concessional cap, it will be automatically applied to the oldest unused 
# concessional contributions first. Below the concessional cap, only the excess will be added to your unused
# concessional contributions to be used for up to and including the next 5 future years.

# NCCs are a great way to get more money into super as you get closer to retirement.
# Under the bring-forward rule, people may effectively bring forward from future years, up to an additional
# two years' worth of non-concessional caps. This means you can contribute a greater amount (up to $330k)
# without exceeding your NCC cap. Unlike the carry-forward rule with CCs, any previously unused NCCs are not
# carried forward, so if you haven't made NCCs for several years, they cannot be added to your NCC limit
# for the current financial year.
# The bring-forward rule is automatically triggered when you breach the annual NCC cap of $110k.

# The concessional contribution cap was reset in 2017-18 from $30k to $25k and is to be increased in
# increments of $2.5k in line with AWOTE (average earnings), not CPI (inflation).
# The NCC cap is 4 times the concessional contribution cap, so it increases at the same time.
# NOTE According to the link below, concessional contribution cap might currently be $30k instead of $27.5k, 
# and NCC cap might be $120k instead of $110k.
# https://passiveinvestingaustralia.com/when-will-the-super-caps-increase/

# In deciding how much to put inside vs outside super, determine how much you want in each timeframe:
# Anything you need in the next few years, use a high-interest savings account, fixed-term deposit, or offset account.
# Anything you need after 5 years and before you can access super, invest in low-cost index funds outside super.
# Anything you don't need until you can access super, use index options in super.
# The most tax-efficient way to split the last 2 steps is to start with super to get the tax benefits for the 
# long term first, and once the amount in super is taken care of, you can work on bringing forward your retirement
# date through outside-super investments.





# General notes about how my software system will work:
# Write lots of different files, each specialised for a certain thing.
# Being able to write multiple files is a way of having multiple return values.
# Think of each file as a snapshot of the current data.
# The software system is a series of transformations on the data files.
# This approach enables you to separate concerns and make everything modular and decoupled.
# And saving all the files means you can observe them for correctness in testing.
# And having them as files means you can either manually or programmatically generate the files.
# Will also need a validation module which checks my balance never goes below 0.

# Might need to split pre-tax modules from post-tax modules, so that I can simulate the pre-tax modules,
# generate tax receipts, apply tax, then simulate post-tax modules.

import math

class Super:
    def __init__(self, in_file):
        self.in_file = in_file
        self.shares = []
        annual_ror = 10
        self.weekly_ror = 100 * (math.exp(math.log(1 + annual_ror / 100) / 52) - 1)
        self.out_file_gen = OutputFileGenerator()
        self.out_cash_file_gen = OutputCashFileGenerator()
        self.tax_receipt_gen = TaxReceiptGenerator()

    def simulate(self, num_weeks):
        f = open(self.in_file, "r")
        input_line = f.readline().split()
        time = int(input_line[0])
        for week in range(num_weeks):
            while time == week:
                if len(input_line) == 1:
                    command = "NONE"
                elif len(input_line) == 3:
                    time, command, amount = input_line
                elif len(input_line) == 4:
                    time, command, variant, amount = input_line
                time, amount = int(time), int(amount)
                if command == "BUY":
                    if variant == "CC":
                        self.buy(amount, time)
                    elif variant == "NCC":
                        self.buy(amount, time)
                elif command == "SELL":
                    sold_shares = self.sell(amount, time)
                    self.out_cash_file_gen.add_sold_shares(sold_shares)
                    self.tax_receipt_gen.add_sold_shares(sold_shares)
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            self.out_file_gen.write_output(self.shares)
            for share in self.shares:
                share["taxed_amount"] *= 1 + self.weekly_ror / 100
                share["untaxed_earnings"] *= 1 + self.weekly_ror / 100
            if week % 52 == 0:
                self.tax(15)
        f.close()
        self.out_file_gen.generate_output_file()
        self.out_cash_file_gen.generate_output_file(num_weeks)
        self.tax_receipt_gen.generate_tax_receipt(num_weeks)

    def buy(self, amount, time):
        self.shares.append({
            "buy_time": time,
            "taxed_amount": amount,
            "untaxed_earnings": 0
            })

    def sell(self, amount, time):
        # The only way you can sell is FHSS
        amount_remaining = amount
        sold_shares = []
        while amount_remaining > 0:
            taxed_amount = self.shares[0]["taxed_amount"]
            untaxed_earnings = self.shares[0]["untaxed_earnings"]
            sell_amount = min(amount_remaining, taxed_amount + untaxed_earnings)
            sell_amount_taxed = sell_amount / (taxed_amount + untaxed_earnings) \
                    * taxed_amount
            sell_amount_untaxed = sell_amount / (taxed_amount + untaxed_earnings) \
                    * untaxed_earnings
            sold_shares.append({
                "sell_time": time,
                "taxed_amount": sell_amount_taxed,
                "untaxed_earnings": sell_amount_untaxed
            })
            self.shares[0]["taxed_amount"] -= sell_amount_taxed
            self.shares[0]["untaxed_earnings"] -= sell_amount_untaxed
            if self.shares[0]["taxed_amount"] == 0 and self.shares[0]["untaxed_earnings"] == 0:
                self.shares.pop(0)
            amount_remaining -= sell_amount
        return sold_shares

    def tax(self, tax_rate):
        for share in self.shares:
            share["taxed_amount"] += (100 - tax_rate) / 100 * share["untaxed_earnings"]
            share["untaxed_earnings"] = 0


class InputFileGenerator:
    def __init__(self, num_weeks, annual_ror):
        self.in_file = open("input_files/super.txt", "w")
        self.num_weeks = num_weeks
        self.buy_cc_list = {}
        self.buy_ncc_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            try:
                self.in_file.write(f"{week} BUY CC {self.buy_cc_list[week]}\n")
            except:
                pass
            try:
                self.in_file.write(f"{week} BUY NCC {self.buy_ncc_list[week]}\n")
            except:
                pass
            try:
                self.in_file.write(f"{week} SELL {self.sell_list[week]}\n")
            except:
                pass
            if week not in self.buy_cc_list and \
                    week not in self.buy_ncc_list and \
                    week not in self.sell_list:
                self.in_file.write(f"{week}\n")
        self.in_file.close()

    def buy(self, amount, variant, time):
        if variant == "CC":
            self.buy_cc_list[time] = amount
        elif variant == "NCC":
            self.buy_ncc_list[time] = amount

    def sell(self, amount, time):
        self.sell_list[time] = amount


class OutputFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/super.txt", "w")
        self.total_amount = []

    def write_output(self, shares):
        self.total_amount.append(sum([share["taxed_amount"] + share["untaxed_earnings"] for share in shares]))

    def generate_output_file(self):
        for week, amount in enumerate(self.total_amount):
            self.out_file.write(f"{week} {amount}\n")
        self.out_file.close()


class OutputCashFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/cash/super.txt", "w")
        self.sold_shares = []

    def add_sold_shares(self, new_sold_shares):
        self.sold_shares.extend(new_sold_shares)

    def generate_output_file(self, num_weeks):
        # I will assume sold_shares list is sorted based on sell_time
        for week in range(num_weeks):
            if len(self.sold_shares) == 0:
                break
            if self.sold_shares[0]["sell_time"] != week:
                self.out_file.write(f"{week}\n")
            else:
                taxed_amount = 0
                untaxed_earnings = 0
                while self.sold_shares[0]["sell_time"] == week:
                    taxed_amount += self.sold_shares[0]["taxed_amount"]
                    untaxed_earnings += self.sold_shares[0]["untaxed_earnings"]
                    self.sold_shares.pop(0)
                    if len(self.sold_shares) == 0:
                        break
                self.out_file.write(f"{week} {taxed_amount + untaxed_earnings}\n")
        self.out_file.close()


class TaxReceiptGenerator:
    def __init__(self):
        self.tax_file = open("output_files/tax/super.txt", "w")
        self.sold_shares = []

    def add_sold_shares(self, new_sold_shares):
        self.sold_shares.extend(new_sold_shares)

    def generate_tax_receipt(self, num_weeks):
        # I will assume sold_shares list is sorted based on sell_time
        for week in range(num_weeks):
            if len(self.sold_shares) == 0:
                break # Pretty sure we don't actually want to break here
            if self.sold_shares[0]["sell_time"] != week:
                self.tax_file.write(f"{week}\n")
            else:
                taxed_amount = 0
                untaxed_earnings = 0
                while self.sold_shares[0]["sell_time"] == week:
                    taxed_amount += self.sold_shares[0]["taxed_amount"]
                    untaxed_earnings += self.sold_shares[0]["untaxed_earnings"]
                    self.sold_shares.pop(0)
                    if len(self.sold_shares) == 0:
                        break
                self.tax_file.write(f"{week} {taxed_amount} {untaxed_earnings}\n")
        self.tax_file.close()


if __name__ == "__main__":
    num_weeks = 200
    in_file_gen = InputFileGenerator(num_weeks, 0)

    in_file_gen.buy(100, "CC", 0)
    in_file_gen.sell(10, 100)
    in_file_gen.write()

    sim = Super("input_files/super.txt")
    sim.simulate(num_weeks)
