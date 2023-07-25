#!/usr/bin/env Rscript

### Some code for NMDS plot is adapted from  Sarkizova et al Nature Biotechnology 
### volume 38, pages199–209(2020) and https://github.com/jonaskuiper/ERAP2_HLA-A29_peptidome

library(HDMD)
library(ecodist)
library(dbscan)
library(UpSetR)
library(gridExtra)
library(RColorBrewer)
library(Biostrings)
library(ggseqlogo)
library(mclust)
library(ggplot2)

# Enter path of predictions csv file and substitution matrix (distPMBEC)
predictions_path = './Predictions_deduped.csv'
subst_matrix_path = './distPMBEC.txt'

### Load  data
predictions<-read.csv(predictions_path)
peps<-predictions[4]
peps<-as.character(peps[,1])

rndseed = 12311
npeps <- length(peps)
len=9
### Calculate Molecular Entropy for amino acid positions
molecularEntropy <- MolecularEntropy(peps, type='AA')

#NMDS plot
### Compute peptide distances using amino acid substitutionmatrix "distPMBEC file" 
distPMBEC <- read.table(subst_matrix_path, header=TRUE, stringsAsFactors=FALSE)

# functions
getDistances <- function(peps, pos_weights=NULL, len=9) {
  if (is.null(pos_weights)) { pos_weights = rep(1, len) }
  n <- length(peps)
  dists <- matrix(nrow=n, ncol=n)
  . <<- lapply(1:n, function(i) { dists[i,i:n] <<- unlist(lapply(i:n, function(j) {
    pepDistPMBEC(strsplit(peps[i], '')[[1]], strsplit(peps[j], '')[[1]], len, pos_weights)
  }))})
  dists[lower.tri(dists)] <- t(dists)[lower.tri(dists)]
  colnames(dists) <- rownames(dists) <- peps
  return(dists)
}

pepDistPMBEC <- function(pepA, pepB, len, pos_weights) {
  return ((sum(unlist(lapply(1:len, function(i) {
    distPMBEC[pepA[i], pepB[i]]*pos_weights[i]
  })))) / len)
}

pos_weights <- 1 - molecularEntropy$H
dists <- getDistances(peps, pos_weights)

### Reduce dimensions (NMDS)
### Note: This step is computationally intensive, it will run relatively
###       quickly for a few hundred peptides but with a few thousand
###       peptides it will take a while.
###       nits=10 is used to generate plots with maxit=500. The trace will help you track progress

set.seed(rndseed)
nmds.tmp <- nmds(as.dist(dists), mindim=2, maxdim=2, nits=10, maxit=500, trace=TRUE)
nmds.dat <- nmds.tmp$conf[[which.min(nmds.tmp$stress)]]


### Clustering

# Perform Gibbs clustering using MCLUST
# 6 clusters as we expect to differentiate between 6 different HLA types
gibbs_model <- Mclust(as.dist(dists), G = 6)

# Get cluster assignments
gibbs_cluster_ids <- unclass(gibbs_model$classification)

# The number of clusters
num_gibbs_clusters <- length(unique(gibbs_cluster_ids))

# Function to get cluster peptides based on cluster_id
get_gibbs_cluster_peptides <- function(cluster_id, peptides, cluster_ids) {
  cluster_peptides <- peptides[cluster_ids == cluster_id]
  one_hot_cluster_peptides <- do.call(rbind, lapply(cluster_peptides, peptide_to_onehot, len))
  return(one_hot_cluster_peptides)
}


## NMDS plot

cluster_colors <- rainbow(num_gibbs_clusters) # Generate a set of colors for clusters
pdf('./nmds_with_clusters.pdf', width=4.5, height=5)
plot(nmds.dat, xlab='nmds1', ylab='nmds2', col = cluster_colors[gibbs_cluster_ids])
legend("topright", legend = unique(gibbs_cluster_ids), col = cluster_colors,
       pch = 16, cex = 0.8,bty = "n")
mtext(side=3, line=0, text="NMDS with Clusters")
dev.off()



## Logos


# Create sequence logo for the entire set of peptides

seq_logo_all <- ggseqlogo(peps,method="bits")

pdf("Sequence_Logo_All.pdf", width = 4, height = 3)
print(seq_logo_all)
dev.off()


# Create a list to store peptides for each cluster
cluster_peptides_list <- vector("list", num_gibbs_clusters)

# Fill the list with peptides for each cluster
for (cluster_id in 1:num_gibbs_clusters) {
  cluster_peptides <- peps[gibbs_cluster_ids == cluster_id]
  cluster_peptides_list[[cluster_id]] <- cluster_peptides
}

# Create sequence logos for each cluster
for (cluster_id in 1:num_gibbs_clusters) {
  # Create the sequence logos
  ## 1) bits mode
  seq_logo <- ggseqlogo(cluster_peptides_list[[cluster_id]], method="bits")
  
  # Save or display the sequence logo as needed
  pdf(paste0("Cluster_", cluster_id, "_Logo_bits.pdf"), width = 4, height = 3)
  print(seq_logo)
  dev.off()
  
  ## 2) probability mode
  seq_logo <- ggseqlogo(cluster_peptides_list[[cluster_id]], method="prob")
  
  # Save or display the sequence logo as needed
  pdf(paste0("Cluster_", cluster_id, "_Logo_prob.pdf"), width = 4, height = 3)
  print(seq_logo)
  dev.off()
}

#-------------