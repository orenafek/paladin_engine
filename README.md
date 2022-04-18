# PaLaDiN Engine
The engine for PaLaDin assertions programming langague

## PaLaDiN CLI && Debug server
In order to run PaLaDiN, run `run_paladin.sh` from project root.
If `--run` option was given to Paladin-CLI, a web server should be opened in 
`http://localhost:<port>`. 
**For Current debug page, goto: `http://localhost:<port>/debug`**

### Usage:
```
paladin_cli.py [-h] (--run | --no-run) [--print-code PRINT_CODE] [--output-file OUTPUT_FILE] [--csv CSV] [--run-debug-server RUN_DEBUG_SERVER] [--port PORT] input_file

positional arguments:
  input_file            Input .py file to PaLaDiNize

optional arguments:
  -h, --help            show this help message and exit
  --run                 Should run PaLaDiNized file
  --no-run              Should not run PaLaDiNized file
  --print-code PRINT_CODE
                        Should print PaLaDiNized code to the screen
  --output-file OUTPUT_FILE
                        Output file path of the PaLaDiNized code
  --csv CSV             Should output archive results to a csv file
  --run-debug-server RUN_DEBUG_SERVER
                        Should run PaLaDiN-Debug server
  --port PORT           The port no of the server in which the dynamic graph runs on.
```