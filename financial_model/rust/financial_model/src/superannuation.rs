use std::fs;
use std::collections::{HashMap, VecDeque};

use super::NUM_TIMESTEPS as NUM_TIMESTEPS;

struct BuyCommand {
    time: usize,
    amount: f64,
}

impl BuyCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[3].parse::<f64>().unwrap(),
        }
    }
}

struct BuyAllCommand {
    time: usize,
}

impl BuyAllCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
        }
    }
}

struct SellCommand {
    time: usize,
    amount: f64,
}

impl SellCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[2].parse::<f64>().unwrap(),
        }
    }
}

pub enum Command {
    BuySG(BuyCommand),
    BuyCC(BuyCommand),
    BuyAllCC(BuyAllCommand),
    BuyNCC(BuyCommand),
    BuyAllNCC(BuyAllCommand),
    Sell(SellCommand),
}

impl Command {
    fn new(input_line: &str) -> Result<Self, &str> {
        let fields: Vec<&str> = input_line.split_whitespace()
                                            .collect();
        match fields[1] {
            "BUY" => {
                match fields[2] {
                    "SG" => Ok(Self::BuySG(BuyCommand::new(fields))),
                    "CC" => {
                        match fields[3] {
                            "ALL" => Ok(Self::BuyAllCC(BuyAllCommand::new(fields))),
                            _ => Ok(Self::BuyCC(BuyCommand::new(fields))),
                        }
                    },
                    "NCC" => {
                        match fields[3] {
                            "ALL" => Ok(Self::BuyAllNCC(BuyAllCommand::new(fields))),
                            _ => Ok(Self::BuyNCC(BuyCommand::new(fields))),
                        }
                    },
                    _ => Err("Failed to parse command"),
                }
            },
            "SELL" => Ok(Self::Sell(SellCommand::new(fields))),
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
            Command::BuySG(BuyCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::BuyCC(BuyCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::BuyAllCC(BuyAllCommand { time }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::BuyNCC(BuyCommand { time, .. }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::BuyAllNCC(BuyAllCommand { time }) => {
                if let Some(commands_vec) = commands_map.get_mut(&time) {
                    commands_vec.push(command);
                } else {
                    commands_map.insert(time, vec![command]);
                }
            },
            Command::Sell(SellCommand { time, .. }) => {
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
    annual_ror: f64,
}

impl Params {
    pub fn new(annual_ror: f64) -> Self {
        Self {
            annual_ror,
        }
    }
}

pub struct BuyReceipt {
    pub time: usize,
    pub amount: f64,
    pub tax: f64,
}

impl BuyReceipt {
    fn new(time: usize, amount: f64, tax: f64) -> Self {
        Self {
            time,
            amount,
            tax,
        }
    }
}

pub struct SellReceipt {
    pub time: usize,
    pub taxed_amount: f64,
    pub untaxed_amount: f64,
}

impl SellReceipt {
    fn new(time: usize, taxed_amount: f64, untaxed_amount: f64) -> Self {
        Self {
            time,
            taxed_amount,
            untaxed_amount,
        }
    }
}

pub enum Transaction {
    BuySG(BuyReceipt),
    BuyCC(BuyReceipt),
    BuyNCC(BuyReceipt),
    Sell(SellReceipt),
}

struct Share {
    taxed_amount: f64,
    untaxed_amount: f64,
}

impl Share {
    fn new(initial_value: f64) -> Self {
        Self {
            taxed_amount: initial_value,
            untaxed_amount: 0.0,
        }
    }

    fn simulate_timestep(&mut self, params: &Params) {
        let weekly_ror = annual_to_weekly_ror(&params.annual_ror);
        self.untaxed_amount += (self.taxed_amount + self.untaxed_amount) * weekly_ror / 100.0;
    }
}

pub struct Asset {
    value: [f64; NUM_TIMESTEPS],
    shares: VecDeque<Share>,
}

impl Asset {
    pub fn new() -> Self {
        Self {
            value: [0.0; NUM_TIMESTEPS],
            shares: VecDeque::new(),
        }
    }

    pub fn simulate_timestep(&mut self, time: usize, params: Params, commands: &HashMap<usize, Vec<Command>>, cash: &[f64; NUM_TIMESTEPS]) -> Option<Vec<Transaction>> {
        self.shares.iter_mut()
                    .for_each(|share| share.simulate_timestep(&params));
        self.value[time] = self.shares.iter()
                                    .map(|share| share.taxed_amount + share.untaxed_amount)
                                    .sum();
        let mut receipts = Vec::<Transaction>::new();
        if let Some(commands_vec) = commands.get(&time) {
            for command in commands_vec {
                match command {
                    Command::BuySG(BuyCommand { time, amount }) => {
                        let tax = 0.15 * amount;
                        self.shares.push_back(Share::new(amount - tax));
                        receipts.push(Transaction::BuySG(BuyReceipt::new(*time, *amount, tax)));
                    },
                    Command::BuyCC(BuyCommand { time, amount }) => {
                        let tax = 0.15 * amount;
                        self.shares.push_back(Share::new(amount - tax));
                        receipts.push(Transaction::BuyCC(BuyReceipt::new(*time, *amount, tax)));
                    },
                    Command::BuyAllCC(BuyAllCommand { time }) => {
                        let amount = cash[*time];
                        let tax = 0.15 * amount;
                        self.shares.push_back(Share::new(amount - tax));
                        receipts.push(Transaction::BuyCC(BuyReceipt::new(*time, amount, tax)));
                    },
                    Command::BuyNCC(BuyCommand { time, amount }) => {
                        let tax = 0.0;
                        self.shares.push_back(Share::new(*amount));
                        receipts.push(Transaction::BuyNCC(BuyReceipt::new(*time, *amount, tax)));
                    },
                    Command::BuyAllNCC(BuyAllCommand { time }) => {
                        let amount = cash[*time];
                        let tax = 0.0;
                        self.shares.push_back(Share::new(amount));
                        receipts.push(Transaction::BuyNCC(BuyReceipt::new(*time, amount, tax)));
                    },
                    Command::Sell(SellCommand { time, amount }) => {
                        let mut remaining_amount = amount.clone();
                        while remaining_amount > 0.0 {
                            let taxed_amount = self.shares[0].taxed_amount;
                            let untaxed_amount = self.shares[0].untaxed_amount;
                            if remaining_amount < taxed_amount {
                                self.shares[0].taxed_amount -= remaining_amount;
                                receipts.push(Transaction::Sell(SellReceipt::new(*time,
                                                                            remaining_amount,
                                                                            0.0)));
                                remaining_amount = 0.0;
                            } else if remaining_amount < taxed_amount + untaxed_amount {
                                self.shares[0].taxed_amount = 0.0;
                                self.shares[0].untaxed_amount -= remaining_amount -
                                                                    taxed_amount;
                                receipts.push(Transaction::Sell(SellReceipt::new(*time,
                                                                            taxed_amount,
                                                                            remaining_amount -
                                                                            taxed_amount)));
                                remaining_amount = 0.0;
                            } else {
                                self.shares.pop_front();
                                receipts.push(Transaction::Sell(SellReceipt::new(*time,
                                                                            taxed_amount,
                                                                            untaxed_amount)));
                                remaining_amount -= taxed_amount + untaxed_amount;
                            }
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

fn annual_to_weekly_ror(annual_ror: &f64) -> f64 {
    100.0 * (((1.0 + annual_ror / 100.0).ln() / 52.0).exp() - 1.0)
}
