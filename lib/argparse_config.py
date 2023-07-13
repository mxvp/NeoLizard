import argparse

def parse_args():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Custom pipeline for neoantigen prediction on NGS samples or TCGA MAF files.',prog="NeoLizard")
    parser.add_argument("--input",required=True,type=str,help="Path of input file/dir")
    subparsers=parser.add_subparsers(help="Operations to perform")
