import os
import logging
import shutil


class CutadaptPipeline:
    '''
    Pipeline for performing Cutadapt on fastq files.
    '''
    def __init__(
        self,
        path_handler,
        command_runner,
    ):
        self.path_handler = path_handler
        self.command_runner = command_runner

    def run_cutadapt_pipeline(self, commands, remove:bool):
        '''
        Runs the pipeline by using the command_runner for launching a subprocess.
        '''
        processed_files = 0
        commands = [i for i in commands.split(" ")]
        processed_path = self.path_handler.output_subfolder("processed")
        file_list = self.path_handler.file_list(self.path_handler.input_path)
        logging.info(
            f"Processing {len(file_list)} files in {self.path_handler.input_path}"
        )

        for file in file_list:
            logging.info(f"Starting trimming of {file[1]}")
            try:
                outfile = os.path.join(processed_path, file[1])
                self.command_runner.run(
                    ["cutadapt"] + commands + ["-o", outfile] + [file[0]]
                )
                processed_files += 1
                logging.info(f"Finished trimming of {file[1]}")
            except Exception as e:
                logging.error("Error occurred while trimming file: %s", file[1])
                logging.error(str(e))
        logging.info(
            f"Finished trimming {processed_files} out of {len(file_list)} files."
        )

        if remove:
            try:
                shutil.rmtree(self.path_handler.input_path)
            except NotADirectoryError:
                os.remove(self.path_handler.input_path)

        self.path_handler.update_input(processed_path)

        logging.info("Preprocessing with Cutadapt completed!")
