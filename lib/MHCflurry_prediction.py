import os
import logging

try:
    from mhcflurry import Class1AffinityPredictor, Class1PresentationPredictor
except ImportError:
    logging.error("mhcflurry package not found. Please make sure it is installed.")
    raise

# 2 ways of doing this:
## 1) scan the sequence for peptides of given length(s) with good binding affinity --> no option to add flanks for improved accuracy
## 2) generate peptides of given length(s) in sequence and test them --> can add flanks for improved accuracy
# option 2 seems most reliable but yet to be benchmarked


class MHCflurryPipeline:
    """
    Pipeline for running MHCflurry on sequences (and flanks) for MHC-binding affinity prediction.
    """

    def __init__(self, path_handler):
        self.path_handler = path_handler

    def create_peptides(self, sequences: list, flanks: list, lengths: list, input_alleles):
        """
        Creates peptides and flanks as a better way of doing a scan for peptides.
        """
        peptides, N_flanks, C_flanks, sequence_names, alleles = [], [], [], [], []
        for count, value in enumerate(sequences):
            seq = value[1]
            name = value[0]
            for l in lengths:
                for index in range(len(seq)):
                    if index + l <= len(seq):  # Check if slicing is possible
                        peptides.append(seq[index : index + l])
                        N_flanks.append(flanks[count][0] + seq[:index])
                        C_flanks.append(seq[index:] + flanks[count][1])
                        sequence_names.append(name)
                        if isinstance(input_alleles,dict):
                            alleles.append(input_alleles[seq[0]])
                        else:
                            alleles.append[input_alleles]
        return peptides, N_flanks, C_flanks, sequence_names, alleles

    def run_mhcflurry_pipeline(
        self,
        sequences: list,
        flanks: list,
        lengths: list,
        add_flanks: bool,
        input_alleles,
    ):
        """
        Runs the MHCflurry pipeline.
        """
        try:
            logging.info("Running MHCflurry pipeline...")
            predictor = Class1PresentationPredictor.load()
            alleles=[]
            outfile = os.path.join(self.path_handler.output_path, "predictions.csv")

            if add_flanks:  # Decides if method 1 or 2
                peptides, N_flanks, C_flanks, sequence_names, alleles = self.create_peptides(
                    sequences, flanks, lengths, input_alleles
                )
                predictions = predictor.predict(
                    peptides=peptides,
                    n_flanks=N_flanks,
                    c_flanks=C_flanks,
                    alleles=alleles,
                )
                predictions.insert(0, "sequence_header", sequence_names)
                predictions.to_csv(outfile, index=False)
            else:
                if isinstance(input_alleles,dict): # Check if TCGA alleles were given
                    alleles = [input_alleles[i[0]] for i in sequences]
                else: # or custom alleles (list)
                    alleles = input_alleles * len(sequences)
                sequences = {i[0]: i[1] for i in sequences}
                predictor.predict_sequences(
                    sequences, alleles=alleles, peptide_lengths=lengths
                ).to_csv(outfile, index=False)

            self.path_handler.update_input(outfile)
            logging.info("Predictions completed.")
        except Exception as e:
            logging.exception(f"An error occurred: {str(e)}")

    # The binding affinity predictions are given as affinities (KD) in nM in the mhcflurry_affinity column. Lower values indicate stronger binders. A commonly-used threshold for peptides with a reasonable chance of being immunogenic is 500 nM.
    # The mhcflurry_affinity_percentile gives the percentile of the affinity prediction among a large number of random peptides tested on that allele (range 0 - 100). Lower is stronger. Two percent is a commonly-used threshold.
    # The last two columns give the antigen processing and presentation scores, respectively. These range from 0 to 1 with higher values indicating more favorable processing or presentation.
