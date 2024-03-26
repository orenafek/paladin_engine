import argparse
import csv
import traceback
from pathlib import *

from PaladinUI.paladin_server.paladin_server import PaladinServer
from archive.archive import Archive
from engine.engine import PaLaDiNEngine


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Input .py file to PaLaDiNize')
    mux_group = parser.add_mutually_exclusive_group()
    mux_group.add_argument('-d', '--defaults', action='store_true',
                           help='Use defaults for output and csv files')
    details_group = mux_group.add_argument_group()
    run_group = details_group.add_argument_group()
    run_group.add_argument('--run', default=True, dest='run', action='store_true', help='Should run PaLaDiNized file')
    run_group.add_argument('-to', '--timeout', type=int, nargs='?', action='store', default=-1,
                           help='Add timeout to the program in seconds')
    details_group.add_argument('--print-code', default=False, dest='print_code', action='store',
                               help='Should print PaLaDiNized code to the screen')
    details_group.add_argument('--output-file', type=str, default='', help='Output file path of the PaLaDiNized code')
    details_group.add_argument('--csv', default='', type=str, help='Should output archive results to a csv file')
    details_group.add_argument('--run-debug-server', default=True, dest='run_debug_server', action='store',
                               help='Should run PaLaDiN-Debug server')
    details_group.add_argument('-p', '--port', default=9999, type=int,
                               help='The port no of the server in which the dynamic graph runs on')
    args = parser.parse_args()

    if args.csv != '' and not args.run:
        parser.error('--csv can\'t be passed when --no-run is passed.')

    return args


# noinspection PyBroadException
def fill_defaults(args):
    input_file = Path(args.input_file).absolute()
    output_file = input_file.parent / Path(input_file.stem + '_output.py')
    csv_file = input_file.parent / input_file.with_suffix('.csv')

    args.output_file = output_file
    args.csv_file = csv_file

    return args


def main():
    args = parse_args()


    if args.defaults:
        args = fill_defaults(args)

        engine = PaLaDiNEngine(args.input_file, args.timeout, record=args.run)

        if args.print_code:
            print(engine.paladinized_code)

        if args.output_file != '':
            engine.write_paladinized(args.output_file)

        # noinspection PyBroadException
        try:
            if args.run:
                engine.execute_with_paladin()

        except BaseException:
            traceback.print_exc()

        finally:
            if args.run_debug_server:
                try:
                    server = PaladinServer.create(engine)
                    server.run(args.port)
                except KeyboardInterrupt:
                    pass
                except BaseException:
                    traceback.print_exc()
            if args.csv != '':
                if engine.run_data.archive:
                    print('Creating CSV')
                    dump_to_csv(engine.run_data.archive, args.csv)


def dump_to_csv(archive: Archive, csv_file_path: str) -> None:
    with open(csv_file_path, 'w+') as fo:
        writer = csv.writer(fo)
        header, rows = archive.to_table()
        writer.writerow(header)
        writer.writerows(rows)


if __name__ == '__main__':
    main()
