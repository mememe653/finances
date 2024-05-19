import math

class Home:
    def __init__(self, in_file):
        self.in_file = in_file
        self.properties = []
        self.sold_properties = []
        self.loans = []
        annual_ror = 10
        self.weekly_ror = 100 * (math.exp(math.log(1 + annual_ror / 100) / 52) - 1)
        self.out_file_gen = OutputFileGenerator()
        self.out_cash_file_gen = OutputCashFileGenerator()

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
                        self.out_cash_file_gen.add_bought_properties([self.properties[-1]])
                    elif command == "LOAN":
                        pass
                    elif command == "SELL":
                        self.sell(time)
                        self.out_cash_file_gen.add_sold_properties([self.sold_properties[-1]])
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            self.out_file_gen.write_output(self.properties, self.loans)
            for home in self.properties:
                home["amount"] *= 1 + self.weekly_ror / 100
        f.close()
        self.out_file_gen.generate_output_file()
        self.out_cash_file_gen.generate_output_file(num_weeks)

    def buy(self, amount, time):
        self.properties.append({
            "buy_time": time,
            "buy_amount": amount,
            "amount": amount
        })

    def sell(self, time):
# For now I will assume I only have 1 property, because multiple properties are treated
# differently with regard to CGT.
        self.sold_properties.append({
            "sell_time": time,
            "amount": self.properties[0]["amount"]
        })
        self.properties.pop(0)


class HomeLoan:
    def __init__(self, amount, duration):
        self.amount = amount
        self.duration = duration
        self.interest_rate = 6
        self.weekly_repayment = self.minimum_repayment(amount, self.interest_rate, duration)

    def pay(self, amount):
        # Do additional repayments reduce your recurring minimum weekly repayment?
        self.amount -= amount + self.weekly_repayment

    def minimum_repayment(self, loan_amount, interest_rate, loan_years):
        weekly_interest_rate = interest_rate / 52 / 100
        num_payments = loan_years * 52
        return (loan_amount * weekly_interest_rate * (1 + weekly_interest_rate) \
                ** num_payments) / ((1 + weekly_interest_rate) ** num_payments - 1)


class InputFileGenerator:
    def __init__(self, num_weeks, annual_ror):
        self.in_file = open("input_files/home.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.loan_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            try:
                self.in_file.write(f"{week} BUY {self.buy_list[week]}\n")
            except:
                pass
            try:
                self.in_file.write(f"{week} LOAN {self.loan_list[week]}\n")
            except:
                pass
            try:
                self.in_file.write(f"{week} SELL {self.sell_list[week]}\n")
            except:
                pass
            if week not in self.buy_list \
                    and week not in self.loan_list \
                    and week not in self.sell_list:
                self.in_file.write(f"{week}\n")
        self.in_file.close()

    def buy(self, amount, time, loan_amount):
        self.buy_list[time] = amount
        if loan_amount > 0:
            self.loan_list[time] = loan_amount

    def sell(self, amount, time):
        self.sell_list[time] = amount


class OutputFileGenerator:
    def __init__(self):
        self.out_property_file = open(f"output_files/home.txt", "w")
        self.out_loan_file = open(f"output_files/home_loan.txt", "w")
        self.property_value = []
        self.loan_value = []

    def write_output(self, properties, loans):
        self.property_value.append(properties[0]["amount"])
        self.loan_value.append(sum([loan.amount for loan in loans]))

    def generate_output_files(self):
        for week in range(len(self.property_value)):
            self.out_property_file.write(f"{week} {self.property_value[week]}\n")
            self.out_loan_file.write(f"{week} {self.loan_value[week]}\n")
        self.out_property_file.close()
        self.out_loan_file.close()


class OutputCashFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/cash/home.txt", "w")
        self.bought_properties = []
        self.sold_properties = []
        self.loan_payments = []

    def add_bought_properties(self, properties):
        self.bought_properties.extend(properties)

    def add_sold_properties(self, properties):
        self.sold_properties.extend(properties)

    def add_loan_payments(self, payments):
        pass

    def generate_output_file(self, num_weeks):
        # I will assume every list is sorted based on sell_time
        for week in range(num_weeks):
            amount = 0
            if len(self.bought_properties) > 0 \
                    and self.bought_properties[0]["buy_time"] == week:
                amount -= self.bought_properties[0]["buy_amount"]
                self.bought_properties.pop(0)
            if len(self.sold_properties) > 0 \
                    and self.sold_properties[0]["sell_time"] == week:
                amount += self.sold_properties[0]["amount"]
            self.out_file.write(f"{week} {amount}\n")
        self.out_file.close()
