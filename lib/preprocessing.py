import os
import subprocess
# Perform fastqc on .fastq.gz file

def fastqc_single(id):
    try:
        process = subprocess.Popen(
            ['fastqc', f'data/raw/{id}.fastq.gz', '-o', 'reports/fastqc'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())  # Print each line of output in real-time
            
        process.communicate()  # Wait for the process to complete
        
        return None
    except FileNotFoundError:
        return "Fastqc is not properly installed"
    

def fastqc_multi(folder):
    try:
        process = subprocess.Popen(
            ['multiqc', f'reports/{folder}', '--outdir', 'reports/multiqc'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())  # Print each line of output in real-time
            
        process.communicate()  # Wait for the process to complete
        
        return None
    except FileNotFoundError:
        return "Multiqc is not properly installed"
