#!/usr/bin/env python
import os
from lib.argparse_config import parse_the_args
from lib.qc import perform_qc
from lib.cutadapt import perform_cutadapt
from lib.lizard import print_lizard
from lib.m2a import convert_maf_to_avinput
from lib.annovar_functions import perform_annovar
from lib.cropping_flanks import perform_cropping_fastas
from lib.MHCflurry_prediction import perform_mhcflurry


def main():
    args = parse_the_args()
    os.makedirs(args.output, exist_ok=True) # Create output folder if it doesn't exist
    if args.qc:
        perform_qc(args.input, args.output)
    if args.cutadapt:
        perform_cutadapt(
            args.input, args.output, args.cutadapt_commands, args.cutadapt_remove
        )
        args.input = os.path.join(args.output, "Processed")
    if args.m2a:
        convert_maf_to_avinput(args.input, args.output)
        args.input = os.path.join(args.output, "avinput_files")
    if args.annovar_annotate_variation:
        perform_annovar(
            "annotate_variation",
            args.input,
            args.output,
            args.annovar_annotate_variation_commands,
        )
        args.input = os.path.join(args.output, "annotations")
    if args.annovar_coding_change:
        perform_annovar(
            "coding_change",
            args.input,
            args.output,
            args.annovar_coding_change_commands,
        )
        args.input = os.path.join(args.output, "fastas")
    if args.mhcflurry:
        sequences, flanks = perform_cropping_fastas(
            args.input, min(args.peptide_lengths) - 1
        )
        perform_mhcflurry(
            args.output,
            sequences,
            flanks,
            args.peptide_lengths,
            args.add_flanks,
            args.alleles,
        )
    print_lizard()


if __name__ == "__main__":
    main()
