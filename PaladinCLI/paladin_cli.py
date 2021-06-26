import argparse
import csv

from engine.engine import PaLaDiNEngine
from stubs.stubs import archive


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Input .py file to PaLaDiNize')
    parser.add_argument('--run', type=bool, default=True, help='Should run PaLaDiNized file')
    parser.add_argument('--print-code', default=False, type=bool, help='Should print PaLaDiNized code to the screen')
    parser.add_argument('--output-file', type=str, default='', help='Output file path of the PaLaDiNized code')
    parser.add_argument('--csv', default='', type=str, help='Should output archive results to a csv file')

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.file, 'r') as f:
        source_code = f.read()
        paladinized_code = PaLaDiNEngine.transform(source_code)

        if args.print_code:
            print(paladinized_code)

        if args.output_file != '':
            with open(args.output_file) as fo:
                fo.write(paladinized_code)

        if args.run:
            PaLaDiNEngine.execute_with_paladin(source_code, args.file)

        if args.csv != '':
            with open(args.csv, 'wb+') as fo:
                writer = csv.writer(fo)
                header, rows = archive.to_table()
                writer.writerow(header)
                writer.writerows(rows)


if __name__ == '__main__':
    main()
