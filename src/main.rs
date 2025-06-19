mod cli;
use anyhow::Result;
use clap::Command;

const AUTOPLY_VERSION: Option<&str> = option_env!("CARGO_PKG_VERSION");

fn main() -> Result<()> {
    let command = Command::new("autoply")
        .version(AUTOPLY_VERSION.unwrap_or("unknown"))
        .about("Autoply - A tool for automating job applications")
        .subcommand_required(true)
        .arg_required_else_help(true)
        .subcommands([cli::setup::run()]);

    let matches = command.get_matches();
    match matches.subcommand() {
        Some((cli::RUN, matches)) => cli::run::run(matches)?,
        _ => unreachable!(),
    }

    Ok(())
}
