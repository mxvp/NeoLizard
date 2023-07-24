from mhcflurry import Class1AffinityPredictor
from mhcflurry import Class1PresentationPredictor
import os

# 2 ways of doing this:
## 1) scan the sequence for peptides of given length(s) with good binding affinity --> no option to add flanks for improved accuracy
## 2) generate peptides of given length(s) in sequence and test them --> can add flanks for improved accuracy
# option 2 seems most reliable but yet to be benchmarked


def create_peptides(sequences, flanks, lengths):
    peptides, N_flanks, C_flanks, sequence_names = [], [], [], []
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
    return peptides, N_flanks, C_flanks, sequence_names


def perform_mhcflurry(output, sequences, flanks, lengths, add_flanks, alleles):
    predictor = Class1PresentationPredictor.load()
    outfile = os.path.join(output, "predictions.csv")
    if add_flanks:
        peptides, N_flanks, C_flanks, sequence_names = create_peptides(
            sequences, flanks, lengths
        )
        predictions = predictor.predict(
            peptides=peptides, n_flanks=N_flanks, c_flanks=C_flanks, alleles=alleles
        )
        predictions.insert(0, "sequence_header", sequence_names)
        predictions.to_csv(outfile, index=False)
    else:
        # Create a list of alleles matching the number of sequences
        if len(alleles) == 1:
            alleles = alleles * len(sequences)  # Replace with the desired allele
        else:
            alleles.extend(["HLA-A*31:01"] * (len(sequences) - len(alleles)))
        sequences = {i[0]: i[1] for i in sequences}
        predictor.predict_sequences(
            sequences, alleles=alleles, peptide_lengths=lengths
        ).to_csv(outfile, index=False)
    return print("Predictions completed.")


# The binding affinity predictions are given as affinities (KD) in nM in the mhcflurry_affinity column. Lower values indicate stronger binders. A commonly-used threshold for peptides with a reasonable chance of being immunogenic is 500 nM.
# The mhcflurry_affinity_percentile gives the percentile of the affinity prediction among a large number of random peptides tested on that allele (range 0 - 100). Lower is stronger. Two percent is a commonly-used threshold.
# The last two columns give the antigen processing and presentation scores, respectively. These range from 0 to 1 with higher values indicating more favorable processing or presentation.
