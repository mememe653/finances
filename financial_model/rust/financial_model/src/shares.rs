use std::fs;
use std::collections::{HashMap, VecDeque};

struct BuyCommand {
    time: usize,
    amount: f64,
}

impl BuyCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
            amount: fields[2].parse::<f64>().unwrap(),
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
    Buy(BuyCommand),
    Sell(SellCommand),
}

impl Command {
    fn new(input_line: &str) -> Result<Self, &str> {
        let fields: Vec<&str> = input_line.split_whitespace()
                                            .collect();
        match fields[1] {
            "BUY" => Ok(Self::Buy(BuyCommand::new(fields))),
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
            Command::Buy(BuyCommand { time, .. }) => {
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

//TODO:Have single source of truth for NUM_TIMESTEPS
const NUM_TIMESTEPS: usize = 35 * 52;

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

//TODO:Implement Transaction
pub struct Transaction {}

struct Share {
    initial_value: f64,
    capital_gains: f64,
    weeks_held: usize,
}

impl Share {
    fn new(initial_value: f64) -> Self {
        Self {
            initial_value,
            capital_gains: 0.0,
            weeks_held: 0,
        }
    }

    fn simulate_timestep(&mut self, params: &Params) {
        let weekly_ror = annual_to_weekly_ror(&params.annual_ror);
        self.weeks_held += 1;
        self.capital_gains += (self.initial_value + self.capital_gains) * weekly_ror / 100.0;
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

    pub fn simulate_timestep(&mut self, time: usize, params: Params, commands: &HashMap<usize, Vec<Command>>) -> Option<Transaction> {
        self.shares.iter_mut()
                    .for_each(|share| share.simulate_timestep(&params));
        self.value[time] = self.shares.iter()
                                    .map(|share| share.initial_value + share.capital_gains)
                                    .sum();
        //TODO:Implement receipt
        let mut receipt = None;
        if let Some(commands_vec) = commands.get(&time) {
            for command in commands_vec {
                match command {
                    Command::Buy(BuyCommand { amount, .. }) => {
                        self.shares.push_back(Share::new(*amount));
                    },
                    Command::Sell(SellCommand { time, amount }) => {
                        let mut remaining_amount = amount.clone();
                        while remaining_amount > 0.0 {
                            let share_value = self.shares[0].initial_value +
                                                self.shares[0].capital_gains;
                            if remaining_amount < share_value {
                                self.shares[0].initial_value *= (share_value -
                                                                 remaining_amount) /
                                                                share_value;
                                self.shares[0].capital_gains *= (share_value -
                                                                 remaining_amount) /
                                                                share_value;
                                remaining_amount = 0.0;
                            } else {
                                remaining_amount -= self.shares[0].initial_value +
                                                    self.shares[0].capital_gains;
                                self.shares.pop_front();
                            }
                        }
                    },
                }
            }
        }
        receipt
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
