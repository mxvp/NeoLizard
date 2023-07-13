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
    
def fastqc_multi(path):
    dir_list=os.listdir(path)
    dir_list = [x for x in dir_list if not x.startswith('.')]
    print(f"Processing {len(dir_list)} files in '", path,"'")
    for file in dir_list:
        fastqc_single(path+'/'+file)

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