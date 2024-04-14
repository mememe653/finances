# I think read from input file which directs the simulation
# But also write to output file which can be read by external parties like tax collector
# Probably write out as JSON

# I could improve accuracy of my code by only allowing to buy/sell an integer number of shares
# I will make it so that you buy each share at $1, because I won't bother with cents
import math

class Shares:
    def __init__(self, in_file):
        self.in_file = in_file
        self.shares = []
        annual_ror = 10
        self.weekly_ror = 100 * (math.exp(math.log(1 + annual_ror / 100) / 52) - 1)
        self.out_file_gen = OutputFileGenerator()
        self.tax_receipt_gen = TaxReceiptGenerator()

    def simulate(self, num_weeks):
        f = open(self.in_file, "r")
        input_line = f.readline().split()
        time = int(input_line[0])
        for week in range(num_weeks):
            while time == week:
                if len(input_line) == 3:
                    time, command, amount = input_line
                    time, amount = int(time), int(amount)
                    if command == "BUY":
                        self.buy(amount, time)
                    elif command == "SELL":
                        sold_shares = self.sell(amount, time)
                        self.tax_receipt_gen.add_sold_shares(sold_shares)
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            self.out_file_gen.write_output(self.shares)
            for i in range(len(self.shares)):
                self.shares[i]["amount"] *= 1 + self.weekly_ror / 100
        f.close()
        self.out_file_gen.generate_output_file()
        self.tax_receipt_gen.generate_tax_receipt(num_weeks)

    def buy(self, amount, time):
        self.shares.append({
            "buy_time": time,
            "buy_amount": amount,
            "amount": amount
            })

    def sell(self, amount, time):
        amount_remaining = amount
        sold_shares = []
        while amount_remaining > 0:
            sell_amount = min(amount_remaining, self.shares[0]["buy_amount"])
            capital_gains = sell_amount / self.shares[0]["buy_amount"] \
                    * (self.shares[0]["amount"] - self.shares[0]["buy_amount"])
            sold_shares.append({
                "sell_time": time,
                "amount": sell_amount,
                "capital_gains": capital_gains,
                "cgt_discount": (time - self.shares[0]["buy_time"]) > 52
            })
            self.shares[0]["amount"] -= sell_amount * self.shares[0]["amount"] \
                    / self.shares[0]["buy_amount"]
            self.shares[0]["buy_amount"] -= sell_amount
            if self.shares[0]["amount"] == 0:
                self.shares.pop(0)
            amount_remaining -= sell_amount
        return sold_shares


class InputFileGenerator:
    def __init__(self, num_weeks, annual_ror):
        self.in_file = open("input_files/shares.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            try:
                self.in_file.write(f"{week} BUY {self.buy_list[week]}\n")
            except:
                pass
            try:
                self.in_file.write(f"{week} SELL {self.sell_list[week]}\n")
            except:
                pass
            if week not in self.buy_list and week not in self.sell_list:
                self.in_file.write(f"{week}\n")
        self.in_file.close()

    def buy(self, amount, time):
        self.buy_list[time] = amount

    def sell(self, amount, time):
        self.sell_list[time] = amount


class OutputFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/shares.txt", "w")
        self.total_amount = []

    def write_output(self, shares):
        self.total_amount.append(sum([share["amount"] for share in shares]))

    def generate_output_file(self):
        for week, amount in enumerate(self.total_amount):
            self.out_file.write(f"{week} {amount}\n")
        self.out_file.close()


class TaxReceiptGenerator:
    def __init__(self):
        self.tax_file = open("output_files/tax/shares.txt", "w")
        self.sold_shares = []

    def add_sold_shares(self, new_sold_shares):
        self.sold_shares.extend(new_sold_shares)

    def generate_tax_receipt(self, num_weeks):
        # I will assume sold_shares list is sorted based on sell_time
        for week in range(num_weeks):
            if len(self.sold_shares) == 0:
                break
            if self.sold_shares[0]["sell_time"] != week:
                self.tax_file.write(f"{week}\n")
            else:
                capital_gains = 0
                while self.sold_shares[0]["sell_time"] == week:
                    capital_gains += self.sold_shares[0]["capital_gains"]
                    cgt_discount = self.sold_shares[0]["cgt_discount"]
                    self.sold_shares.pop(0)
                    if len(self.sold_shares) == 0:
                        break
                taxable_income = capital_gains if not cgt_discount else capital_gains / 2
                self.tax_file.write(f"{week} {taxable_income}\n")
        self.tax_file.close()



if __name__ == "__main__":
    num_weeks = 104
    in_file_gen = InputFileGenerator(num_weeks, 10)
    in_file_gen.buy(100, 0)
    in_file_gen.sell(90, 52)
    in_file_gen.write()

    shares_sim = Shares("input_files/shares.txt")
    shares_sim.simulate(num_weeks)
