NEOLIZARD
---------

NeoLizard is a package for setting up and running a custom pipeline for neoantigen prediction on NGS samples, VCF or TCGA MAF files.
Pipeline can start from processed vcf/maf/avinput files or from raw sequencing fastq/bam files.


Configuration:

- Make sure annovar is configured, download refgene.txt files manually if download failed.
    perl ./annotate_variation.pl -buildver hg38 -downdb refGene humandb/;\
    perl ./annotate_variation.pl --buildver hg38 --downdb seq humandb/hg38_seq;\
    perl ./retrieve_seq_from_fasta.pl humandb/hg38_refGene.txt -seqdir humandb/hg38_seq -format refGene -outfile humandb/hg38_refGeneMrna.fa
- MHCflurry handles extremely large fasta files poorly, be sure to handle them manually (20MB+)


Depencencies are based on pipeline config:
    -ANNOVAR
    -MHCFLURRY
    -CUTADAPT
    -FASTQC
    -MULTIQC

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
    --mhcflurry_lengths 9

GUI:
----

If preferred, a streamlit python-based web gui is available.
    streamlit run gui.py