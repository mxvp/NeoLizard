import argparse
import sys
import os
import subprocess
from lib import *
from lib.preprocessing import *


def main():

    # 1.Preprocessing

    ## A. Fastqc / multiqc reports
    QC_type='1'
    while QC_type=='1':
        QC_type=input("Create and add fastqc report (1), combine multiqc (2) or continue(3)?")
        if QC_type=='1':
            id=input("Enter ID of file in data/raw")
            output=fastqc_single(id)
            continue
        if QC_type=='2':
            folder=input("Enter folder name within reports e.g. fastqc")
            output=fastqc_multi(folder)
            print(output)
            QC_type='2'
            continue
        if QC_type=='3':
            continue
        else:
            print('unrecognized')

    ## B. 

if __name__=='__main__':
    main()