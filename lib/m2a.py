#!/usr/bin/env python

## Some of the MAF input lines have missing tabs, this doesn't seem to be a problem in avinput format for ANNOVAR so they are retained.

import os
import logging



class MAFtoAVInputConverter:

    def __init__(self, path_handler):
        self.path_handler = path_handler
    
    def get_indices(self, head):
        cols = [
            "Chromosome",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele1",
            "Tumor_Seq_Allele2",
        ]
        try:
            indices = [head.index(col) for col in cols]
        except ValueError as e:
            logging.error("Error while getting indices: %s", str(e))
            indices = []
        return indices

    def maf_2_avinput(self, file, output_dir):
        outfile_path = os.path.join(output_dir, file[1][:-4] + ".avinput")

        try:
            with open(file[0], "r") as maf, open(outfile_path, "w") as outfile:
                head = None
                for line in maf:
                    if line.startswith("#"):
                        continue

                    items = line.split("\t")
                    if not head:
                        head = items
                        col_titles = [
                            "col_chrom",
                            "col_start",
                            "col_end",
                            "col_ref",
                            "col_t1",
                            "col_t2",
                        ]
                        col_indices = self.get_indices(head)
                        pairs = {}
                        for n, i in enumerate(col_titles):
                            pairs[i] = col_indices[n]
                        continue

                    if items[pairs["col_ref"]] == items[pairs["col_t1"]]:
                        var_allele = pairs["col_t2"]
                    else:
                        var_allele = pairs["col_t1"]

                    # An insertion resulting in frameshift uses different conventions in ANNOVAR --> start and end must be the same (pos left of insertion)
                    if (
                        items[pairs["col_start"]] < items[pairs["col_end"]]
                        and items[pairs["col_t1"]] == "-"
                        and items[pairs["col_t2"]] != "-"
                    ):
                        items[pairs["col_end"]] = items[pairs["col_start"]]

                    annovar_line = "\t".join(
                        [
                            items[pairs["col_chrom"]],
                            items[pairs["col_start"]],
                            items[pairs["col_end"]],
                            items[pairs["col_ref"]],
                            items[var_allele],
                            "\n",
                        ]
                    )

                    outfile.write(annovar_line)

        except Exception as e:
            error_message = f"Error occurred while converting {file[1]} to AVINPUT: {str(e)}"
            logging.error(error_message)

    def run_pipeline(self):
        converted_files=[]
        file_list = self.path_handler.file_list(self.path_handler.input_path)
        output_dir = self.path_handler.output_subfolder("avinput_files")
        for file in file_list:
            logging.info("Converting MAF to AVInput for file: %s", file[1])
            try:
                self.maf_2_avinput(file, output_dir)
                converted_files.append(file[1][:-4] + ".avinput")
                logging.info("Conversion completed for file: %s", file[1])
            except Exception as e:
                logging.error("Error occurred while converting %s to AVINPUT", file[1])
                logging.error(str(e))

        # Remove any incomplete files after the loop
        for file in os.listdir(output_dir):
            try:
                if file not in converted_files:
                    os.remove(os.path.join(output_dir, file))
            except Exception as e:
                logging.error("Error occurred while removing file: %s", file)
                logging.error(str(e))

        logging.info(
            f"MAF to AVINPUT conversion completed for {len(os.listdir(output_dir))} out of {len(file_list)} files."
        )
        self.path_handler.update_input(output_dir)
