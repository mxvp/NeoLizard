from mhcflurry import Class1AffinityPredictor
from mhcflurry import Class1PresentationPredictor
import os

# 2 ways of doing this:
## 1) scan the sequence for peptides of given length(s) with good binding affinity --> no option to add flanks for improved accuracy
## 2) generate peptides of given length(s) in sequence and test them --> can add flanks for improved accuracy
# option 2 seems most reliable but yet to be benchmarked

def mhcflurry_scan(sequences,lengths,alleles):
    # Load the trained predictor
    predictor = Class1PresentationPredictor.load()

    # Use the predictor to make predictions on the sequences
    return predictor.predict_sequences(sequences, alleles=alleles,peptide_lengths=lengths)

#--------------------
def mhcflurry_predict(sequences):
    pass

def create_peptides(sequences,flanks,lengths,alleles):
    peptides,N_flanks,C_flanks,new_alleles={},[],[]
    for count,value in enumerate(sequences):
        seq=value[1]
        for l in lengths:
            # sliding window approach here!


            new_alleles.append(alleles[count])
    return peptides,N_flanks,C_flanks,new_alleles
#---------------------


def perform_mhcflurry(output,sequences,flanks,lengths,add_flanks,alleles):
    # Create a list of alleles matching the number of sequences
    if len(alleles)==1:
        alleles = alleles * len(sequences)  # Replace with the desired allele
    else:
        alleles.extend(["HLA-A*31:01"]*(len(sequences)-len(alleles)))
    
    outfile = os.path.join(output, "predictions.csv")
    if add_flanks:
        with open(outfile,'a') as f:
            peptides,N_flanks,C_flanks,alleles=create_peptides(sequences,flanks,lengths,alleles)
            mhcflurry_predict(peptides,N_flanks,C_flanks,alleles).to_csv(outfile,index=False)
    else:
        sequences={i[0].split()[1]:i[1]for i in sequences}
        mhcflurry_scan(sequences,lengths,alleles).to_csv(outfile,index=False)
    return print("Predictions completed.")


#The binding affinity predictions are given as affinities (KD) in nM in the mhcflurry_affinity column. Lower values indicate stronger binders. A commonly-used threshold for peptides with a reasonable chance of being immunogenic is 500 nM.
#The mhcflurry_affinity_percentile gives the percentile of the affinity prediction among a large number of random peptides tested on that allele (range 0 - 100). Lower is stronger. Two percent is a commonly-used threshold.
#The last two columns give the antigen processing and presentation scores, respectively. These range from 0 to 1 with higher values indicating more favorable processing or presentation.