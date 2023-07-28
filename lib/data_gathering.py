
# SAMPLE = filename before any "."
# MUTATION = SAMPLE + lineX (line from avinput containing the mutation)
# TRANSCRIPT = NM... (from fasta that is found based on MUTATION)
# PEPTIDE = the peptide itself, found from header passed to mhcflurry predictions

import pandas as pd
import os
import logging


class PipelineData:
    """
    This class object serves 2 purposes: saving all analyzed data and performing data gathering functions.
    """

    def __init__(self, path_handler):
        self.path_handler = path_handler
        self.sample_alleles = None
        self.sample_allele_IDs = None
        self.sample_mutations = None
        self.mutation_transcripts = None

        self.data = data = {
            "samples": [],
            "alleles": [],
            "mutations": [],
            "transcripts": [],
            "peptide": [],
        }

    def link_samples_to_mutation_from_avinput(self):
        sample_mutations = {}
        file_list = self.path_handler.file_list(
            self.path_handler.input_path
        )  # read in .avinput files
        for file in file_list:
            try:
                with open(file) as f:
                    lines = f.readlines()
                    sample = os.path.basename(file).split(".")[0]
                    for i in len(lines):
                        sample_mutations[sample] = "line" + str(i + 1)
            except Exception as e:
                logging.error(e)
        self.sample_mutations = sample_mutations
        return sample_mutations

    def link_HLA_ID_TCGA_to_MAF_samples(self, HLA_dict: dict):
        sample_allele_IDs = {}
        file_list = self.path_handler.file_list(
            self.path_handler.input_path
        )  # read in .avinput files
        for file in file_list:
            try:
                # Read the data from the file
                with open(file) as f:
                    lines = f.readlines()
                    # Remove lines starting with "#" and split the remaining lines into columns
                    data_lines = [
                        line.strip().split("\t")
                        for line in lines
                        if not line.startswith("#")
                    ]

                    # Extract the header line
                    header = data_lines[0]

                    # Create a DataFrame from the data lines
                    df = pd.DataFrame(data_lines[1:], columns=header)
                    allele = df.loc[0, "Tumor_Sample_Barcode"]
                    sample = os.path.basename(file).split(".")[0]
                    sample_allele_IDs[sample] = allele
            except Exception as e:
                logging.error(e)
        self.sample_allele_IDs = sample_allele_IDs

    def link_HLA_TCGA_to_samples(self, sample_allele_IDs: dict, HLA_dict: dict):
        sample_alleles = {}
        try:
            for sample, allele_ID in sample_allele_IDs.items():
                sample_alleles[sample] = HLA_dict[allele_ID]
        except Exception as e:
            logging.error(e)
        self.sample_alleles = sample_alleles
        return sample_alleles
    
    def link_mutation_to_transcripts(self):
        mutation_transcripts = {}
        file_list = self.path_handler.file_list(self.path_handler.input_path)
        for file in file_list:
            try:
                with open(file,'r') as f:
                    sample = os.path.basename(file).split(".")[0]
                    for line in f:
                        if line.startswith(">"):
                            line = line[1:].split(' ')
                            lineX=line[0]
                            if sample+'_'+lineX not in mutation_transcripts:
                                mutation_transcripts[sample+'_'+lineX]=[]
                            transcript = line[1]
                            if transcript not in mutation_transcripts[sample+'_'+lineX]:
                                mutation_transcripts[sample+'_'+lineX].append(transcript)
            except Exception as e:
                logging.error(e)
        self.mutation_transcripts = mutation_transcripts

            

