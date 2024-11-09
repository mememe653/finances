use std::fs;
use std::collections::HashMap;

use super::NUM_TIMESTEPS as NUM_TIMESTEPS;

struct StartCommand {
    time: usize,
    amount: f64,
    balloon_payment: f64,
    duration: usize,
}

impl StartCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[2].parse::<f64>().unwrap(),
            balloon_payment: fields[3].parse::<f64>().unwrap(),
            duration: fields[4].parse::<usize>().unwrap(),
        }
    }
}

pub enum Command {
    Start(StartCommand),
}

impl Command {
    fn new(input_line: &str) -> Result<Self, &str> {
        let fields: Vec<&str> = input_line.split_whitespace()
                                            .collect();
        match fields[1] {
            "START" => Ok(Self::Start(StartCommand::new(fields))),
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
    balloon_payment_value: [f64; NUM_TIMESTEPS],
    balloon_payment_time: Option<usize>,
    minimum_weekly_repayment: Option<f64>,
}

impl Asset {
    pub fn new() -> Self {
        Self {
            value: [0.0; NUM_TIMESTEPS],
            balloon_payment_value: [0.0; NUM_TIMESTEPS],
            balloon_payment_time: None,
            minimum_weekly_repayment: None,
        }
    }

    pub fn simulate_timestep(&mut self, time: usize, params: Params, commands: &HashMap<usize, Vec<Command>>) -> Option<Vec<Transaction>> {
        let weekly_interest_rate = annual_to_weekly_interest_rate(params.annual_interest_rate);
        if time > 0 {
            self.value[time] = self.value[time - 1] * (1.0 + weekly_interest_rate / 100.0);
            self.balloon_payment_value[time] = self.balloon_payment_value[time - 1] * 
                (1.0 + weekly_interest_rate / 100.0);
            let loan_value = self.value[time];
            let balloon_payment_value = self.balloon_payment_value[time];
            log::trace!("Apply interest to car loan, remaining loan is ${loan_value} at time (time)");
            log::trace!("Apply interest to car loan balloon payment, new balloon payment value is ${balloon_payment_value} at time {time}");
        }
        let mut receipts = Vec::<Transaction>::new();
        if let Some(balloon_payment_time) = self.balloon_payment_time {
            if time == balloon_payment_time {
                let amount = self.balloon_payment_value[time];
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
                self.balloon_payment_value[time] = 0.0;
                self.balloon_payment_time = None;
                log::trace!("Pay car loan balloon payment of ${amount} at time {time}");
            }
        }
        if let Some(minimum_repayment) = self.minimum_weekly_repayment {
            if self.value[time] < minimum_repayment {
                let amount = self.value[time];
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
                self.value[time] -= amount;
                self.minimum_weekly_repayment = None;
                log::trace!("Pay minimum weekly car loan repayment of ${amount} at time {time}");
            } else {
                let amount = minimum_repayment;
                receipts.push(Transaction::Pay(PayReceipt::new(time, amount)));
                self.value[time] -= amount;
                log::trace!("Pay minimum weekly car loan repayment of ${amount} at time {time}");
            }
        }
        if let Some(commands_vec) = commands.get(&time) {
            for command in commands_vec {
                match command {
                    Command::Start(StartCommand { time, amount, balloon_payment, duration }) => {
                        self.value[*time] = *amount;
                        self.balloon_payment_value[*time] = *balloon_payment;
                        self.balloon_payment_time = Some(*time + *duration * 52);
                        self.minimum_weekly_repayment = Some(minimum_repayment(*amount,
                                                            params.annual_interest_rate,
                                                            *duration));
                        log::trace!("Take out car loan worth ${amount} at time {time}");
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
            text = format!("{}{} {}\n", text, i, val + self.balloon_payment_value[i]);
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
