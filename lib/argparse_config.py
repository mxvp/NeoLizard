# Have to use prefixes for subarguments, namespace conflicts will happen even if using groups

# By default, argparse will assume that any argument that starts with a hyphen (-) is an option or flag,
# and any argument that doesn't start with a hyphen is a positional argument.
# This means that as long as the arguments provided after the positional argument(s) don't start with a hyphen,
# argparse will interpret them as values for that positional argument.
# --> we use strings when passing commands that need to be performed in a subprocess. The script will correctly turn them into lists.

import os
import argparse


def parse_the_args():
    """
    Full argument parsing config, this is imported in main().
    """
    parser = argparse.ArgumentParser(
        description="Custom pipeline for neoantigen prediction on NGS samples or TCGA MAF files.",
        prog="NeoLizard",
    )
    parser.add_argument(
        "--input", type=str, required=True, help="<Required> Input file(s) path"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.getcwd(),
        help="Provide output folder path. If none is specified, current working directory is used.",
    )
    parser.add_argument("--qc", action="store_true", help="perform QC")
    parser.add_argument("--m2a", action="store_true", help="Convert MAF to AVINPUT")

    cutadapt_parser = parser.add_argument_group("cutadapt", "Cutadapt")
    cutadapt_parser.add_argument(
        "--cutadapt", action="store_true", help="Perform cutadapt"
    )
    cutadapt_parser.add_argument(
        "--cutadapt_commands",
        type=str,
        help='Enter commands for cutadapt, excluding input and output, as string e.g. "-q 5 -Q 15,20" ',
    )
    cutadapt_parser.add_argument(
        "--cutadapt_remove", action="store_true", help="Remove original file(s)"
    )

    annovar_parser = parser.add_argument_group("annovar", "Annovar")
    annovar_parser.add_argument(
        "--annovar_annotate_variation",
        action="store_true",
        help="Perform annotate_variation.",
    )
    annovar_parser.add_argument(
        "--annovar_coding_change", action="store_true", help="Perform coding_change."
    )
    annovar_parser.add_argument(
        "--annovar_coding_change_commands",
        type=str,
        default='annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate',
        help='Enter commands for annovar, excluding input and output, as string e.g. "annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate"',
    )
    annovar_parser.add_argument(
        "--annovar_annotate_variation_commands",
        type=str,
        default='-build hg38 -dbtype refGene annovar/humandb/ --comment',
        help='Enter commands for annovar, excluding input and output, as string e.g. "-build hg38 -dbtype refGene annovar/humandb/ --comment"',
    )

    HLA_parser = parser.add_argument_group("HLA", "HLA")
    HLA_parser.add_argument(
        "--HLA_TCGA", action="store_true", help="Use TCGA source for HLA alleles."
    )
    HLA_parser.add_argument(
        "--HLA_TCGA_custom",
        type=str,
        default=None,
        help="Enter custom path to TCGA HLA alleles text file.",
    )
    HLA_parser.add_argument(
        "--HLA_typing", action="store_true", help="Perform HLA typing on samples."
    )

    mhcflurry_parser = parser.add_argument_group("mhcflurry", "MHCflurry")
    mhcflurry_parser.add_argument(
        "--mhcflurry", action="store_true", help="Perform mhcflurry"
    )
    mhcflurry_parser.add_argument(
        "--add_flanks",
        action="store_true",
        help="Generate peptides of given length(s) in sequence and test them --> can add flanks for improved accuracy.",
    )
    mhcflurry_parser.add_argument(
        "--peptide_lengths",
        type=int,
        default=[9],
        nargs="+",
        help="Enter length(s) of peptides to scan for."
    )
    mhcflurry_parser.add_argument(
        "--TCGA_alleles",
        action='store_true',
        help="Use TCGA PanCancer alleles."
    )
    mhcflurry_parser.add_argument(
        "--custom_alleles",
        type=str,
        nargs="+",
        default=["HLA-A*31:01"],
        help="Enter the HLA alleles.",
    )

    cmd_parser = parser.add_argument_group("cmd", "Custom command")
    cmd_parser.add_argument(
        "--cmd",
        type=str,
        help="Custom command with multiple arguments. Please enter as a string! e.g. 'a_module -m 10 -q 20 -j 4' ",
    )

    database_parser = parser.add_argument_group("database", "Database")
    database_parser.add_argument(
        "--store_db",
        action='store_true',
        help='Store results in database. Will be created if not available. Please fill in credentials using "--db-username" "--db-password" "--db-host" and "--db-name".'
    )
    database_parser.add_argument("--db_username", type=str, default='postgres', help="Database username, default superuser is postgres")
    database_parser.add_argument("--db_password", type=str, help="Database password")
    database_parser.add_argument("--db_host", type=str, default= 'localhost', help="Database host, default is localhost")
    database_parser.add_argument("--db_name", type=str, default='neolizard_db',help="Database name, lowercase! Default is neolizard_db")

    # Parse the arguments
    args = parser.parse_args()

    return args
