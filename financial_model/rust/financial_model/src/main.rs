mod home;

fn main() {
    let commands = home::parse_input("input_files/home.txt");
    let mut asset = home::Asset::new();
    let num_timesteps = 35 * 52;
    for time in 1..num_timesteps {
        let params = home::Params::new(8.0);
        asset.simulate_timestep(time, params, &commands);
    }
    asset.write_to_file("output_files/home.txt");
}
