use std::fs;
use std::collections::HashMap;

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
}

impl SellCommand {
    fn new(fields: Vec<&str>) -> Self {
        Self {
            time: fields[0].parse::<usize>().unwrap(),
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
            Command::Sell(SellCommand { time }) => {
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

const NUM_TIMESTEPS: usize = 35 * 52;

pub struct Asset {
    value: [f64; NUM_TIMESTEPS],
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
}

impl BuyReceipt {
    fn new(time: usize, amount: f64) -> Self {
        Self {
            time,
            amount,
        }
    }
}

pub struct SellReceipt {
    pub time: usize,
    pub amount: f64,
}

impl SellReceipt {
    fn new(time: usize, amount: f64) -> Self {
        Self {
            time,
            amount,
        }
    }
}

pub enum Transaction {
    Buy(BuyReceipt),
    Sell(SellReceipt),
}

impl Asset {
    pub fn new() -> Self {
        Self {
            value: [0.0; NUM_TIMESTEPS],
        }
    }

    pub fn simulate_timestep(&mut self, time: usize, params: Params, commands: &HashMap<usize, Vec<Command>>) -> Option<Vec<Transaction>> {
        let weekly_ror = annual_to_weekly_ror(params.annual_ror);
        //TODO:Fix bug on line below when time = 0
        self.value[time] = self.value[time - 1] * (1.0 + weekly_ror / 100.0);
        let mut receipts = Vec::<Transaction>::new();
        if let Some(commands_vec) = commands.get(&time) {
            for command in commands_vec {
                match command {
                    Command::Buy(BuyCommand { time, amount }) => {
                        self.value[*time] += amount;
                        receipts.push(Transaction::Buy(BuyReceipt::new(*time, *amount)));
                    },
                    Command::Sell(SellCommand { time }) => {
                        let amount = self.value[*time];
                        self.value[*time] = 0.0;
                        receipts.push(Transaction::Sell(SellReceipt::new(*time, amount)));
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


fn annual_to_weekly_ror(annual_ror: f64) -> f64 {
    100.0 * (((1.0 + annual_ror / 100.0).ln() / 52.0).exp() - 1.0)
}
