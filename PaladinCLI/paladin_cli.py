import argparse
import csv
import traceback

from PaladinCLI.interactive_graph.paladin_debug_server import PaladinDebugServer
from archive.archive import Archive
from engine.engine import PaLaDiNEngine


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Input .py file to PaLaDiNize')
    run_group = parser.add_mutually_exclusive_group(required=True)
    run_group.add_argument('--run', default=True, dest='run', action='store_true', help='Should run PaLaDiNized file')
    run_group.add_argument('--no-run', default=False, dest='run', action='store_false',
                           help='Should not run PaLaDiNized file')
    parser.add_argument('--print-code', default=False, dest='print_code', action='store',
                        help='Should print PaLaDiNized code to the screen')
    parser.add_argument('--output-file', type=str, default='', help='Output file path of the PaLaDiNized code')
    parser.add_argument('--csv', default='', type=str, help='Should output archive results to a csv file')
    parser.add_argument('--run-debug-server', default=False, dest='run_debug_server', action='store',
                        help='Should run PaLaDiN-Debug server')
    parser.add_argument('--port', default=9999, type=int,
                        help='The port no of the server in which the dynamic graph runs on.')
    args = parser.parse_args()

    if args.csv != '' and not args.run:
        parser.error('--csv can\'t be passed when --no-run is passed.')

    return args


# noinspection PyBroadException
def main():
    args = parse_args()
    archive = None
    thrown_exception = None
    with open(args.input_file, 'r') as f:
        source_code = f.read()
        paladinized_code = PaLaDiNEngine.transform(source_code)

        if args.print_code:
            print(paladinized_code)

        if args.output_file != '':
            with open(args.output_file, 'w+') as fo:
                fo.write(PaLaDiNEngine.import_line('stubs.stubs'))
                fo.writelines('\n' * 3)
                fo.write(paladinized_code)

        try:
            if args.run:
                result, archive, thrown_exception = PaLaDiNEngine.execute_with_paladin(source_code,
                                                                                       paladinized_code,
                                                                                       args.input_file)
                print(result)

        except BaseException:  # Plot a graph.
            traceback.print_exc()

        finally:
            if args.run_debug_server:
                try:
                    server = PaladinDebugServer.create(source_code, archive, thrown_exception)
                    server.run(args.port)
                except KeyboardInterrupt:
                    pass
                except BaseException:
                    traceback.print_exc()
            if args.csv != '':
                print('Creating CSV')
                dump_to_csv(archive, args.csv)


def dump_to_csv(archive: Archive, csv_file_path: str) -> None:
    with open(csv_file_path, 'w+') as fo:
        writer = csv.writer(fo)
        header, rows = archive.to_table()
        writer.writerow(header)
        writer.writerows(rows)


if __name__ == '__main__':
    main()
