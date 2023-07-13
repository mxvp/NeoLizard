#!/usr/bin/env python

import argparse
from lib.preprocessing import *
from lib.lizard import print_lizard


def parse_args():
    parser=argparse.ArgumentParser(description="Custom pipeline for neoantigen prediction on NGS samples or TCGA MAF files.")
    parser.add_argument("--loc",type=str,required=True,help="Path to file/directory")
    parser.add_argument("--format",type=str,required=True,choices=["fastq","sam","bam","maf","vcf"],help="Format of input file(s)")
    parser.add_argument("--multi",default=False, action="store_true",help="Enable multi-mode when input is a directory with multiple files")
    parser.add_argument("--QC",default=True, action="store_false",help="Perform quality control on input file(s)")
    args=parser.parse_args()


    return args

def main():
    inputs=parse_args()
    if inputs.format in ["fastq","sam","bam"]:
        if inputs.multi:
            fastqc_multi(inputs.loc)
            multiqc("reports/fastqc")
        else:
            fastqc_single(inputs.loc)




    print("Done!")
    return print_lizard()


if __name__=='__main__':
    main()