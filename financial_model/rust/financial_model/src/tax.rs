use super::NUM_TIMESTEPS as NUM_TIMESTEPS;
//TODO:Adjust tax brackets with inflation

struct TaxBrackets {
    bracket_1: TaxBracket,
    bracket_2: TaxBracket,
    bracket_3: TaxBracket,
    bracket_4: TaxBracket,
    bracket_5: TaxBracket,
}

impl TaxBrackets {
    fn new(taxable_income: f64, tax_rates: [f64; 5]) -> Self {
        let tax_brackets = [18200.0, 45000.0, 135000.0, 190000.0];
        //let tax_rates = [0.0, 16.0, 30.0, 37.0, 45.0];

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

    pub fn compute_tax(taxable_income: f64, tax_rates: [f64; 5]) -> f64 {
        let tax_brackets = Self::new(taxable_income, tax_rates);
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

pub fn reconcile_tax(taxable_income: [f64; 52], original_income: [f64; 52]) -> f64 {
    //TODO:Have single source of truth for tax rates
    let tax_rates = [0.0, 16.0, 30.0, 37.0, 45.0];
    let year_taxable_income = taxable_income.into_iter().sum();
    let tax = TaxBrackets::compute_tax(year_taxable_income, tax_rates);
    let year_original_income = original_income.into_iter().sum();
    let tax_withheld = TaxBrackets::compute_tax(year_original_income, tax_rates);
    tax - tax_withheld
}

pub fn tax_income(taxable_income: [f64; NUM_TIMESTEPS]) -> [f64; NUM_TIMESTEPS] {
    let tax_rates = [0.0, 16.0, 30.0, 37.0, 45.0];
    let yearly_taxable_income = weekly_to_yearly_taxable_income(&taxable_income);
    let yearly_tax: Vec<f64> = yearly_taxable_income.iter()
                                            .map(|income| TaxBrackets::compute_tax(*income,
                                                                                   tax_rates))
                                            .collect();
    let mut taxed_income = [0.0; NUM_TIMESTEPS];
    for time in 0..NUM_TIMESTEPS {
        let tax = yearly_tax[time / 52] / 52.0;
        taxed_income[time] += taxable_income[time] - tax;
    }
    taxed_income
}

pub fn tax_super_fhss(taxable_income: [f64; 52], super_taxed_amount: [f64; 52], super_untaxed_amount: [f64; 52]) -> f64 {
    let year_super_taxed_amount: f64 = super_taxed_amount.into_iter().sum();
    let year_super_untaxed_amount: f64 = super_untaxed_amount.into_iter().sum();
    let tax = 0.15 * year_super_untaxed_amount;

    let tax_rates = [0.0, 16.0, 30.0, 37.0, 45.0];
    let mut adjusted_tax_rates = [0.0; 5];
    for (i, tax_rate) in tax_rates.iter().enumerate() {
        let adjusted_rate = tax_rate - 30.0;
        if adjusted_rate > 0.0 {
            adjusted_tax_rates[i] = adjusted_rate;
        } else {
            adjusted_tax_rates[i] = 0.0;
        }
    }
    let year_taxable_income = taxable_income.into_iter().sum();
    let tax_1 = TaxBrackets::compute_tax(year_taxable_income, adjusted_tax_rates);
    let year_super_amount = year_super_taxed_amount + year_super_untaxed_amount - tax;
    let tax_2 = TaxBrackets::compute_tax(year_taxable_income + year_super_amount, adjusted_tax_rates);
    tax + tax_2 - tax_1
}

fn weekly_to_yearly_taxable_income(weekly_taxable_income: &[f64; NUM_TIMESTEPS]) -> [f64; (NUM_TIMESTEPS - 1) / 52 + 1] {
    let mut yearly_taxable_income  = [0.0; (NUM_TIMESTEPS - 1) / 52 + 1];
    for (i, taxable_income) in weekly_taxable_income.iter().enumerate() {
        yearly_taxable_income[i / 52] += taxable_income;
    }
    yearly_taxable_income
}
