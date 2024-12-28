<h1 align="center" style="border-bottom: none">
    <a href="https://prometheus.io" target="_blank"><img alt="Prometheus" src="./.assets/heading-icon.svg"></a><br>Blindfold Chess
</h1>

> A `Python` project designed to explore the randomness of chess and all of its funky implications. This project is part of my _writings_ which you can take a look at here!

- [Prerequisites](https://github.com/adithya-r-01/blindfold-chess/tree/main?tab=readme-ov-file#prerequisites)
- [Running The Simulation](https://github.com/adithya-r-01/blindfold-chess/tree/main?tab=readme-ov-file#running-the-simulation)
- [Analyzing Results](https://github.com/adithya-r-01/blindfold-chess/tree/main?tab=readme-ov-file#analyzing-the-results)

## Prerequisites

This project relies on `Python3` which is the only firm prerequisite in order to run this simulation. Start by cloning the repository and enter the root directory:

```shell
git clone https://github.com/adithya-r-01/blindfold-chess
cd blindfold-chess
```
The recommended way of gathering all the requirements for this package is by generating a `venv` and installing the dependencies using the `requirements.txt`:

```shell
virtualenv chess
source chess/bin/activate
pip install -r requirements.txt
```
In order to leverage the full functionality of the simulation with a chess engine (e.g. Stockfish) download the executable. If you are using `brew` you can use:

```shell
brew install stockfish 
```

## Running The Simulation

The main script for the simulation is `simulation.py` however before you can run the script you will need to setup a couple parameters in the `config.yaml` file:

```yaml
threads: 2 # Number of threads to run the simulation on
engine: /opt/stockfish # Path to the engine executable (optional)
output: out # Output directory
```
The only strictly required parameter is `engine` if you are running the simulation with an engine - otherwise threads and output default to `1` and `out` respectively.

In order to run the simulation use `python3 simulation.py`, the parameters are:

- `-h` or `--help`: Display the _help_ message with information about the parameters.
- `--verbosity`: Controls the verbosity (defaults to False).
- `--simulations`: Number of simulations to run (defaults to 100).
-  `--opponent`: Accepts 'Random' or 'Engine' (defaults to Random).

And that's basically it! Info and debug logs will appear based on the `--verbosity` level. The `output` directory defined in the `config.yaml` file will populate with the simulation results.

## Analyzing Results

> [!TIP]
> This part is where you let _your_ creativity shine through. Use the existing code as a template for visualizations and analysis.

The `analysis.py` file contains various analysis and visualization components. Simply use `python3 analysis.py` to run the analysis. Visualizations will also appear in the `output` directory defined in the `config.yaml`.

To define which folder to analyze use the required `--read` parameter with the correct folder name.
