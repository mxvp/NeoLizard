import os
import logging


class AnnovarPipeline:
    def __init__(self, path_handler, command_runner):
        self.path_handler = path_handler
        self.command_runner = command_runner

    def run_annotate_variation_pipeline(self, commands):
        annotated_files = 0
        commands = [i for i in commands.split(" ")]
        file_list = self.path_handler.file_list(self.path_handler.input_path)
        annotations_path = self.path_handler.output_subfolder("annotations")
        logging.info(
            f"Processing {len(file_list)} files in {self.path_handler.input_path}"
        )
        for file in file_list:
            logging.info(f"Starting annotation of {file[1]}")
            try:
                outfile = os.path.join(annotations_path, file[1][:-8])
                self.command_runner.run(
                    ["perl", "annovar/annotate_variation.pl"]
                    + [file[0]]
                    + ["-out", outfile]
                    + commands
                )
                annotated_files += 1
                logging.info(f"Finished annotation of {file[1]}")
            except Exception as e:
                logging.error("Error occurred while annotating file: %s", file[1])
                logging.error(str(e))
        logging.info(
            f"Finished annotating {annotated_files} out of {len(file_list)} files."
        )

        self.path_handler.update_input(annotations_path)

    def run_coding_change_pipeline(self, commands):
        fasta_files = 0
        commands = [i for i in commands.split(" ")]
        file_list = self.path_handler.file_list(self.path_handler.input_path)
        file_list = [
            file for file in file_list if file[0].endswith(".exonic_variant_function")
        ]
        fastas_path = self.path_handler.output_subfolder("fastas")
        logging.info(
            f"Processing {len(file_list)} files in {self.path_handler.input_path}"
        )
        for file in file_list:
            logging.info(f"Starting annotation of {file[1]}")
            try:
                outfile = os.path.join(fastas_path, file[1])
                self.command_runner.run(
                    ["perl", "annovar/coding_change.pl"]
                    + [file[0]]
                    + ["--outfile", outfile]
                    + commands
                )
                fasta_files += 1
                logging.info(f"Finished annotation of {file[1]}")
            except Exception as e:
                logging.error("Error occurred while annotating file: %s", file[1])
                logging.error(str(e))
        logging.info(
            f"Finished creating fastas for {fasta_files} out of {len(file_list)} files."
        )

        self.path_handler.update_input(fastas_path)
