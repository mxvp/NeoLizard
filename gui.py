import streamlit as st
import os
import logging
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
from contextlib import contextmanager
from io import StringIO
import sys


# Custom stream to capture the printed output
class OutputCapturer:
    def __init__(self):
        self.buffer = StringIO()

    def write(self, text):
        self.buffer.write(text)

    def flush(self):
        pass


# Context manager to temporarily redirect the stdout and capture return value
@contextmanager
def capture_output():
    capturer = OutputCapturer()
    sys.stdout = capturer
    original_stdout = sys.stdout
    try:
        yield capturer.buffer
    finally:
        sys.stdout = original_stdout


def main():
    st.title("NeoLizard - Custom Pipeline for Neoantigen Prediction")

    # Create text input for --input
    input_file = st.text_input(
        "Input File(s) Path", help="Required. Path to the input file(s)."
    )

    # Create text input for --output
    output_folder = st.text_input(
        "Output Folder Path",
        value=os.getcwd(),
        help="Path to the output folder. If not specified, the current working directory will be used.",
    )

    # Create checkboxes for --qc and --m2a
    perform_qc = st.checkbox("Perform QC", help="Perform QC if selected.")
    convert_maf_to_avinput = st.checkbox(
        "Convert MAF to AVINPUT",
        help="Convert MAF files to AVINPUT format if selected.",
    )

    # Create checkbox group for cutadapt arguments
    st.subheader("Cutadapt")
    perform_cutadapt = st.checkbox(
        "Perform Cutadapt", help="Perform Cutadapt if selected."
    )
    cutadapt_commands = st.text_input(
        "Cutadapt Commands",
        help="Enter commands for Cutadapt, excluding input and output, as a string e.g., '-q 5 -Q 15,20'.",
    )
    remove_cutadapt_input = st.checkbox(
        "Remove Original File(s)", help="Remove the original file(s) if selected."
    )

    # Create checkbox group for Annovar arguments
    st.subheader("Annovar")
    perform_annovar_annotate_variation = st.checkbox(
        "Perform annotate_variation", help="Perform annotate_variation if selected."
    )
    annovar_annotate_variation_commands = st.text_input(
        "Annotate Variation Commands",
        value ="annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate",
        help="Enter commands for Annovar annotate_variation, excluding input and output, as a string e.g., 'annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate'.",
    )
    perform_annovar_coding_change = st.checkbox(
        "Perform coding_change", help="Perform coding_change if selected."
    )
    annovar_coding_change_commands = st.text_input(
        "Coding Change Commands",
        value="-build hg38 -dbtype refGene annovar/humandb/ --comment",
        help="Enter commands for Annovar coding_change, excluding input and output, as a string e.g., '-build hg38 -dbtype refGene annovar/humandb/ --comment'.",
    )



    # Create checkbox group for MHCflurry arguments
    st.subheader("MHCflurry")
    perform_mhcflurry = st.checkbox(
        "Perform MHCflurry", help="Perform MHCflurry if selected."
    )
    add_flanks = st.checkbox(
        "Generate Peptides with Flanks",
        help="Generate peptides with flanks for improved accuracy if selected.",
    )
    peptide_lengths = st.text_input(
        "Peptide Length(s)",
        value="9",
        help="Enter length(s) of peptides to scan for separated by spaces e.g., '8 9 10 11'.",
    )
    # Create checkbox for "Custom alleles"
    use_custom_alleles = st.checkbox("Custom alleles", value=False, help="Enter the alleles separated by spaces e.g., 'HLA-A*31:01'.")

    #   Create "Custom alleles" text input field based on the checkbox value
    if use_custom_alleles:
        custom_alleles = st.text_input(
            "Enter the alleles separated by spaces e.g., 'HLA-A*31:01'.",
            value='HLA-A*31:01'
    )
    else:
        custom_alleles = ""  # Initialize the variable with an empty string when not using custom alleles

    TCGA_alleles = st.checkbox(
        "TCGA alleles",
        help="Use TCGA PanGenome alleles.",
    )

    st.subheader("Custom command")
    # Custom subprocess commands
    custom_command = st.text_input(
        "Custom command",
        help="Custom command with multiple arguments. Please enter as a string! e.g. 'a_module -m 10 -q 20 -j 4' ",
    )



    # Create a "Run" button to trigger the CLI functionality
    if st.button("Run NeoLizard"):
        with st.spinner("Running NeoLizard..."):
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
                "peptide_lengths": [int(length) for length in peptide_lengths.split()],
                "custom_alleles": custom_alleles.split(),
                "TCGA_alleles": TCGA_alleles
            }
            st.subheader("Execution Output")
            execute_cli(args)

        # Display success message
        st.success("NeoLizard execution is complete!")


