use std::fs;
use std::collections::HashMap;

use super::NUM_TIMESTEPS as NUM_TIMESTEPS;

struct StartCommand {
    time: usize,
    amount: f64,
    duration: usize,
}

impl StartCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[2].parse::<f64>().unwrap(),
            duration: fields[3].parse::<usize>().unwrap(),
        }
    }
}

struct PayCommand {
    time: usize,
    amount: f64,
}

struct StartAllCommand {
    time: usize,
    duration: usize,
}

impl StartAllCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            duration: fields[3].parse::<usize>().unwrap(),
        }
    }
}

impl PayCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[2].parse::<f64>().unwrap(),
        }
    }
}

struct PayAllCommand {
    time: usize,
}

impl PayAllCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
        }
    }
}

pub enum Command {
    Start(StartCommand),
    StartAll(StartAllCommand),
    Pay(PayCommand),
    PayAll(PayAllCommand),
}

impl Command {
    fn new(input_line: &str) -> Result<Self, &str> {
        let fields: Vec<&str> = input_line.split_whitespace()
                                            .collect();
        match fields[1] {
            "START" => {
                match fields[2] {
                    "ALL" => Ok(Self::StartAll(StartAllCommand::new(fields))),
                    _ => Ok(Self::Start(StartCommand::new(fields))),
                }
            },
            "PAY" => {
                match fields[2] {
                    "ALL" => Ok(Self::PayAll(PayAllCommand::new(fields))),
                    _ => Ok(Self::Pay(PayCommand::new(fields))),
                }
            },
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
            Command::Start(StartCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::StartAll(StartAllCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::Pay(PayCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::PayAll(PayAllCommand { time }) => {
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

pub struct Params {
    annual_interest_rate: f64,
}

impl Params {
    pub fn new(annual_interest_rate: f64) -> Self {
        Self {
            annual_interest_rate,
        }
    }
}

pub struct StartReceipt {
    pub time: usize,
    pub amount: f64,
}

impl StartReceipt {
    fn new(time: usize, amount: f64) -> Self {
        Self {
            time,
            amount,
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
    Start(StartReceipt),
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

    pub fn simulate_timestep(&mut self, time: usize, params: Params, commands: &HashMap<usize, Vec<Command>>, cash: &[f64; NUM_TIMESTEPS]) -> Option<Vec<Transaction>> {
        let weekly_interest_rate = annual_to_weekly_interest_rate(params.annual_interest_rate);
        if time > 0 {
            self.value[time] = self.value[time - 1] * (1.0 + weekly_interest_rate / 100.0);
        }
        let mut receipts = Vec::<Transaction>::new();
        if let Some(minimum_repayment) = self.minimum_weekly_repayment {
            if self.value[time] < minimum_repayment {
                let amount = self.value[time];
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
                self.value[time] -= amount;
            } else {
                let amount = minimum_repayment;
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
                self.value[time] -= amount;
            }
        }
        if let Some(commands_vec) = commands.get(&time) {
            for command in commands_vec {
                match command {
                    Command::Start(StartCommand { time, amount, duration }) => {
                        self.value[*time] = *amount;
                        self.minimum_weekly_repayment = Some(minimum_repayment(*amount,
                                                            params.annual_interest_rate,
                                                            *duration));
                        receipts.push(Transaction::Start(StartReceipt::new(*time, *amount)));
                    },
                    Command::StartAll(StartAllCommand { time, duration }) => {
                        let amount = cash[*time];
                        self.value[*time] = amount;
                        self.minimum_weekly_repayment = Some(minimum_repayment(amount,
                                                            params.annual_interest_rate,
                                                            *duration));
                        receipts.push(Transaction::Start(StartReceipt::new(*time, amount)));
                    },
                    Command::Pay(PayCommand { time, amount }) => {
                        if self.value[*time] < *amount {
                            receipts.push(Transaction::Pay(PayReceipt::new(*time,
                                                                           self.value[*time])));
                            self.value[*time] = 0.0;
                        } else {
                            receipts.push(Transaction::Pay(PayReceipt::new(*time, *amount)));
                            self.value[*time] -= amount;
                        }
                    },
                    Command::PayAll(PayAllCommand { time }) => {
                        let amount = cash[*time];
                        if self.value[*time] < amount {
                            receipts.push(Transaction::Pay(PayReceipt::new(*time,
                                                                           self.value[*time])));
                            self.value[*time] = 0.0;
                        } else {
                            receipts.push(Transaction::Pay(PayReceipt::new(*time, amount)));
                            self.value[*time] -= amount;
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

fn minimum_repayment(loan_amount: f64, annual_interest_rate: f64, loan_years: usize) -> f64 {
    let weekly_interest_rate = annual_interest_rate / 52.0 / 100.0;
    let num_payments = loan_years * 52;
    (loan_amount * weekly_interest_rate * (1.0 + weekly_interest_rate).powf(num_payments
        as f64)) / ((1.0 + weekly_interest_rate).powf(num_payments as f64) - 1.0)
}
