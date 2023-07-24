import subprocess
import os


def fastqc_single(file, output):
    path_to_reports = os.path.join(output, "reports/fastqc")
    if not os.path.exists(path_to_reports):
        os.makedirs(path_to_reports)
        print("Created reports/fastqc dir!")
    try:
        process = subprocess.Popen(
            ["fastqc", file, "-o", path_to_reports],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
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


def multiqc(folder, output):
    path_to_reports = os.path.join(output, "reports/multiqc")
    if not os.path.exists(path_to_reports):
        os.makedirs(path_to_reports)
        print("Created reports/multiqc dir!")
    try:
        process = subprocess.Popen(
            ["multiqc", folder, "--outdir", path_to_reports],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
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


def scrape_multiqc(output):
    with open(
        os.path.join(output, "reports/multiqc/multiqc_data/multiqc_general_stats.txt"),
        "r",
    ) as f:
        for line in f.readlines()[1:]:
            line = line.split()
            print(
                f"Sample {line[0]}:\t Percent duplicates: {str(round(float(line[1]),2))}\t GC-percentage: {str(round(float(line[2]),2))} \t average sequence length: {str(round(float(line[3]),2))}\t Percent fails: {str(round(float(line[4]),2))}\t Total sequences: {str(round(float(line[5]),2))}"
            )


def perform_qc(path, output):
    if os.path.isdir(path):
        dir_list = os.listdir(path)
        dir_list = [x for x in dir_list if not x.startswith(".")]
        print(f"Processing {len(dir_list)} files in '", path, "'")
        for file in dir_list:
            fastqc_single(path + "/" + file, output)
        multiqc(os.path.join(output, "reports/fastqc"), output)
    else:
        fastqc_single(path, output)
        multiqc(os.path.join(output, "reports/fastqc"), output)
    scrape_multiqc(output)
    return print("QC completed")
