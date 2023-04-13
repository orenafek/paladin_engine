# PaLaDiN Engine

The engine for PaLaDin assertions programming langague

## Requirements

1. `python 3.10` or above

## Installation

### Third party tools

#### Installation on Mac-OS / Linux

1. Install `poetry`, to install PaLaDiN's Python's dependencies.
    1. Open a Terminal window and run `curl -sSL https://install.python-poetry.org | python3 -`
    2. Add poetry's binary directory to `PATH`, run:
        - On Mac-OS: `echo "export PATH=$PATH:$HOME/.local/bin" >> $HOME/.bash_profile`
        - On Linux: `echo "export PATH=$PATH:$HOME/.local/bin" >> $HOME/.bashrc`
    3. In the project's root directory, run: `poetry install`
    4. To make sure poetry has created a virtual environment with the dependencies,  
       run: `which python`. The output should be `<PROJECT_ROOT_DIR>/.venv/bin/python`


2. Install `npm`, to install PaLaDiN's fornt-end NodeJs dependencies:
    1. Install `nvm`  
       Open a Terminal window and run:
        - On Mac-OS: `brew install nvm`
        - On Linux:  `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash`
    2. Install `npm` using `nvm`:  
       Open a Terminal window and run: `nvm install node`

#### Installation on Windows

TBD

### PaLaDiN Installations

1. After installing third party tools, in the project's root directory run: `make all`

## PaLaDiN CLI && Debug server

In order to run PaLaDiN, run `run_paladin.sh` from project root.
If `--run` option was given to Paladin-CLI, a web server should be opened in
`http://localhost:<port>`.

### Usage:

```
paladin_cli.py [-h] [-d] [--run] [-to [TIMEOUT]]
                      [--print-code PRINT_CODE] [--output-file OUTPUT_FILE]
                      [--csv CSV] [--run-debug-server RUN_DEBUG_SERVER]
                      [-p PORT]
                      input_file

positional arguments:
  input_file      Input .py file to PaLaDiNize

options:
  -h, --help      show this help message and exit
  -d, --defaults  Use defaults for output and csv files

optional arguments:
  -h, --help            show this help message and exit
  --run                 Should run PaLaDiNized file
  --no-run              Should not run PaLaDiNized file
  --to TIMEOUT[s]       A timeout, in seconds, to set the run program.
  --print-code PRINT_CODE
                        Should print PaLaDiNized code to the screen
  --output-file OUTPUT_FILE
                        Output file path of the PaLaDiNized code
  --csv CSV             Should output archive results to a csv file
  --run-debug-server RUN_DEBUG_SERVER
                        Should run PaLaDiN-Debug server
  --port PORT           The port no of the server to run on.
```