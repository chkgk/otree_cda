import csv
import os
import sys

def split(input_path, output_path):
    with open(input_path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        first_line = next(reader)
        code, table_names = first_line[0], first_line[1:]

        content = f.read()
        tables = content.split(f"{code}\n")

        for table_name, table in zip(table_names, tables):
            filename = f'{table_name}.csv'
            with open(os.path.join(output_path, filename), 'w') as f:
                f.write(table)

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    split(input_file, output_dir)