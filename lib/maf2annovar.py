#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Small script to convert MAF files into text files suited for ANNOVAR.
Required flag:
    -m "maf file location"
Optional flags:
    -o "output txt file location"
    -d "debug"


Adapted from:
    @author: Christian Brueffer (ORCID: 0000-0002-3826-0989)
    Home:    https://github.com/cbrueffer/misc_bioinf/
    License: https://github.com/cbrueffer/misc_bioinf/LICENSE.md
"""

from __future__ import print_function

# MAF columns we need for the conversion
HEADER_CHROMOSOME = 'Chromosome'
HEADER_START_POS = 'Start_Position'
HEADER_END_POS = 'End_Position'
HEADER_REF_ALLELE = 'Reference_Allele'
HEADER_TUMOR_ALLELE_1 = 'Tumor_Seq_Allele1'
HEADER_TUMOR_ALLELE_2 = 'Tumor_Seq_Allele2'


def get_cols(header):
    """Returns the column indexes for the columns we are interested in."""
    try:
        col_chrom = header.index(HEADER_CHROMOSOME)
        col_start = header.index(HEADER_START_POS)
        col_end = header.index(HEADER_END_POS)
        col_ref = header.index(HEADER_REF_ALLELE)
        col_t1 = header.index(HEADER_TUMOR_ALLELE_1)
        col_t2 = header.index(HEADER_TUMOR_ALLELE_2)
    except ValueError as e:
        raise ValueError("cannot find required MAF column: %s" % str(e))

    return(col_chrom, col_start, col_end, col_ref, col_t1, col_t2)


def maf_to_annovar(maf_file, sep="\t"):
    """Converts a given file in MAF format (e.g., from TCGA) into a format
    suitable for Annovar.
    """
    try:
        outfile=open(args.output[:-4]+'.avinput','w')
    except:
        outfile=open(maf_file[:-4]+'.avinput','w')

    with open(maf_file, "r") as maf:
        header = None
        for line in maf:
            if line.startswith("#"):
                continue

            items = line.split(sep)
            if not header:
                header = items
                try:
                    col_chrom, col_start, col_end, col_ref, col_t1, col_t2 = get_cols(header)
                    continue
                except:
                    raise

            # check which allele is the variant one
            if items[col_ref] == items[col_t1]:
                var_allele = col_t2
            else:
                var_allele = col_t1

            annovar_line = "\t".join([items[col_chrom], items[col_start],
                                      items[col_end], items[col_ref], items[var_allele],'\n'])

            outfile.write(annovar_line)
    outfile.close()


if __name__ == "__main__":
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description='Convert a MAF file to .avinput file suited for ANNOVAR input.')
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Enable debug output")
    parser.add_argument("-m", "--maf_file", required=True,
                        help="File in MAF format")
    parser.add_argument("-o","--output",
                        help="Add output location")
    args = parser.parse_args()

    if not os.path.exists(args.maf_file) or not os.path.isfile(args.maf_file):
        print("Input MAF file cannot be read: %s" % args.maf_file,
              file=sys.stderr)
        sys.exit(1)

    try:
        maf_to_annovar(args.maf_file)
    except KeyboardInterrupt:
        print("Program interrupted by user, exiting.")
    except Exception as e:
        if args.debug:
            import traceback
            print(traceback.format_exc())

        print('Error:', str(e), file=sys.stderr)
