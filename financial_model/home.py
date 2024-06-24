# I reckon have the loan in a separate input file, and simulate it separately.
# Because what if you have multiple loans, and which one are you paying off?
# Each loan can have its own separate input file.
# And in the loan input file, you can specify the amount you pay in addition
# to the minimum repayment.

import math

class Home:
    def __init__(self, in_file, params):
        self.in_file = in_file
        self.properties = []
        self.sold_properties = []
        annual_ror = params["ANNUAL_ROR"]
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
                if len(input_line) == 2:
                    time, command = input_line
                    time = int(time)
                    if command == "SELL":
                        self.sell(time)
                        self.out_cash_file_gen.add_sold_properties([self.sold_properties[-1]])
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            self.out_file_gen.write_output(self.properties)
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


class InputFileGenerator:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/home.txt", "w")
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
                temp = self.sell_list[week]
                self.in_file.write(f"{week} SELL\n")
            except:
                pass
            if week not in self.buy_list \
                    and week not in self.sell_list:
                self.in_file.write(f"{week}\n")
        self.in_file.close()

    def buy(self, amount, time):
        self.buy_list[time] = amount

    def sell(self, time):
        self.sell_list[time] = 0


class OutputFileGenerator:
    def __init__(self):
        self.out_property_file = open(f"output_files/home.txt", "w")
        self.property_value = []

    def write_output(self, properties):
        try:
            self.property_value.append(properties[0]["amount"])
        except:
            self.property_value.append(0)

    def generate_output_file(self):
        for week in range(len(self.property_value)):
            self.out_property_file.write(f"{week} {self.property_value[week]}\n")
        self.out_property_file.close()


class OutputCashFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/cash/home.txt", "w")
        self.bought_properties = []
        self.sold_properties = []

    def add_bought_properties(self, properties):
        self.bought_properties.extend(properties)

    def add_sold_properties(self, properties):
        self.sold_properties.extend(properties)

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
