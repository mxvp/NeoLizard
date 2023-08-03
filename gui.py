import streamlit as st
import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import StringIO
from lib.logger_config import configure_lib_logger, configure_logger
from lib.path_handler import PathHandler
from lib.cmd_runner import CommandRunner
from lib.qc import QCPipeline
from lib.m2a import MAFtoAVInputConverter
from lib.annovar_functions import AnnovarPipeline
from lib.cropping_flanks import CroppingFlanksPipeline
from lib.MHCflurry_prediction import MHCflurryPipeline
from lib.lizard import print_lizard
from lib.cutadapt import CutadaptPipeline
from lib.data_gathering import PipelineData
from lib.HLA import HLAPipeline
from lib.database_operations import DatabaseOperations
from contextlib import contextmanager

# Results page under pages/results.py

st. set_page_config(layout="wide") 
st.sidebar.image('./resources/NEO_logo.png')

def main():
    """
    Main function for running the NeoLizard streamlit gui.
    """

    # Set title and subtitle
    st.title("NeoLizard")
    st.header("Custom Pipeline for Neoantigen Prediction")

    ## Query builder

    # Paths
    input_file = st.text_input(
        "Input File(s) Path", help="Required. Path to the input file(s)."
    )
    output_folder = st.text_input(
        "Output Folder Path",
        value=os.getcwd(),
        help="Path to the output folder. If not specified, the current working directory will be used.",
    )
    # Preprocessing
    st.subheader("Preprocessing (beta)")
    perform_qc = st.checkbox("Perform QC", help="Perform QC using Fastqc and Multiqc.")
    perform_cutadapt = st.checkbox("Perform Cutadapt", help="Perform Cutadapt.")
    if perform_cutadapt:
        cutadapt_commands = st.text_input(
            "Cutadapt Commands",
            help="Enter commands for Cutadapt, excluding input and output e.g., '-q 5 -Q 15,20'.",
        )
    else:
        cutadapt_commands = ""

    remove_cutadapt_input = st.checkbox(
        "Remove Original File(s)",
        help="Remove the original raw file(s) sequentially to limit disk usage.",
    )
    custom_command = st.checkbox("Custom command (beta)", help="Create custom command.")
    if custom_command:
        custom_command = st.text_input(
            "Custom command (beta)",
            help="Custom command with multiple arguments. E.g. 'a_module -m 10 -q 20 -j 4' ",
        )
    else:
        custom_command = ""

    st.subheader("MAF file conversion")
    convert_maf_to_avinput = st.checkbox(
        "Convert MAF to AVINPUT",
        help="Convert MAF files to AVINPUT format if selected. Necessary for implementing ANNOVAR.",
    )

    # ANNOVAR
    st.subheader("ANNOVAR")
    perform_annovar_annotate_variation = st.checkbox(
        "Perform annotate_variation", help="Perform annovar annotate_variation."
    )
    if perform_annovar_annotate_variation:
        annovar_annotate_variation_commands = st.text_input(
            "Annotate Variation Commands",
            value="-build hg38 -dbtype refGene annovar/humandb/ --comment",
            help="Enter commands for Annovar coding_change, excluding input and output. E.g. '-build hg38 -dbtype refGene annovar/humandb/ --comment'.",
        )
    else:
        annovar_annotate_variation_commands = ""
    perform_annovar_coding_change = st.checkbox(
        "Perform coding_change", help="Perform annovar coding_change."
    )
    if perform_annovar_coding_change:
        annovar_coding_change_commands = st.text_input(
            "Coding Change Commands",
            value="annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate",
            help="Enter commands for Annovar annotate_variation, excluding input and output. E.g. 'annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate'.",
        )
    else:
        annovar_coding_change_commands = ""

    # MHCflurry
    st.subheader("MHCflurry")
    perform_mhcflurry = st.checkbox("Perform MHCflurry", help="Perform MHCflurry.")
    if perform_mhcflurry:
        add_flanks = st.checkbox(
            "Generate Peptides with Flanks",
            help="Generate peptides with extended flanks for improved accuracy (computationally more intensive).",
        )
        peptide_lengths = st.text_input(
            "Peptide Length(s)",
            value="9",
            help="Enter length(s) of peptides to scan for separated by spaces e.g. '8 9 10 11'.",
        )
        use_custom_alleles = st.checkbox(
            "Custom alleles",
            value=False,
            help="Enter the alleles separated by spaces e.g., 'HLA-A*31:01'.",
        )
        if use_custom_alleles:
            custom_alleles = st.text_input(
                "Enter the allele(s) separated by spaces e.g., 'HLA-A*31:01'.",
                value="HLA-A*31:01",
            )
        else:
            custom_alleles = ""

        TCGA_alleles = st.checkbox(
            "TCGA alleles",
            help="Use TCGA PanGenome alleles.",
        )
    else:
        add_flanks = False
        peptide_lengths = ""
        use_custom_alleles = False
        custom_alleles = ""
        TCGA_alleles = False

    # database operations
    st.subheader("PostgreSQL ")
    store_db = st.checkbox(
        "Store data in PostgreSQL database",
        help="If PostgreSQL is installed, this will store all relevant intermediate data and predictions result in a database.",
    )
    if store_db:
        db_username = st.text_input(
            "Enter username",
            value="postgres",
            help="Database username, default superuser is postgres",
        )
        db_password = st.text_input("Enter password", help="Database password")
        db_host = st.text_input(
            "Enter hostname",
            value="localhost",
            help="Database host, default is localhost",
        )
        db_name = st.text_input(
            "Enter database name",
            value="neolizard_db",
            help="Database name, lowercase! Default is neolizard_db",
        )
    else:
        db_username = ""
        db_password = ""
        db_host = ""
        db_name = ""

    # Create a "Run" button to trigger the CLI functionality
    if st.button("Run NeoLizard"):
        # Create argparse.Namespace object with the selected options and their values
        args = {
            "input": input_file,
            "output": output_folder,
            "qc": perform_qc,
            "m2a": convert_maf_to_avinput,
            "cutadapt": perform_cutadapt,
            "cutadapt_commands": cutadapt_commands,
            "cutadapt_remove": remove_cutadapt_input,
            "annovar_annotate_variation": perform_annovar_annotate_variation,
            "annovar_coding_change": perform_annovar_coding_change,
            "annovar_coding_change_commands": annovar_coding_change_commands,
            "annovar_annotate_variation_commands": annovar_annotate_variation_commands,
            "mhcflurry": perform_mhcflurry,
            "add_flanks": add_flanks,
            "peptide_lengths": [int(length) for length in peptide_lengths.split(' ')],
            "custom_alleles": custom_alleles.split(),
            "TCGA_alleles": TCGA_alleles,
            "store_db": store_db,
            "db_username": db_username,
            "db_password": db_password,
            "db_host": db_host,
            "db_name": db_name,
        }
        st.subheader("Execution Output")
        execute_cli(args)

        # Display success message
        st.success("NeoLizard execution is complete!")


