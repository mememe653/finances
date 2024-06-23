import math

class HomeLoan:
    def __init__(self, in_file, params):
        self.in_file = in_file
        self.out_file_gen = OutputFileGenerator()
        self.out_cash_file_gen = OutputCashFileGenerator()
        self.interest_rate = params["annual_interest_rate"]
        #self.weekly_interest_rate = self.interest_rate / 52 / 100
        self.weekly_interest_rate = (math.exp(math.log(1 + self.interest_rate / 100) / 52) - 1) \
                                    * 100

    def simulate(self, num_weeks):
        f = open(self.in_file, "r")
        self.loan_amount = 0
        input_line = f.readline().split()
        time = int(input_line[0])
        for week in range(num_weeks):
            while time == week:
                if len(input_line) == 4:
                    time, command, amount, duration = input_line
                    time, amount, duration = int(time), int(amount), int(duration)
                    if command == "START":
                        self.buy(amount, time)
                        self.out_cash_file_gen.add_loan(amount, time)
                        self.weekly_repayment = self.minimum_repayment(amount, \
                                                                        self.interest_rate, \
                                                                        duration)
                if len(input_line) == 3:
                    time, command, amount = input_line
                    time, amount = int(time), int(amount)
                    if command == "PAY":
                        self.pay(amount, time)
                        self.out_cash_file_gen.add_payment({
                            "time": time,
                            "amount": amount
                        })
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            self.out_file_gen.write_output(self.loan_amount)
            if self.loan_amount > 0:
                self.out_cash_file_gen.add_payment({
                    "time": week,
                    "amount": self.weekly_repayment
                })
                self.loan_amount *= 1 + self.weekly_interest_rate / 100
                self.loan_amount -= self.weekly_repayment
            else:
                self.loan_amount = 0
        f.close()
        self.out_file_gen.generate_output_file()
        self.out_cash_file_gen.generate_output_file(num_weeks)

    def buy(self, amount, time):
        self.loan_amount = amount

    def pay(self, amount, time):
        self.loan_amount -= amount

    def minimum_repayment(self, loan_amount, interest_rate, loan_years):
        weekly_interest_rate = interest_rate / 52 / 100
        num_payments = loan_years * 52
        return (loan_amount * weekly_interest_rate * (1 + weekly_interest_rate) \
                ** num_payments) / ((1 + weekly_interest_rate) ** num_payments - 1)


class InputFileGenerator:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/home_loan.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.pay_list = {}

    def write(self):
        for week in range(self.num_weeks):
            try:
                self.in_file.write(f"{week} START {self.buy_list[week]['amount']} " \
                                    f"{self.buy_list[week]['duration']}\n")
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

    def buy(self, amount, time, duration):
        self.buy_list[time] = {
                "amount": amount,
                "duration": duration
            }

    def pay(self, amount, time):
        self.pay_list[time] = amount


class OutputFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/home_loan.txt", "w")
        self.loan_value = []

    def write_output(self, amount):
        self.loan_value.append(amount)

    def generate_output_file(self):
        for week in range(len(self.loan_value)):
            self.out_file.write(f"{week} {self.loan_value[week]}\n")
        self.out_file.close()


class OutputCashFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/cash/home_loan.txt", "w")
        self.loan_payments = []

    def add_loan(self, amount, time):
        self.loan = {
                "buy_time": time,
                "amount": amount
            }

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
            if week == self.loan["buy_time"]:
                self.out_file.write(f"{week} {self.loan['amount'] - amount}\n")
            else:
                self.out_file.write(f"{week} {-amount}\n")
        self.out_file.close()


if __name__ == "__main__":
    num_weeks = 520
    params = {
            "annual_interest_rate": 6
        }

    input_file_gen = InputFileGenerator(num_weeks)
    input_file_gen.buy(100, 0, 5)
    input_file_gen.write()

    home_loan = HomeLoan("input_files/home_loan.txt", params)
    home_loan.simulate(num_weeks)
