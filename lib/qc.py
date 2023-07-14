import subprocess
import os


def fastqc_single(file):
    path_to_reports='reports/fastqc'
    if not os.path.exists(path_to_reports):
        os.makedirs(path_to_reports)
        print("Created reports/fastqc dir!")
    try:
        process = subprocess.Popen(
            ['fastqc', file, '-o', 'reports/fastqc'],
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
    

def multiqc(folder):
    path_to_reports='reports/multiqc'
    if not os.path.exists(path_to_reports):
        os.makedirs(path_to_reports)
        print("Created reports/multiqc dir!")
    try:
        process = subprocess.Popen(
            ['multiqc', folder, '--outdir', 'reports/multiqc'],
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
    
def scrape_multiqc():
    with open('reports/multiqc/multiqc_data/multiqc_general_stats.txt','r') as f:
        for line in f.readlines()[1:]:
            line=line.split()
            print(f'Sample {line[0]}:\t Percent duplicates: {str(round(float(line[1]),2))}\t GC-percentage: {str(round(float(line[2]),2))} \t average sequence length: {str(round(float(line[3]),2))}\t Percent fails: {str(round(float(line[4]),2))}\t Total sequences: {str(round(float(line[5]),2))}')


def perform_qc(path):
    if os.path.isdir(path):
        dir_list=os.listdir(path)
        dir_list = [x for x in dir_list if not x.startswith('.')]
        print(f"Processing {len(dir_list)} files in '", path,"'")
        for file in dir_list:
            fastqc_single(path+'/'+file)
        multiqc('reports/fastqc')
    else:
        fastqc_single(path)
        multiqc('reports/fastqc')
    scrape_multiqc()
    return print("QC completed")