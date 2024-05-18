class InputFileGenerator:
    def __init__(self, num_weeks):
        self.num_weeks = num_weeks
        self.income = {}
        self.out_file = "income.txt"

    def write(self):
        f = open(f"input_files/{self.out_file}", "w")
        for week in range(self.num_weeks):
            try:
                f.write(f"{week} {self.income[week]}\n")
            except:
                f.write(f"{week}\n")
        f.close()

    def add(self, week, amount):
        self.income[week] = amount


if __name__ == "__main__":
    num_weeks = 104
    generator = InputFileGenerator(num_weeks)
    for week in range(num_weeks):
        generator.add(week, 2000)
    generator.write()
