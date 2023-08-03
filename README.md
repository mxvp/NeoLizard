![neolizard logo](https://raw.githubusercontent.com/mxvp/NeoLizard/main/resources/NEO_logo.png)

NeoLizard is a package for setting up and running a custom pipeline for neoantigen prediction.  
The pipeline can start from processed files (vcf/maf/avinput) or from raw sequencing files (fastq/bam).  
Both CLI- and web-application versions are available.

# 1. Setup

## Based on intended pipeline usage, install necessary tools:
    -FASTQC
    -MULTIQC
    -CUTADAPT
    -ANNOVAR
    -MHCFLURRY
    -PostgreSQL

## ANNOVAR

- Registration required, download at: https://annovar.openbioinformatics.org/en/latest/user-guide/download
- After downloading, move ANNOVAR into the NeoLizard dir or add to path.
- Assure ANNOVAR works as expected: https://annovar.openbioinformatics.org/en/latest/user-guide/startup
- Make sure ANNOVAR is configured with desired reference genome, I advise downloading the official hg38.
    - perl ./annotate_variation.pl -buildver hg38 -downdb refGene humandb/
    - perl ./annotate_variation.pl --buildver hg38 --downdb seq humandb/hg38_seq
    - perl ./retrieve_seq_from_fasta.pl humandb/hg38_refGene.txt -seqdir humandb/hg38_seq -format refGene -outfile humandb/hg38_refGeneMrna.fa
- Note: downloads often fail. If necessary, please download all failed downloads manually from https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips.

## MHCflurry

- Install the package:
```
$ pip install mhcflurry
```
- If you don't already have it, you will also need to install tensorflow version 2.2.0 or later. On most platforms you can do this with:
```
$ pip install tensorflow
```
or if you're using an Apple silicon based processor (M1,M2,M3):
```
$ pip install tensorflow-macos
```
- Fetch the necessary model:
```
$ mhcflurry-downloads fetch models_class1_presentation
```
- Note: MHCflurry handles extremely large fasta files poorly (20MB+), be sure to handle them manually for low RAM systems.

## PostgreSQL

- If data collection in a relational database format is intended, please install PostgreSQL.
- A new database will be created by NeoLizard for data storage and classification if needed.

# 2. Usage


COMMAND LINE INTERFACE:
-----------------------

Flags:
    --input: Input file(s) path, required.
    --output: Provide output folder path. If none is specified, current working directory is used.
    --qc: Perform QC on raw sequencing data using fastqc and multiqc
    --cutadapt: Perform cutadapt on raw sequencing data
        --cutadapt_commands: Provide a string containing the cutadapt flags (excluding input and output) e.g. '-m 10 -q 20 -j 4', required.
        --cutadapt_remove: Dynamically remove original file(s)
    --m2a: Convert MAF to AVINPUT
    --mhcflurry: perform MHCflurry neo-antigen prediction on fasta files
        --add_flanks: Generate peptides of given length(s) in sequence and test them --> can add flanks for improved accuracy
        --peptide_lengths: Enter length(s) of peptides to scan for.
        --alleles: Enter HLA alleles.
    --cmd: Add custom commands. Make sure to add as a string!! e.g. " --cmd 'a_module -m 10 -q 20 -j 4' "

Examples: 

    # performing QC and cutadapt
    python3 Neolizard.py 
        --input testing_area/srr 
        --output testing_area 
        --qc
        --cutadapt 
        --cutadapt_commands '-m 10 -q 20 -j 4'
        --cutadapt_remove


    # starting from maf files
    python3 Neolizard.py 
    --input testing_area/maf_files 
    --output testing_area 
    --m2a 
    --annovar_annotate_variation 
    --annovar_annotate_variation_commands "-build hg38 -dbtype refGene annovar/humandb/ --comment" 
    --annovar_coding_change 
    --annovar_coding_change_commands "annovar/humandb/hg38_refGene.txt annovar/humandb/hg38_refGeneMrna.fa --includesnp --onlyAltering --alltranscript --tolerate"
    --mhcflurry
    --TCGA_alleles

GUI:
----

If preferred, a streamlit python-based web gui is available.
    streamlit run gui.py