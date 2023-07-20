import streamlit as st
import os
from lib import (
    qc,
    cutadapt,
    lizard,
    m2a,
    annovar_functions,
    cropping_flanks,
    MHCflurry_prediction
)
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
    input_file = st.text_input("Input File(s) Path", help="Required. Path to the input file(s).")

    # Create text input for --output
    output_folder = st.text_input("Output Folder Path", value=os.getcwd(), help="Path to the output folder. If not specified, the current working directory will be used.")

    # Create checkboxes for --qc and --m2a
    perform_qc = st.checkbox("Perform QC", help="Perform QC if selected.")
    convert_maf_to_avinput = st.checkbox("Convert MAF to AVINPUT", help="Convert MAF files to AVINPUT format if selected.")

    # Create checkbox group for cutadapt arguments
    st.subheader("Cutadapt")
    perform_cutadapt = st.checkbox("Perform Cutadapt", help="Perform Cutadapt if selected.")
    cutadapt_commands = st.text_input("Cutadapt Commands", help="Enter commands for Cutadapt, excluding input and output, as a string e.g., '-q 5 -Q 15,20'.")
    remove_cutadapt_input = st.checkbox("Remove Original File(s)", help="Remove the original file(s) if selected.")

    # Create checkbox group for Annovar arguments
    st.subheader("Annovar")
    perform_annovar_annotate_variation = st.checkbox("Perform annotate_variation", help="Perform annotate_variation if selected.")
    perform_annovar_coding_change = st.checkbox("Perform coding_change", help="Perform coding_change if selected.")
    annovar_coding_change_commands = st.text_input("Coding Change Commands", help="Enter commands for Annovar coding_change, excluding input and output, as a string e.g., '-build hg38 -dbtype refGene annovar/humandb/ --comment'.")
    annovar_annotate_variation_commands = st.text_input("Annotate Variation Commands", help="Enter commands for Annovar annotate_variation, excluding input and output, as a string e.g., 'annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate'.")

    # Create checkbox group for MHCflurry arguments
    st.subheader("MHCflurry")
    perform_mhcflurry = st.checkbox("Perform MHCflurry", help="Perform MHCflurry if selected.")
    add_flanks_for_accuracy = st.checkbox("Generate Peptides with Flanks", help="Generate peptides with flanks for improved accuracy if selected.")
    peptide_lengths = st.text_input("Peptide Length(s)", value="8 9 10 11", help="Enter length(s) of peptides to scan for separated by spaces e.g., '8 9 10 11'.")
    alleles = st.text_input("Alleles", value="HLA-A*31:01", help="Enter the alleles separated by spaces e.g., 'HLA-A*31:01'.")

    # Create a "Run" button to trigger the CLI functionality
    if st.button("Run NeoLizard"):
        with st.spinner("Running NeoLizard..."):

            # Create argparse.Namespace object with the selected options and their values
            args = {
                'input': input_file,
                'output': output_folder,
                'qc': perform_qc,
                'm2a': convert_maf_to_avinput,
                'cutadapt': perform_cutadapt,
                'cutadapt_commands': cutadapt_commands,
                'cutadapt_remove': remove_cutadapt_input,
                'annovar_annotate_variation': perform_annovar_annotate_variation,
                'annovar_coding_change': perform_annovar_coding_change,
                'annovar_coding_change_commands': annovar_coding_change_commands,
                'annovar_annotate_variation_commands': annovar_annotate_variation_commands,
                'mhcflurry': perform_mhcflurry,
                'add_flanks': add_flanks_for_accuracy,
                'peptide_lengths': [int(length) for length in peptide_lengths.split()],
                'alleles': alleles.split(),
            }
            st.subheader("Execution Output")
            execute_cli(args)


        # Display success message
        st.success("NeoLizard execution is complete!")


def execute_cli(args):
    output = ""

    if args['qc']:
        # Capture the printed output and return value for QC function
        with capture_output() as out:
            result = qc.perform_qc(args['input'], args['output'])
            st.text("\n"+out.getvalue())
        st.text(output)

    if args['cutadapt']:
        # Capture the printed output and return value for cutadapt function
        with capture_output() as out:
            result = cutadapt.perform_cutadapt(args['input'], args['output'], args['cutadapt_commands'], args['cutadapt_remove'])
            st.text("\n"+out.getvalue())
        args['input'] = os.path.join(args['output'], 'Processed')

    if args['m2a']:
        # Capture the printed output and return value for MAF to AVINPUT conversion function
        with capture_output() as out:
            result = m2a.convert_maf_to_avinput(args['input'], args['output'])
            st.text("\n"+out.getvalue())
        args['input'] = os.path.join(args['output'], 'avinput_files')

    if args['annovar_annotate_variation']:
        # Capture the printed output and return value for annovar 'annotate_variation' function
        with capture_output() as out:
            result = annovar_functions.perform_annovar('annotate_variation', args['input'], args['output'], args['annovar_annotate_variation_commands'])
            st.text("\n"+out.getvalue())
        args['input'] = os.path.join(args['output'], 'annotations')

    if args['annovar_coding_change']:
        # Capture the printed output and return value for annovar 'coding_change' function
        with capture_output() as out:
            result = annovar_functions.perform_annovar('coding_change', args['input'], args['output'], args['annovar_coding_change_commands'])
            st.text("\n"+out.getvalue())
        args['input'] = os.path.join(args['output'], 'fastas')

    if args['mhcflurry']:
        # Capture the printed output and return value for MHCflurry function
        sequences, flanks = cropping_flanks.perform_cropping_fastas(args['input'], min(args['peptide_lengths']) - 1)
        with capture_output() as out:
            result = MHCflurry_prediction.perform_mhcflurry(args['output'], sequences, flanks, args['peptide_lengths'], args['add_flanks'], args['alleles'])
            st.text("\n"+out.getvalue())

    # Perform the lizard function and capture its printed output
    with capture_output() as out:
        lizard.print_lizard()
        st.text("\n"+out.getvalue())




if __name__ == "__main__":
    main()