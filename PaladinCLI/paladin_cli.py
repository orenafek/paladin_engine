import argparse
import csv

from engine.engine import PaLaDiNEngine

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

        try:
            if args.run:
                result, archive = PaLaDiNEngine.execute_with_paladin(paladinized_code, args.input_file)
        finally:
            if args.csv != '':
                print('Creating CSV')
                with open(args.csv, 'w+') as fo:
                    writer = csv.writer(fo)
                    header, rows = archive.to_table()
                    writer.writerow(header)
                    writer.writerows(rows)


if __name__ == '__main__':
    main()
