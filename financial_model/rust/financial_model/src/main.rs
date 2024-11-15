use std::fs;
use std::collections::HashMap;
use simple_logger::SimpleLogger;

mod home;
mod home_loan;
mod car_loan;
mod hecs;
mod shares;
mod superannuation;
mod income;
mod tax;
mod misc;

const NUM_TIMESTEPS: usize = 35 * 52 + 2;

fn main() {
    SimpleLogger::new().with_colors(true).init().unwrap();

    let params = parse_params_file("input_files/params.txt");
    let tax_brackets = parse_tax_brackets_file("input_files/tax_brackets.txt");

    let income = income::parse_input("input_files/income.txt");
    let expenses = misc::parse_input("input_files/misc.txt");

    let mut taxable_income = income;
    //TODO:Figure out why taxed_income variable is unused
    let taxed_income = tax::tax_income(income, tax_brackets, params["INFLATION_RATE"]);
    let mut fhss_taxed = [0.0; NUM_TIMESTEPS];
    let mut fhss_untaxed = [0.0; NUM_TIMESTEPS];

    let mut cash = tax::tax_income(income, tax_brackets, params["INFLATION_RATE"]);
    for (i, expense) in expenses.iter().enumerate() {
        cash[i] -= expense;
    }

    let home_commands = home::parse_input("input_files/home.txt");
    let mut home_asset = home::Asset::new();

    let home_loan_commands = home_loan::parse_input("input_files/home_loan.txt");
    let mut home_loan_asset = home_loan::Asset::new();

    let car_loan_commands = car_loan::parse_input("input_files/car_loan.txt");
    let mut car_loan_asset = car_loan::Asset::new();

    let hecs_commands = hecs::parse_input("input_files/hecs.txt");
    let mut hecs_asset = hecs::Asset::new();

    let shares_commands = shares::parse_input("input_files/shares.txt");
    let mut shares_asset = shares::Asset::new();

    let super_commands = superannuation::parse_input("input_files/super.txt");
    let mut super_asset = superannuation::Asset::new();

    for sim_time in 0..NUM_TIMESTEPS {
        if sim_time % 52 == 0 && sim_time != 0 {
            let year_taxable_income: [f64; 52] = taxable_income[(sim_time - 52) .. sim_time]
                                                    .try_into().unwrap();
            let original_income: [f64; 52] = income[(sim_time - 52) .. sim_time]
                                                    .try_into().unwrap();
            cash[sim_time] -= tax::reconcile_tax(year_taxable_income,
                                                 original_income,
                                                 tax_brackets[sim_time]);
            let year_fhss_taxed: [f64; 52] = fhss_taxed[(sim_time - 52) .. sim_time]
                                                    .try_into().unwrap();
            let year_fhss_untaxed: [f64; 52] = fhss_untaxed[(sim_time - 52) .. sim_time]
                                                    .try_into().unwrap();
            cash[sim_time] -= tax::tax_super_fhss(year_taxable_income, year_fhss_taxed, year_fhss_untaxed, tax_brackets[sim_time]);
        }

        if sim_time != 0 {
            cash[sim_time] += cash[sim_time - 1];
        }

        let home_params = home::Params::new(params["HOME_APPRECIATION_RATE"]);
        let receipts = home_asset.simulate_timestep(sim_time, home_params, &home_commands);
        if let Some(receipts_vec) = receipts {
            for receipt in receipts_vec {
                match receipt {
                    home::Transaction::Buy(home::BuyReceipt { time, amount }) => {
                        cash[time] -= amount;
                    },
                    home::Transaction::Sell(home::SellReceipt { time, amount }) => {
                        cash[time] += amount;
                    },
                }
            }
            let cash_on_hand = cash[sim_time];
            log::trace!("Cash on hand is ${cash_on_hand}");
        }

        let home_loan_params = home_loan::Params::new(params["HOME_LOAN_INTEREST_RATE"]);
        let receipts = home_loan_asset.simulate_timestep(sim_time, home_loan_params, &home_loan_commands, &cash);
        if let Some(receipts_vec) = receipts {
            for receipt in receipts_vec {
                match receipt {
                    home_loan::Transaction::Start(home_loan::StartReceipt { time, amount }) => {
                        cash[time] += amount;
                    },
                    home_loan::Transaction::Pay(home_loan::PayReceipt { time, amount }) => {
                        cash[time] -= amount;
                    },
                }
            }
            let cash_on_hand = cash[sim_time];
            log::trace!("Cash on hand is ${cash_on_hand}");
        }

        let car_loan_params = car_loan::Params::new(params["CAR_LOAN_INTEREST_RATE"]);
        let receipts = car_loan_asset.simulate_timestep(sim_time, car_loan_params, &car_loan_commands);
        if let Some(receipts_vec) = receipts {
            for receipt in receipts_vec {
                match receipt {
                    car_loan::Transaction::Pay(car_loan::PayReceipt { time, amount }) => {
                        cash[time] -= amount;
                    },
                }
            }
            let cash_on_hand = cash[sim_time];
            log::trace!("Cash on hand is ${cash_on_hand}");
        }

        let hecs_params = hecs::Params::new(params["HECS_INDEXATION_RATE"]);
        let receipts = hecs_asset.simulate_timestep(sim_time, hecs_params, &hecs_commands, &income);
        if let Some(receipts_vec) = receipts {
            for receipt in receipts_vec {
                match receipt {
                    hecs::Transaction::Pay(hecs::PayReceipt { time, amount }) => {
                        cash[time] -= amount;
                    }
                }
            }
            let cash_on_hand = cash[sim_time];
            log::trace!("Cash on hand is ${cash_on_hand}");
        }

        let shares_params = shares::Params::new(params["SHARES_ROR"]);
        let receipts = shares_asset.simulate_timestep(sim_time, shares_params, &shares_commands, &cash);
        if let Some(receipts_vec) = receipts {
            for receipt in receipts_vec {
                match receipt {
                    shares::Transaction::Buy(shares::BuyReceipt { time, amount }) => {
                        cash[time] -= amount;
                    },
                    shares::Transaction::Sell(shares::SellReceipt {
                        time,
                        amount,
                        taxable_amount,
                    }) => {
                        cash[time] += amount;
                        taxable_income[time] += taxable_amount;
                    }
                }
            }
            let cash_on_hand = cash[sim_time];
            log::trace!("Cash on hand is ${cash_on_hand}");
        }

        let super_params = superannuation::Params::new(params["SUPER_ROR"]);
        let receipts = super_asset.simulate_timestep(sim_time, super_params, &super_commands, &cash);
        if let Some(receipts_vec) = receipts {
            for receipt in receipts_vec {
                match receipt {
                    superannuation::Transaction::BuySG(superannuation::BuyReceipt { .. }) => {
                        ();
                    },
                    superannuation::Transaction::BuyCC(superannuation::BuyReceipt {
                        time,
                        amount,
                        ..
                    }) => {
                        cash[time] -= amount; 
                        taxable_income[time] -= amount;
                    },
                    superannuation::Transaction::BuyNCC(superannuation::BuyReceipt {
                        time,
                        amount,
                        ..
                    }) => {
                        cash[time] -= amount;
                    },
                    superannuation::Transaction::Sell(superannuation::SellReceipt {
                        time,
                        taxed_amount,
                        untaxed_amount,
                    }) => {
                        cash[time] += taxed_amount + untaxed_amount;
                        fhss_taxed[time] += taxed_amount;
                        fhss_untaxed[time] += untaxed_amount;
                    }
                }
            }
            let cash_on_hand = cash[sim_time];
            log::trace!("Cash on hand is ${cash_on_hand}");
        }
    }

    home_asset.write_to_file("output_files/home.txt");
    home_loan_asset.write_to_file("output_files/home_loan.txt");
    car_loan_asset.write_to_file("output_files/car_loan.txt");
    hecs_asset.write_to_file("output_files/hecs.txt");
    shares_asset.write_to_file("output_files/shares.txt");
    super_asset.write_to_file("output_files/super.txt");

    write_cash_to_file(cash, "output_files/cash.txt");
}

