import math

class CarLoan:
    def __init__(self, in_file):
        self.in_file = in_file
        self.out_file_gen = OutputFileGenerator()
        self.out_cash_file_gen = OutputCashFileGenerator()
        self.interest_rate = 7
        self.weekly_interest_rate = (math.exp(math.log(1 + self.interest_rate / 100) / 52) - 1) \
                                    * 100

    def simulate(self, num_weeks):
        f = open(self.in_file, "r")
        input_line = f.readline().split()
        time = int(input_line[0])
        for week in range(num_weeks):
            while time == week:
                if len(input_line) == 5:
                    time, command, amount, balloon_payment, duration = input_line
                    time, amount, balloon_payment = int(time), int(amount), int(balloon_payment)
                    duration = int(duration)
                    if command == "START":
                        self.buy(amount, balloon_payment, time, duration)
                        self.weekly_repayment = self.minimum_repayment(self.loan_amount, \
                                                                        self.interest_rate, \
                                                                        duration)
                input_line = f.readline().split()
                if len(input_line) == 0:
                    break
                time = int(input_line[0])
            self.out_file_gen.write_output(self.loan_amount \
                                            + self.balloon_payment["amount"])
            if week == self.balloon_payment["time"]:
                self.out_cash_file_gen.add_payment({
                    "time": week,
                    "amount": self.balloon_payment["amount"]
                })
                #self.loan_amount -= self.balloon_payment["amount"]
                self.balloon_payment["amount"] = 0
            self.balloon_payment["amount"] *= 1 + self.weekly_interest_rate / 100
            if self.loan_amount > 0:
                self.out_cash_file_gen.add_payment({
                    "time": week,
                    "amount": self.weekly_repayment
                })
                self.loan_amount *= 1 + self.weekly_interest_rate / 100
                self.loan_amount -= self.weekly_repayment
        f.close()
        self.out_file_gen.generate_output_file()
        self.out_cash_file_gen.generate_output_file(num_weeks)

    def buy(self, amount, balloon_payment, time, duration):
        self.loan_amount = amount - balloon_payment
        self.balloon_payment = {
                "amount": balloon_payment,
                "time": time + 52 * duration
            }

    def pay(self, amount):
        pass

    def minimum_repayment(self, loan_amount, interest_rate, loan_years):
        weekly_interest_rate = interest_rate / 52 / 100
        num_payments = loan_years * 52
        return (loan_amount * weekly_interest_rate * (1 + weekly_interest_rate) \
                ** num_payments) / ((1 + weekly_interest_rate) ** num_payments - 1)


class InputFileGenerator:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/car_loan.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}

    def write(self):
        for week in range(self.num_weeks):
            try:
                self.in_file.write(f"{week} START {self.buy_list[week]['amount']} " \
                                    f"{self.buy_list[week]['balloon_payment']} " \
                                    f"{self.buy_list[week]['duration']}\n")
            except:
                pass
            if week not in self.buy_list:
                self.in_file.write(f"{week}\n")
        self.in_file.close()

    def buy(self, amount, balloon_payment, time, duration):
        self.buy_list[time] = {
                "amount": amount,
                "balloon_payment": balloon_payment,
                "duration": duration
            }


class OutputFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/car_loan.txt", "w")
        self.loan_value = []

    def write_output(self, amount):
        self.loan_value.append(amount)

    def generate_output_file(self):
        for week in range(len(self.loan_value)):
            self.out_file.write(f"{week} {self.loan_value[week]}\n")
        self.out_file.close()


class OutputCashFileGenerator:
    def __init__(self):
        self.out_file = open("output_files/cash/car_loan.txt", "w")
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
    input_file_gen = InputFileGenerator(520)
    input_file_gen.buy(100, 20, 0, 5)
    input_file_gen.write()

    car_loan = CarLoan("input_files/car_loan.txt")
    car_loan.simulate(520)
