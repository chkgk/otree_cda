I use a custom file format to export both trades and orders through otree's custom export function
To split the files, use the export_splitter.py script.
It will take the custom export file from otree as the first argument and an output dir as the second argument.

Example:
python export_splitter.py .\raw\cda_rep1_custom_2024-03-19.csv .\custom_exports_split\

This splits the custom export file cda_rep1_custom_2024-03-19.csv into two files Trade_1.csv and Order_1.csv in custom_exports_split.

The number indicates the repetition of the market.
0 = practice period
1 = first repetition
2 = second repetition