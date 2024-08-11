use std::fs;

use super::NUM_TIMESTEPS as NUM_TIMESTEPS;

pub fn parse_input(file_path: &str) -> [f64; NUM_TIMESTEPS] {
    let mut expenses = [0.0; NUM_TIMESTEPS];
    let input_lines = fs::read_to_string(file_path)
        .expect("Invalid file path");
    for line in input_lines.lines() {
        let fields: Vec<&str> = line.split_whitespace()
                                    .collect();
        let time: usize = fields[0].parse().unwrap();
        let amount: f64 = fields[1].parse().unwrap();
        expenses[time] += amount;
    }
    expenses
}
