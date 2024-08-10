class Home:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/home.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} BUY {transaction}\n")
            if week in self.sell_list:
                for _ in self.sell_list[week]:
                    self.in_file.write(f"{week} SELL\n")
        self.in_file.close()

    def buy(self, amount, time):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append(amount)

    def sell(self, time):
        if time not in self.sell_list:
            self.sell_list[time] = []
        self.sell_list[time].append(time)


class HomeLoan:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/home_loan.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.pay_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} START {transaction['amount']} " \
                                        f"{transaction['duration']}\n")
            if week in self.pay_list:
                for transaction in self.pay_list[week]:
                    self.in_file.write(f"{week} PAY {transaction}\n")
        self.in_file.close()

    def buy(self, amount, time, duration):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": amount,
            "duration": duration,
        })
    
    def pay(self, amount, time):
        if time not in self.pay_list:
            self.pay_list[time] = []
        self.pay_list[time].append(amount)


class CarLoan:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/car_loan.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} START {transaction['amount']} " \
                                        f"{transaction['balloon_payment']} " \
                                        f"{transaction['duration']}\n")
        self.in_file.close()

    def buy(self, amount, balloon_payment, time, duration):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": amount,
            "balloon_payment": balloon_payment,
            "duration": duration,
        })


class Hecs:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/hecs.txt", "w")
        self.num_weeks = num_weeks
        self.pay_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.pay_list:
                for transaction in self.pay_list[week]:
                    self.in_file.write(f"{week} PAY {transaction['amount']}\n")
        self.in_file.close()

    def pay(self, amount, time):
        if time not in self.pay_list:
            self.pay_list[time] = []
        self.pay_list[time].append({
            "amount": amount,
        })


class Shares:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/shares.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} BUY {transaction['amount']}\n")
            if week in self.sell_list:
                for transaction in self.sell_list[week]:
                    self.in_file.write(f"{week} SELL {transaction['amount']}\n")
        self.in_file.close()

    def buy(self, amount, time):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": amount,
        })

    def sell(self, amount, time):
        if time not in self.sell_list:
            self.sell_list[time] = []
        self.sell_list[time].append({
            "amount": amount,
        })


class Superannuation:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/super.txt", "w")
        self.num_weeks = num_weeks
        self.buy_sg_list = {}
        self.buy_cc_list = {}
        self.buy_ncc_list = {}
        self.sell_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_sg_list:
                for transaction in self.buy_sg_list[week]:
                    self.in_file.write(f"{week} BUY SG {transaction['amount']}\n")
            if week in self.buy_cc_list:
                for transaction in self.buy_cc_list[week]:
                    self.in_file.write(f"{week} BUY CC {transaction['amount']}\n")
            if week in self.buy_ncc_list:
                for transaction in self.buy_ncc_list[week]:
                    self.in_file.write(f"{week} BUY NCC {transaction['amount']}\n")
            if week in self.sell_list:
                for transaction in self.sell_list[week]:
                    self.in_file.write(f"{week} SELL {transaction['amount']}\n")
        self.in_file.close()

    def buy(self, amount, variant, time):
        if variant == "SG":
            if time not in self.buy_sg_list:
                self.buy_sg_list[time] = []
            self.buy_sg_list[time].append({
                "amount": amount,
            })
        if variant == "CC":
            if time not in self.buy_cc_list:
                self.buy_cc_list[time] = []
            self.buy_cc_list[time].append({
                "amount": amount,
            })
        elif variant == "NCC":
            if time not in self.buy_ncc_list:
                self.buy_ncc_list[time] = []
            self.buy_ncc_list[time].append({
                "amount": amount,
            })

    def sell(self, amount, time):
        if time not in self.sell_list:
            self.sell_list[time] = []
        self.sell_list[time].append({
            "amount": amount,
        })


class Income:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/income.txt", "w")
        self.num_weeks = num_weeks
        self.income_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.income_list:
                for transaction in self.income_list[week]:
                    self.in_file.write(f"{week} {transaction['amount']}\n")
        self.in_file.close()

    def add(self, amount, time):
        if time not in self.income_list:
            self.income_list[time] = []
        self.income_list[time].append({
            "amount": amount,
        })


class Misc:
    def __init__(self, num_weeks):
        self.in_file = open("input_files/misc.txt", "w")
        self.num_weeks = num_weeks
        self.buy_list = {}

    def write(self):
        for week in range(self.num_weeks):
            if week in self.buy_list:
                for transaction in self.buy_list[week]:
                    self.in_file.write(f"{week} {transaction['amount']}\n")
        self.in_file.close()

    def add(self, amount, time):
        if time not in self.buy_list:
            self.buy_list[time] = []
        self.buy_list[time].append({
            "amount": amount,
        })


if __name__ == "__main__":
    num_weeks = 35 * 52

    income_file_gen = Income(num_weeks)
    misc_file_gen = Misc(num_weeks)
    home_file_gen = Home(num_weeks)
    home_loan_file_gen = HomeLoan(num_weeks)
    car_loan_file_gen = CarLoan(num_weeks)
    shares_file_gen = Shares(num_weeks)
    superannuation_file_gen = Superannuation(num_weeks)
    hecs_file_gen = Hecs(num_weeks)

    for week in range(num_weeks):
        income_file_gen.add(1442, week)

    misc_file_gen.add(-135000, 0)
    shares_file_gen.buy(135000, 0)



    #misc_file_gen.add(-8000, 0)
    #home_file_gen.buy(500000, 0)
    #home_file_gen.sell(52)
    #home_loan_file_gen.buy(300000, 0, 30)
    #home_loan_file_gen.pay(10000, 52)
    #car_loan_file_gen.buy(20000, 10000, 0, 1)
    #shares_file_gen.buy(100000, 1)
    #shares_file_gen.sell(10000, 53)
    #superannuation_file_gen.buy(10000, "CC", 1)
    #superannuation_file_gen.sell(1000, 53)
    #for week in range(num_weeks):
        #superannuation_file_gen.buy(0.11 * 1442, "SG", week)
        #superannuation_file_gen.buy(1000, "NCC", week)
    #superannuation_file_gen.sell(10000, 26)
    #hecs_file_gen.pay(1000, 1)

    income_file_gen.write()
    misc_file_gen.write()
    home_file_gen.write()
    home_loan_file_gen.write()
    car_loan_file_gen.write()
    shares_file_gen.write()
    superannuation_file_gen.write()
    hecs_file_gen.write()