def execute_cli(args):
    output = ""

    os.makedirs(args["output"], exist_ok=True) # Create output folder if it doesn't exist

    pathing = PathHandler(args['input'], args['output'])

    if not pathing.validate_paths():
        logging.error("Invalid input paths. Aborting!")
        return

    command_runner = CommandRunner()
    pipeline_data=PipelineData(pathing)
    HLA_pipeline = HLAPipeline(pathing,command_runner)

    if args["qc"]:
        # Capture the printed output and return value for QC function
        with capture_output() as out:
            qc_pipeline = QCPipeline(pathing, command_runner)
            qc_pipeline.run_pipeline()
            st.text("\n" + out.getvalue())
        st.text(output)

    if args["cutadapt"]:
        # Capture the printed output and return value for cutadapt function
        with capture_output() as out:
            cutadapt_pipeline = CutadaptPipeline(pathing,command_runner)
            cutadapt_pipeline.run_cutadapt_pipeline(args['cutadapt_commands'],args['cutadapt_remove'])
            st.text("\n" + out.getvalue())
        args["input"] = os.path.join(args["output"], "Processed")

    if args["m2a"]:
        # Capture the printed output and return value for MAF to AVINPUT conversion function
        with capture_output() as out:
            if args['TCGA_alleles']:
                # Gather HLA alleles from maf files
                pipeline_data.link_HLA_ID_TCGA_to_MAF_samples()
                # Temp custom source...
                HLA_dict = HLA_pipeline.process_TCGA_HLA(custom_source='./resources/panCancer_hla.tsv')
                pipeline_data.link_HLA_TCGA_to_samples(HLA_dict)
            # Perform MAF to AVInput conversion
            m2a_pipeline = MAFtoAVInputConverter(pathing)
            m2a_pipeline.run_pipeline()

            # Gather sample names and mutation names here (filename to "." and filename to ".  + lineX")
            pipeline_data.link_samples_to_mutation_from_avinput()
            
            st.text("\n" + out.getvalue())

    if args["annovar_annotate_variation"]:
        # Capture the printed output and return value for annovar 'annotate_variation' function
        with capture_output() as out:
            # Perform annovar_annotate
            annovar_pipeline = AnnovarPipeline(pathing, command_runner)
            annovar_pipeline.run_annotate_variation_pipeline(
                args['annovar_annotate_variation_commands']
            )
            st.text("\n" + out.getvalue())

    if args["annovar_coding_change"]:
        # Capture the printed output and return value for annovar 'coding_change' function
        with capture_output() as out:
            # Perform annovar_coding change
            annovar_pipeline = AnnovarPipeline(pathing, command_runner)
            annovar_pipeline.run_coding_change_pipeline(
                args['annovar_coding_change_commands']
            )

            # Link mutations to transcripts 
            pipeline_data.link_mutation_to_transcripts()

            # Link transcripts to HLA_alleles
            if args['TCGA_alleles']:
                pipeline_data.link_transcript_to_TCGA_HLA_alleles()
            st.text("\n" + out.getvalue())

    if args["mhcflurry"]:
        # Capture the printed output and return value for MHCflurry function
        with capture_output() as out:
            # Perform MHCflurry binding affinity prediction. Add_flanks and alleles will be used in pipeline.
            cropping_flanks_pipeline = CroppingFlanksPipeline(pathing)
            mhcflurry_pipeline = MHCflurryPipeline(pathing)

            flank_length = min(args['peptide_lengths']) - 1
            sequences, flanks = cropping_flanks_pipeline.cropping_flanks_pipeline_run(flank_length)

            if args['TCGA_alleles']:
                alleles = pipeline_data.transcripts_alleles
            else:
                alleles = args['custom_alleles']
            mhcflurry_pipeline.run_mhcflurry_pipeline(sequences,flanks,args['peptide_lengths'],args['add_flanks'],alleles)

            st.text("\n" + out.getvalue())

    # Perform the lizard function and capture its printed output
    with capture_output() as out:
        print_lizard()
        st.text("\n" + out.getvalue())


if __name__ == "__main__":
    main()
