#!/usr/bin/env python

import csv

def combine_csv_files(input_files_pathlist, output_file):
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)

        # Loop through each input file
        for i, file_name in enumerate(input_files_pathlist):
            with open(file_name, mode='r') as infile:
                reader = csv.reader(infile)

                # Copy header from the first file, skip headers for the rest
                if i == 0:
                    header = next(reader)
                    writer.writerow(header)

                # Copy data from each file
                for row in reader:
                    writer.writerow(row)