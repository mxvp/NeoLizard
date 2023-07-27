import os
import logging
import subprocess
import pkg_resources


class HLAPipeline:
    '''
    Pipeline for processing HLA types from the PanCancer tsv file and performing HLA-typing on raw data.
    '''
    def __init__(self, path_handler, command_runner):
        self.path_handler = path_handler
        self.command_runner = command_runner

    def process_TCGA_HLA(self, custom_source=None)->dict:
        '''
        Function for reading the PanCancer tsv file and storing all MHC alleles per classifier in a dict.
        '''
        if custom_source != None:
            if not os.path.isfile(custom_source):
                error_message = f"Custom source file not found: {custom_source}"
                logging.error(error_message)
                raise FileNotFoundError(error_message)
            source_file = custom_source
        else:
            try:
                source_file = pkg_resources.resource_filename(
                    "neolizard.resources", "panCancer_hla.tsv"
                )
            except Exception as e:
                error_message = f"Unable to find panCancer_hla.tsv' source file. Make sure it's in /resources or provide custom path."
                logging.error(error_message)
                raise FileNotFoundError(error_message)
        HLA_dict = {}
        try:
            with open(source_file, "r") as f:
                for line in f:
                    line = line.strip().split("\t")
                    if len(line) != 2:
                        logging.warning(
                            f"Ignoring line '{line}' with incorrect format."
                        )
                        continue
                    key = line[0]
                    values = line[1].split(",")
                    HLA_dict[key] = values
                logging.info(f"{len(HLA_dict)} HLA alleles retrieved from file.")
        except FileNotFoundError as e:
            logging.error(f"Error while reading file: {e}")
            raise
        except Exception as e:
            logging.error(f"Error occurred during file processing: {e}")
            raise

        return HLA_dict

    