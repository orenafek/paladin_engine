import argparse
import csv
import traceback

import InteractiveGraph.interactive_graph
from engine.engine import PaLaDiNEngine
from interactive_debugger import interactive_debugger
from source_provider import SourceProvider


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Input .py file to PaLaDiNize')
    run_group = parser.add_mutually_exclusive_group(required=True)
    run_group.add_argument('--run', default=True, dest='run', action='store_true', help='Should run PaLaDiNized file')
    run_group.add_argument('--no-run', default=False, dest='run', action='store_false',
                           help='Should run PaLaDiNized file')
    parser.add_argument('--print-code', default=False, dest='print_code', action='store',
                        help='Should print PaLaDiNized code to the screen')
    parser.add_argument('--output-file', type=str, default='', help='Output file path of the PaLaDiNized code')
    parser.add_argument('--csv', default='', type=str, help='Should output archive results to a csv file')
    parser.add_argument('--static-graph-file-name', default='', type=str,
                        help='A path to print the runtime static graph image into.')
    args = parser.parse_args()

    if args.csv != '' and not args.run:
        parser.error('--csv can\'t be passed when --no-run is passed.')

    return args


def main():
    args = parse_args()

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

        # noinspection PyBroadException
        try:
            if args.run:
                result, archive = PaLaDiNEngine.execute_with_paladin(paladinized_code, args.input_file)

            # handle_run_exceptions(archive, result)

        except:  # Plot a graph.
            pass
        finally:
            d: dict = archive.records
            di = [(k, v[0::max(len(v), 3)]) for k, v in d.items()]
            archive.records = dict(di)
            ig = InteractiveGraph.interactive_graph.InteractiveGraph(archive)
            igi = InteractiveGraph.interactive_graph.InteractiveGraph.GraphIterator(ig)

            ig.create_reset_button_callback(igi)
            ig.create_tap_node_data_callback(igi)

            if args.static_graph_file_name:
                # ig.print_static_graph(args.static_graph_file_name)
                try:
                    ig.run()
                except KeyboardInterrupt:
                    pass
            if args.csv != '':
                print('Creating CSV')
                with open(args.csv, 'w+') as fo:
                    writer = csv.writer(fo)
                    header, rows = archive.to_table()
                    writer.writerow(header)
                    writer.writerows(rows)


def handle_run_exceptions(archive, result):
    if isinstance(result, tuple) and issubclass(result[0], BaseException):

        exception_type, exception, tb = result
        # Extract the frame in which the exception was thrown.
        for frame_summary in reversed(traceback.extract_tb(tb)):
            if any([_ for _ in PaLaDiNEngine.PALADIN_STUBS_LIST if _ == frame_summary.name]) or \
                    'stubs.py' in frame_summary.filename:
                # Skip inner functions.
                continue

            exception_line_no = frame_summary.lineno
            break

        # Match original line no.
        original_line_no = SourceProvider.get_line_no(frame_summary.line)
        debugger = \
            interactive_debugger.InteractiveDebugger(archive,
                                                     f"Exception in {frame_summary.name}: {10}",
                                                     10)
        debugger.cmdloop()


if __name__ == '__main__':
    main()
