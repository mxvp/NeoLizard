NeoLizard is a package for setting up and running a custom pipeline for neoantigen prediction on NGS samples or TCGA MAF files.

Pipeline can start from processed vcf/maf/avinput files or from raw sequencing fastq/bam files.

Flags:
    --input: Input file(s) path, required.
    --output: Provide output folder path. If none is specified, current working directory is used.
    --qc: Perform QC on raw sequencing data using fastqc and multiqc
    --m2a: Convert MAF to AVINPUT
    --cutadapt: Perform cutadapt on raw sequencing data
        --cutadapt_commands: Provide a string containing the cutadapt flags (excluding input and output) e.g. '-m 10 -q 20 -j 4', required.
        --cutadapt_remove: Dynamically remove original file(s)

Examples: 

    python3 Neolizard.py 
        --input testing_area/srr 
        --output testing_area 
        --cutadapt 
        --cutadapt_commands '-m 10 -q 20 -j 4'
        --cutadapt_remove