def execute_cli(args):
    '''
    Will execute all all selected query elements.
    '''
    output = ""

    os.makedirs(
        args["output"], exist_ok=True
    )  # Create output folder if it doesn't exist

    # Initiate pathing handler
    pathing = PathHandler(args["input"], args["output"])

    if not pathing.validate_paths():
        logging.error("Invalid input paths. Aborting!")
        return

    # Initiate other objects
    command_runner = CommandRunner()
    pipeline_data = PipelineData(pathing)
    HLA_pipeline = HLAPipeline(pathing, command_runner)

    ## Run each selected query element, same workflow as NeoLizard.py main CLI functionality.

    if args["qc"]:
        with st.spinner("Running QC..."):
            qc_pipeline = QCPipeline(pathing, command_runner)
            qc_pipeline.run_pipeline()

    if args["cutadapt"]:
        with st.spinner("Running Cutadapt..."):
            cutadapt_pipeline = CutadaptPipeline(pathing, command_runner)
            cutadapt_pipeline.run_cutadapt_pipeline(
                args["cutadapt_commands"], args["cutadapt_remove"]
            )
        args["input"] = os.path.join(args["output"], "Processed")

    if args["m2a"]:
        with st.spinner("Converting MAF to AVINPUT..."):
            try:
                if args["TCGA_alleles"]:
                    pipeline_data.link_HLA_ID_TCGA_to_MAF_samples()
                    HLA_dict = HLA_pipeline.process_TCGA_HLA(
                        custom_source="./resources/panCancer_hla.tsv"
                    )
                    pipeline_data.link_HLA_TCGA_to_samples(HLA_dict)
                m2a_pipeline = MAFtoAVInputConverter(pathing)
                m2a_pipeline.run_pipeline()
                pipeline_data.link_samples_to_mutation_from_avinput()
            except Exception as e:
                st.write(f"in m2a: {e}")
    if args["annovar_annotate_variation"]:
        with st.spinner("Running Annovar annotate_variation..."):
            try:
                annovar_pipeline = AnnovarPipeline(pathing, command_runner)
                annovar_pipeline.run_annotate_variation_pipeline(
                    args["annovar_annotate_variation_commands"]
                )
            except Exception as e:
                st.write(f"in annovar annotate: {e}")

    if args["annovar_coding_change"]:
        with st.spinner("Running Annovar coding_change..."):
            try:
                annovar_pipeline = AnnovarPipeline(pathing, command_runner)
                annovar_pipeline.run_coding_change_pipeline(
                    args["annovar_coding_change_commands"]
                )
                pipeline_data.link_mutation_to_transcripts()
                if args["TCGA_alleles"]:
                    pipeline_data.link_transcript_to_TCGA_HLA_alleles()
            except Exception as e:
                st.write(f"in annovar coding change: {e}")

    if args["mhcflurry"]:
        with st.spinner("Running MHCflurry..."):
            cropping_flanks_pipeline = CroppingFlanksPipeline(pathing)
            mhcflurry_pipeline = MHCflurryPipeline(pathing)
            flank_length = min(args["peptide_lengths"]) - 1
            sequences, flanks = cropping_flanks_pipeline.cropping_flanks_pipeline_run(
                flank_length
            )
            if args["TCGA_alleles"]:
                alleles = pipeline_data.transcripts_alleles
            else:
                alleles = args["custom_alleles"]
            mhcflurry_pipeline.run_mhcflurry_pipeline(
                sequences, flanks, args["peptide_lengths"], args["add_flanks"], alleles
            )

        # Update session_state value when analysis is complete and results page can be generated.
        st.session_state["predictions"] = pathing.input_path

    if args["store_db"]:
        with st.spinner("Storing data in PostgreSQL database..."):
            database_operations = DatabaseOperations(
                args["db_username"],
                args["db_password"],
                args["db_host"],
                args["db_name"],
                pipeline_data,
                pathing,
            )

    with st.spinner("Running Lizard..."):
        print_lizard()


if __name__ == "__main__":
    # Initialize session_state value (these are carried over pages).
    st.session_state["predictions"] = None
    main()
