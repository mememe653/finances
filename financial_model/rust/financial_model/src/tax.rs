use super::NUM_TIMESTEPS as NUM_TIMESTEPS;

const TAX_RATES: [f64; 5] = [0.0, 16.0, 30.0, 37.0, 45.0];

struct TaxBrackets {
    bracket_1: TaxBracket,
    bracket_2: TaxBracket,
    bracket_3: TaxBracket,
    bracket_4: TaxBracket,
    bracket_5: TaxBracket,
}

impl TaxBrackets {
    fn new(taxable_income: f64, tax_rates: [f64; 5], tax_brackets: [f64; 4]) -> Self {
        let bracket_1 = TaxBracket::new(taxable_income, 0.0, tax_brackets[0], tax_rates[0]);
        let bracket_2 = TaxBracket::new(taxable_income, tax_brackets[0], tax_brackets[1],
                                        tax_rates[1]);
        let bracket_3 = TaxBracket::new(taxable_income, tax_brackets[1], tax_brackets[2],
                                        tax_rates[2]);
        let bracket_4 = TaxBracket::new(taxable_income, tax_brackets[2], tax_brackets[3],
                                        tax_rates[3]);
        let bracket_5 = TaxBracket::new(taxable_income, tax_brackets[3], f64::MAX,
                                        tax_rates[4]);

        Self {
            bracket_1,
            bracket_2,
            bracket_3,
            bracket_4,
            bracket_5,
        }
    }

    pub fn compute_tax(taxable_income: f64, tax_rates: [f64; 5], tax_brackets: [f64; 4]) -> f64 {
        let tax_brackets = Self::new(taxable_income, tax_rates, tax_brackets);
        let mut tax = 0.0;
        tax += tax_brackets.bracket_1.amount * tax_brackets.bracket_1.tax_rate / 100.0;
        tax += tax_brackets.bracket_2.amount * tax_brackets.bracket_2.tax_rate / 100.0;
        tax += tax_brackets.bracket_3.amount * tax_brackets.bracket_3.tax_rate / 100.0;
        tax += tax_brackets.bracket_4.amount * tax_brackets.bracket_4.tax_rate / 100.0;
        tax += tax_brackets.bracket_5.amount * tax_brackets.bracket_5.tax_rate / 100.0;
        tax
    }
}

struct TaxBracket {
    amount: f64,
    lower_bound: f64,
    upper_bound: f64,
    tax_rate: f64,
}

impl TaxBracket {
    pub fn new(taxable_income: f64, lower_bound: f64, upper_bound: f64, tax_rate: f64) -> Self {
        if taxable_income < lower_bound {
            Self {
                amount: 0.0,
                lower_bound,
                upper_bound,
                tax_rate
            }
        } else if taxable_income < upper_bound {
            Self {
                amount: taxable_income - lower_bound,
                lower_bound,
                upper_bound,
                tax_rate
            }
        } else {
            Self {
                amount: upper_bound - lower_bound,
                lower_bound,
                upper_bound,
                tax_rate
            }
        }
    }
}

pub fn reconcile_tax(taxable_income: [f64; 52], original_income: [f64; 52], tax_brackets: [f64; 4]) -> f64 {
    let year_taxable_income = taxable_income.into_iter().sum();
    let tax = TaxBrackets::compute_tax(year_taxable_income, TAX_RATES, tax_brackets);
    let year_original_income = original_income.into_iter().sum();
    let tax_withheld = TaxBrackets::compute_tax(year_original_income, TAX_RATES, tax_brackets);
    tax - tax_withheld
}

pub fn tax_income(taxable_income: [f64; NUM_TIMESTEPS], tax_brackets: [[f64; 4]; NUM_TIMESTEPS], annual_inflation_rate: f64) -> [f64; NUM_TIMESTEPS] {
    let yearly_taxable_income = weekly_to_yearly_taxable_income(&taxable_income);
    let mut yearly_tax_brackets: Vec<&[f64; 4]> = tax_brackets.iter()
                                            .enumerate()
                                            .filter(|&(time, _)| time % 52 == 0 && time != 0)
                                            .map(|(_, brackets)| brackets)
                                            .collect();
    yearly_tax_brackets.push(&tax_brackets[NUM_TIMESTEPS - 1]);
    let mut yearly_tax: Vec<f64> = Vec::new();
    for (time, tax_brackets) in yearly_tax_brackets.iter().enumerate() {
        yearly_tax.push(TaxBrackets::compute_tax(yearly_taxable_income[time],
                                                 TAX_RATES,
                                                 **tax_brackets));
    }
    let weekly_inflation_rate = annual_to_weekly_inflation(annual_inflation_rate);
    let mut weekly_tax = [1.0; NUM_TIMESTEPS];
    let mut weekly_tax_sum: Vec<f64> = Vec::new();
    for time in 0..NUM_TIMESTEPS {
        if time > 0 {
            weekly_tax[time] = weekly_tax[time - 1] * (1.0 + weekly_inflation_rate / 100.0);
        }
        if time % 52 == 0 {
            weekly_tax_sum.push(0.0);
        }
        let weekly_tax_sum_len = weekly_tax_sum.len();
        weekly_tax_sum[weekly_tax_sum_len - 1] += weekly_tax[time];
    }
    for time in 0..NUM_TIMESTEPS {
        weekly_tax[time] *= yearly_tax[time / 52] / weekly_tax_sum[time / 52];
    }
    let mut taxed_income = [0.0; NUM_TIMESTEPS];
    for time in 0..NUM_TIMESTEPS {
        taxed_income[time] += taxable_income[time] - weekly_tax[time];
    }
    taxed_income
}

pub fn tax_super_fhss(taxable_income: [f64; 52], super_taxed_amount: [f64; 52], super_untaxed_amount: [f64; 52], tax_brackets: [f64; 4]) -> f64 {
    let year_super_taxed_amount: f64 = super_taxed_amount.into_iter().sum();
    let year_super_untaxed_amount: f64 = super_untaxed_amount.into_iter().sum();
    let tax = 0.15 * year_super_untaxed_amount;

    let mut adjusted_tax_rates = [0.0; 5];
    for (i, tax_rate) in TAX_RATES.iter().enumerate() {
        let adjusted_rate = tax_rate - 30.0;
        if adjusted_rate > 0.0 {
            adjusted_tax_rates[i] = adjusted_rate;
        } else {
            adjusted_tax_rates[i] = 0.0;
        }
    }
    let year_taxable_income = taxable_income.into_iter().sum();
    let tax_1 = TaxBrackets::compute_tax(year_taxable_income, adjusted_tax_rates, tax_brackets);
    let year_super_amount = year_super_taxed_amount + year_super_untaxed_amount - tax;
    let tax_2 = TaxBrackets::compute_tax(year_taxable_income + year_super_amount, adjusted_tax_rates, tax_brackets);
    tax + tax_2 - tax_1
}

fn weekly_to_yearly_taxable_income(weekly_taxable_income: &[f64; NUM_TIMESTEPS]) -> [f64; (NUM_TIMESTEPS - 1) / 52 + 1] {
    let mut yearly_taxable_income  = [0.0; (NUM_TIMESTEPS - 1) / 52 + 1];
    for (i, taxable_income) in weekly_taxable_income.iter().enumerate() {
        yearly_taxable_income[i / 52] += taxable_income;
    }
    yearly_taxable_income
}

fn annual_to_weekly_inflation(annual_inflation_rate: f64) -> f64 {
    100.0 * (((1.0 + annual_inflation_rate / 100.0).ln() / 52.0).exp() - 1.0)
}
