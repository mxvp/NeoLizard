# Have to use prefixes for subarguments, namespace conflicts will happen even if using groups
# change args.input in main() after every operation to location necessary for next

# By default, argparse will assume that any argument that starts with a hyphen (-) is an option or flag, and any argument that doesn't start with a hyphen is a positional argument. This means that as long as the arguments provided after the positional argument(s) don't start with a hyphen, argparse will interpret them as values for that positional argument.
# nargs: multiple values are passed (added to list), "" hyphens work to capture as one value


import argparse

def parse_the_args():
    parser = argparse.ArgumentParser(description='Custom pipeline for neoantigen prediction on NGS samples or TCGA MAF files.',prog="NeoLizard")
    parser.add_argument('--input', type=str, required=True, help='Input file(s) path')
    parser.add_argument('--qc', action='store_true', help='perform QC')
    parser.add_argument('--m2a', action='store_true', help='Convert MAF to AVINPUT')

    # Example argument group
    cutadapt_parser = parser.add_argument_group('cutadapt', 'Optional argument: cutadapt')
    cutadapt_parser.add_argument('--cutadapt', action='store_true', help='Enable cutadapt')
    cutadapt_parser.add_argument('--cutadapt_trimlength', type=int, help='Subargument for cutadapt: trimlength')
    cutadapt_parser.add_argument('--cutadapt_trimlength2', type=int, help='Subargument for cutadapt: trimlength2')

    # Example nargs
    parser.add_argument('--command', nargs='+', help='Command argument')

    # Parse the arguments
    args = parser.parse_args()

    return args

