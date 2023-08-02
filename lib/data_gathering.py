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

        self.sample_allele_IDs = (
            None  # dict: {filename: HLA_TCGA_ID, filename2: HLA_TCGA_ID2,...}
        )
        self.sample_alleles = None  # dict: {filename:[HLA_allele1, HLA_allele2,...], filename2:[HLA_allele1_1, HLA_allele2_2,...],...}
        self.sample_mutations = None  # dict: {filename: [line1,line2,line3,...], filename2: [line1_1,line2_2,line3_3,...],...}
        self.mutation_transcripts = None  # dict: {filename_lineX: [NM...,NM...,NM...], filename_lineX2: [NM...,NM...,NM...],...}
        self.transcripts_alleles = None  # dict: {filename_lineX_NM: [HLA_allele1, HLA_allele2,...], filename_lineX_NM2: [HLA_allele1, HLA_allele2,...],...}


    def link_HLA_ID_TCGA_to_MAF_samples(self):
        '''
        Function to link the HLA_IDs from TCGA to the MAF samples.
        '''
        sample_allele_IDs = {}
        file_list = self.path_handler.file_list(
            self.path_handler.input_path
        )  # read in .avinput files
        for file in file_list:
            try:
                # Read the data from the file
                with open(file[0]) as f:
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
                    sample = file[1].split(".")[0]
                    sample_allele_IDs[sample] = allele
            except Exception as e:
                logging.error(f"{e} in link_HLA_ID_TCGA_to_MAF_samples")
        self.sample_allele_IDs = sample_allele_IDs

    def link_HLA_TCGA_to_samples(self, HLA_dict: dict):
        '''
        Function to link HLA-alleles to the MAF samples.
        '''
        sample_alleles = {}
        try:
            for sample, allele_ID in self.sample_allele_IDs.items():
                try:
                    sample_alleles[sample] = HLA_dict[
                        allele_ID[:16]
                    ]  # :16 because the TCGA file reports first 16 chars
                except:
                    logging.info(
                        f"TCGA alleles not found for {sample},defaulting to ['HLA-A*31:01']"
                    )
                    sample_alleles[sample] = ["HLA-A*31:01"]
        except Exception as e:
            logging.error(f"{e} in link_HLA_TCGA_to_samples")
        self.sample_alleles = sample_alleles

    def link_samples_to_mutation_from_avinput(self):
        '''
        Function to link the samples to the mutations (from AVINPUT).
        '''
        sample_mutations = {}
        file_list = self.path_handler.file_list(
            self.path_handler.input_path
        )  # read in .avinput files
        for file in file_list:
            try:
                with open(file[0]) as f:
                    lines = f.readlines()
                    sample = file[1].split(".")[0]
                    sample_mutations[sample] = []
                    for i in range(len(lines)):
                        sample_mutations[sample].append("line" + str(i + 1))
            except Exception as e:
                logging.error(f"{e} in link_samples_to_mutation_from_avinput")
        self.sample_mutations = sample_mutations

    def link_mutation_to_transcripts(self):
        '''
        Function to link the mutations from AVINPUT to the transcripts in the fastas.
        '''
        mutation_transcripts = {}
        file_list = self.path_handler.file_list(self.path_handler.input_path)
        for file in file_list:
            try:
                with open(file[0], "r") as f:
                    sample = file[1].split(".")[0]
                    for line in f:
                        if line.startswith(">"):
                            line = line[1:].split(" ")
                            lineX = line[0]
                            if sample + "_" + lineX not in mutation_transcripts:
                                mutation_transcripts[sample + "_" + lineX] = []
                            transcript = line[1]
                            if (
                                transcript
                                not in mutation_transcripts[sample + "_" + lineX]
                            ):
                                mutation_transcripts[sample + "_" + lineX].append(
                                    transcript
                                )
            except Exception as e:
                logging.error(f"{e} in link_mutation_to_transcripts")
        self.mutation_transcripts = mutation_transcripts

    def link_transcript_to_TCGA_HLA_alleles(self):
        '''
        Function to link the transcripts to the HLA alleles from TCGA.
        '''
        transcript_alleles = {}
        # Try to keep logical order to benefit MHCflurry linking process efficiency
        for key, value in self.mutation_transcripts.items():
            for transcript in value:
                transcript_alleles[key + "_" + transcript] = self.sample_alleles[
                    key.split("_")[0]
                ]
        self.transcripts_alleles = transcript_alleles
