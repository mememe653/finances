import math

class Hecs:
    def __init__(self, in_file, params):
        self.in_file = in_file
        self.brackets_file = open("input_files/hecs_brackets.txt", "r")
        self.income_file = open("input_files/income.txt", "r")
        self.out_file_gen = OutputFileGenerator()
        self.out_cash_file_gen = OutputCashFileGenerator()
        self.interest_rate = params["ANNUAL_INDEXATION_RATE"]
        self.weekly_interest_rate = (math.exp(math.log(1 + self.interest_rate / 100) / 52) - 1) \
                                    * 100

    def simulate(self, num_weeks):
        f = open(self.in_file, "r")
        hecs_debt_started = False
        input_line = f.readline().split()
        time = int(input_line[0])
        for week in range(num_weeks):
            while time == week:
                if len(input_line) == 3:
                    time, command, amount = input_line
                    time, amount = int(time), int(amount)
                    if command == "START":
                        self.buy(amount, week)
                        hecs_debt_started = True
                    if command == "PAY":
                        self.pay(amount, week)
                        self.out_cash_file_gen.add_payment({
                            "time": week,
                            "amount": amount
                        })
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            if hecs_debt_started:
                self.weekly_repayment = self.minimum_repayment(week)
            self.out_file_gen.write_output(self.loan_amount)
            if self.loan_amount > 0:
                self.out_cash_file_gen.add_payment({
                    "time": week,
                    "amount": self.weekly_repayment
                })
                self.loan_amount *= 1 + self.weekly_interest_rate / 100
                self.loan_amount -= self.weekly_repayment
        f.close()
        self.brackets_file.close()
        self.income_file.close()
        self.out_file_gen.generate_output_file()
        self.out_cash_file_gen.generate_output_file(num_weeks)

    def buy(self, amount, time):
        self.loan_amount = amount

    def pay(self, amount, time):
        self.loan_amount -= amount

    def minimum_repayment(self, time):
        #TODO:Fix this method, because each income bracket should be compared against
        #     taxable income plus super contributions
        income_brackets = []
        repayment_rates = []
        while len(income_brackets) == 0 or len(repayment_rates) == 0:
            input_line = self.brackets_file.readline().split()
            if len(input_line) > 0:
                week = int(input_line[0])
                command = input_line[1]
                if week == time:
                    if command == "RATES":
                        for i in range(2, len(input_line)):
                            repayment_rates.append(float(input_line[i]))
                    if command == "BRACKETS":
                        for i in range(2, len(input_line)):
                            income_brackets.append(int(input_line[i]))

        week, weekly_income = self.income_file.readline().split()
        week = int(week)
        while week != time:
            week, weekly_income = self.income_file.readline().split()
            week = int(week)
        weekly_income = int(weekly_income)
        annual_income = weekly_income * 52
        for i, income_bracket in enumerate(income_brackets):
            if annual_income < income_bracket:
                repayment_rate = repayment_rates[i]
                break
        if annual_income > income_brackets[-1]:
            repayment_rate = repayment_rates[-1]
        return weekly_income * repayment_rate / 100


class InputFileGenerator:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/hecs.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.pay_list = {}

    def write(self):
        for week in range(self.num_weeks):
            try:
                self.in_file.write(f"{week} START {self.buy_list[week]}\n")
            except:
                pass
            try:
                self.in_file.write(f"{week} PAY {self.pay_list[week]}\n")
            except:
                pass
            if week not in self.buy_list \
                    and week not in self.pay_list:
                self.in_file.write(f"{week}\n")
        self.in_file.close()

    def buy(self, amount, time):
        self.buy_list[time] = amount

    def pay(self, amount, time):
        self.pay_list[time] = amount


class OutputFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/hecs.txt", "w")
        self.loan_value = []

    def write_output(self, amount):
        self.loan_value.append(amount)

    def generate_output_file(self):
        for week in range(len(self.loan_value)):
            self.out_file.write(f"{week} {self.loan_value[week]}\n")
        self.out_file.close()


class OutputCashFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/cash/hecs.txt", "w")
        self.loan_payments = []

    def add_payment(self, payment):
        self.loan_payments.append(payment)

    def generate_output_file(self, num_weeks):
        # I will assume the list is sorted based on time
        for week in range(num_weeks):
            amount = 0
            if len(self.loan_payments) == 0:
                break
            while week == self.loan_payments[0]["time"]:
                amount += self.loan_payments[0]["amount"]
                self.loan_payments.pop(0)
                if len(self.loan_payments) == 0:
                    break
            self.out_file.write(f"{week} {-amount}\n")
        self.out_file.close()


if __name__ == "__main__":
    num_weeks = 104
    params = {
            "annual_indexation_rate": 4
        }

    input_file_gen = InputFileGenerator(num_weeks)
    input_file_gen.buy(20000, 0)
    input_file_gen.write()

    hecs = Hecs("input_files/hecs.txt", params)
    hecs.simulate(num_weeks)
