use std::fs;
use std::collections::HashMap;

struct PayCommand {
    time: usize,
    amount: f64,
}

impl PayCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[2].parse::<f64>().unwrap(),
        }
    }
}

pub enum Command {
    Pay(PayCommand),
}

impl Command {
    fn new(input_line: &str) -> Result<Self, &str> {
        let fields: Vec<&str> = input_line.split_whitespace()
                                            .collect();
        match fields[1] {
            "PAY" => Ok(Self::Pay(PayCommand::new(fields))),
            _ => Err("Failed to parse command"),
        }
    }
}

pub fn parse_input(file_path: &str) -> HashMap<usize, Vec<Command>> {
    let input_lines = fs::read_to_string(file_path)
        .expect("Invalid file path");
    let commands: Vec<Command> = input_lines.lines()
                .map(|line| Command::new(line).unwrap())
                .collect();
    let mut commands_map: HashMap<usize, Vec<Command>> = HashMap::new();
    for command in commands {
        match command {
            Command::Pay(PayCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
        }
    }
    commands_map
}

//TODO:Have single source of truth for number of timesteps
const NUM_TIMESTEPS: usize = 35 * 52;

pub struct Params {
    annual_indexation_rate: f64,
}

impl Params {
    pub fn new(annual_indexation_rate: f64) -> Self {
        Self {
            annual_indexation_rate,
        }
    }
}

pub struct PayReceipt {
    pub time: usize,
    pub amount: f64,
}

impl PayReceipt {
    fn new(time: usize, amount: f64) -> Self {
        Self {
            time,
            amount,
        }
    }
}

pub enum Transaction {
    Pay(PayReceipt),
}

pub struct Asset {
    value: [f64; NUM_TIMESTEPS],
    minimum_weekly_repayment: Option<f64>,
}

impl Asset {
    pub fn new() -> Self {
        Self {
            value: [0.0; NUM_TIMESTEPS],
            minimum_weekly_repayment: None,
        }
    }

    pub fn simulate_timestep(&mut self, time: usize, params: Params, commands: &HashMap<usize, Vec<Command>>, repayment_income: &[f64; NUM_TIMESTEPS]) -> Option<Vec<Transaction>> {
        let weekly_interest_rate = annual_to_weekly_interest_rate(params.annual_indexation_rate);
        let year_repayment_income = compute_repayment_income(repayment_income, time);
        //TODO:Fix bug below where never any minimum repayment
        //Will be fixed when I add support for initial values, because no
        //repayment if no HECS debt
        if self.value[time] == 0.0 {
            self.minimum_weekly_repayment = None;
        } else {
            self.minimum_weekly_repayment = Some(minimum_repayment(year_repayment_income));
        }
        if time > 0 {
            self.value[time] = self.value[time - 1] * (1.0 + weekly_interest_rate / 100.0);
        }
        let mut receipts = Vec::<Transaction>::new();
        if let Some(repayment) = self.minimum_weekly_repayment {
            if self.value[time] < repayment {
                let amount = self.value[time];
                self.value[time] -= amount;
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
                self.minimum_weekly_repayment = None;
            } else {
                let amount = repayment;
                self.value[time] -= repayment;
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
            }
        }
        if let Some(commands_vec) = commands.get(&time) {
            for command in commands_vec {
                match command {
                    Command::Pay(PayCommand { time, amount }) => {
                        if self.value[*time] < *amount {
                            let actual_amount = self.value[*time];
                            self.value[*time] -= actual_amount;
                            receipts.push(Transaction::Pay(PayReceipt::new(*time,
                                                                           actual_amount)));
                        } else {
                            self.value[*time] -= amount;
                            receipts.push(Transaction::Pay(PayReceipt::new(*time, *amount)));
                        }
                    },
                }
            }
        }
        if receipts.len() > 0 {
            Some(receipts)
        } else {
            None
        }
    }

    pub fn write_to_file(&self, filepath: &str) {
        let mut text: String = "".into();
        for (i, val) in self.value.iter().enumerate() {
            text = format!("{}{} {}\n", text, i, val);
        }
        fs::write(filepath, text).expect("Unable to write output file");
    }
}

fn annual_to_weekly_interest_rate(annual_interest_rate: f64) -> f64 {
    100.0 * (((1.0 + annual_interest_rate / 100.0).ln() / 52.0).exp() - 1.0)
}

fn compute_repayment_income(repayment_income: &[f64; NUM_TIMESTEPS], time: usize) -> f64 {
    let lower_bound = time / 52 * 52;
    let upper_bound = std::cmp::min(NUM_TIMESTEPS, ((time / 52) + 1) * 52);
    repayment_income[lower_bound .. upper_bound].into_iter().sum()
}

fn minimum_repayment(repayment_income: f64) -> f64 {
    let hecs_brackets = [0.0,
                        54435.0,
                        62850.0,
                        66620.0,
                        70618.0,
                        74855.0,
                        79346.0,
                        84107.0,
                        89154.0,
                        94503.0,
                        100174.0,
                        106185.0,
                        112556.0,
                        119309.0,
                        126467.0,
                        134056.0,
                        142100.0,
                        150626.0,
                        159663.0,
                        f64::MAX];

    let repayment_rates = [0.0,
                            1.0,
                            2.0,
                            2.5,
                            3.0,
                            3.5,
                            4.0,
                            4.5,
                            5.0,
                            5.5,
                            6.0,
                            6.5,
                            7.0,
                            7.5,
                            8.0,
                            8.5,
                            9.0,
                            9.5,
                            10.0];

    for i in 0..19 {
        if repayment_income >= hecs_brackets[i] && repayment_income <= hecs_brackets[i+1] {
            return repayment_income * repayment_rates[i] / 100.0 / 52.0;
        }
    }
    panic!("Repayment income should be a non-negative number");
}
