# Note that a positive expense is turned into a negative cash amount

class InputFileGenerator:
    def __init__(self, num_weeks):
        self.num_weeks = num_weeks
        self.expenses = []
        self.out_file = "misc.txt"

    def write(self):
        self.expenses.sort(key=lambda x: x["time"])
        f = open(f"input_files/{self.out_file}", "w")
        for week in range(self.num_weeks):
            if len(self.expenses) == 0:
                f.write(f"{week} 0\n")
                continue
            time = self.expenses[0]["time"]
            amount = 0
            while time == week:
                amount += self.expenses[0]["amount"]
                self.expenses.pop(0)
                if len(self.expenses) == 0:
                    break
                time = self.expenses[0]["time"]
            f.write(f"{week} {amount}\n")
        f.close()

    def add(self, week, amount):
        self.expenses.append({
            "time": week,
            "amount": -amount
        })
