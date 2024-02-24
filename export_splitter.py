import csv

with open('export_test/custom_export.csv', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    first_line = next(reader)
    code, table_names = first_line[0], first_line[1:]

    content = f.read()
    tables = content.split(f"{code}\n")

    for table_name, table in zip(table_names, tables):
        with open(f'{table_name}.csv', 'w') as f:
            f.write(table)
