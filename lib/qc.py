import subprocess
import os
import logging


class QCPipeline:
    def __init__(self, path_handler, command_runner):
        self.path_handler = path_handler
        self.command_runner = command_runner

    def fastqc(self, file_list):
        path_to_reports = self.path_handler.output_subfolder("reports/fastqc")
        logging.info("Starting FastQC...")
        for file in file_list:
            self.command_runner.run(["fastqc", file[0], "-o", path_to_reports])
        logging.info("FastQC completed.")

    def multiqc(self, folder):
        path_to_reports = self.path_handler.output_subfolder("reports/multiqc")
        logging.info("Starting MultiQC...")
        self.command_runner.run(["multiqc", folder, "--outdir", path_to_reports])
        logging.info("MultiQC completed.")

    def scrape_multiqc(self):
        with open(
            os.path.join(
                self.path_handler.output_path,
                "reports/multiqc/multiqc_data/multiqc_general_stats.txt",
            ),
            "r",
        ) as f:
            for line in f.readlines()[1:]:
                line = line.split()
                logging.info(
                    f"Sample {line[0]}:\t Percent duplicates: {str(round(float(line[1]),2))}\t GC-percentage: {str(round(float(line[2]),2))} \t average sequence length: {str(round(float(line[3]),2))}\t Percent fails: {str(round(float(line[4]),2))}\t Total sequences: {str(round(float(line[5]),2))}"
                )

    def run_pipeline(self):
        try:
            file_list = self.path_handler.file_list(self.path_handler.input_path)
            self.fastqc(file_list)
            self.path_handler.update_input(
                os.path.join(self.path_handler.output_path, "reports/fastqc")
            )
            self.multiqc(self.path_handler.input_path)
            self.path_handler.reset_input()
            self.scrape_multiqc()
        except Exception as e:
            logging.error("Error occurred during pipeline execution: %s", str(e))