fn write_cash_to_file(cash: [f64; NUM_TIMESTEPS], filepath: &str) {
    let mut text: String = "".into();
    for (i, val) in cash.iter().enumerate() {
        text = format!("{}{} {}\n", text, i, val);
    }
    fs::write(filepath, text).expect("Unable to write output file");
}

fn parse_params_file(file_path: &str) -> HashMap<String, f64> {
    let input_lines = fs::read_to_string(file_path)
        .expect("Invalid file path");
    let mut params: HashMap<String, f64> = HashMap::new();
    for line in input_lines.lines() {
        let fields: Vec<&str> = line.split_whitespace()
                                    .collect();
        let key = fields[0];
        let val = fields[1].parse::<f64>().unwrap();
        params.insert(key.to_string(), val);
    }
    params
}

fn parse_tax_brackets_file(file_path: &str) -> [[f64; 4]; NUM_TIMESTEPS] {
    let input_lines = fs::read_to_string(file_path)
        .expect("Invalid file path");
    let mut tax_brackets_list = [[0.0; 4]; NUM_TIMESTEPS];
    for (time, line) in input_lines.lines().enumerate() {
        let tax_brackets: Vec<&str> = line.split_whitespace()
                                            .collect();
        //tax_brackets_list[time] = line.iter()
                                        //.map(|bracket| bracket.parse::<f64>().unwrap())
                                        //.collect();
        tax_brackets_list[time] = [tax_brackets[0].parse::<f64>().unwrap(),
                                    tax_brackets[1].parse::<f64>().unwrap(),
                                    tax_brackets[2].parse::<f64>().unwrap(),
                                    tax_brackets[3].parse::<f64>().unwrap()]
    }
    tax_brackets_list
}
