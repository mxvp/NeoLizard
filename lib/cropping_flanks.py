import os
import logging


class CroppingFlanksPipeline:
    def __init__(self,path_handler):
        self.path_handler = path_handler

    def parse_header(self, header):
        parts = header.split()
        mutation_info = list(filter(lambda x: x.startswith("p."), parts))[0][2:]
        mutation, pos = None, None
        if "delins" in mutation_info:
            # in case of confirmed del and ins
            try:
                pos = int(mutation_info.split("_")[0][1:])
            except ValueError:
                pos = int(mutation_info.split("delins")[0][1:])
            length = len(mutation_info.split("delins")[1])
            mutation = "indel"
        elif "ins" in mutation_info:
            # in case of insertion
            pos = int(mutation_info.split("_")[0][1:])
            length = len(mutation_info.split("ins")[1])
            mutation = "ins"
        elif "del" in mutation_info:
            # In case of deletion: only position is needed where cleavage occurred
            if "_" in mutation_info:
                pos = int(mutation_info.split("_")[0][1:])
            else:
                pos = int(mutation_info[1:-3])
            mutation = "del"
            length = 0
        elif "fs*" in mutation_info:
            # in case of large mutation: position and length of insertion is needed
            length = int(mutation_info.split("fs*")[1])
            pos = int(mutation_info.split("fs*")[0][1:-1])
            mutation = "indel"
        else:
            # in case of snp: position is needed
            pos = int(mutation_info[1:-1])
            mutation = "snp"
            length = 0

        # Note: python_pos=fasta_pos - 1
        return mutation, pos - 1, length
    
    def crop_sequence(self,seq, pos, flank_length, strip_length):
        left_strip = seq[max(0, pos - strip_length - flank_length) : pos - strip_length]
        right_strip = seq[pos + strip_length + 1 : pos + strip_length + flank_length + 1]
        remaining_left = seq[: max(0, pos - strip_length - flank_length)]
        remaining_right = seq[pos + strip_length + flank_length + 1 :]

        if len(left_strip) < flank_length:
            left_strip = seq[: pos - strip_length]
            remaining_left = ""

        if len(right_strip) < flank_length:
            right_strip = seq[pos + strip_length + 1 :]
            remaining_right = ""

        return left_strip + seq[pos : (pos + strip_length + 1)] + right_strip, (
            remaining_left,
            remaining_right,
        )

    def process_fasta_file(self, input_file, flank_length):
        sequences = []
        cropped_sequences = []
        flanks = []

        with open(input_file, "r") as file:
            current_sequence = ""
            current_header = ""
            for line in file:
                if line.startswith(">"):
                    if current_sequence != "":
                        sequences.append((current_header, current_sequence))
                        current_sequence = ""
                    current_header = line.strip()
                else:
                    current_sequence += line.strip()

            if current_sequence != "":
                sequences.append((current_header, current_sequence))

        for header, sequence in sequences:
            if "WILDTYPE" in header:
                continue
            mutation, pos, length = self.parse_header(header)
            # For compatibility with MHCflurry --> remove last '*'
            sequence = sequence[:-1]
            cropped_sequence, flank = self.crop_sequence(
                sequence, pos, flank_length, length
            )
            # Add filename to header for later identification of neopeptide origins
            header = header + " " + os.path.basename(input_file)
            cropped_sequences.append((header, cropped_sequence))
            flanks.append(flank)

        return cropped_sequences, flanks

    def cropping_flanks_pipeline_run(self, flank_length):
        cropped_sequences = []
        flanks = []
        logging.info("Preparing fasta sequences for MHCflurry...")

        file_list = self.path_handler.file_list(self.path_handler.input_path)
        for file in file_list:
            try:
                processed_sequences, processed_flanks = self.process_fasta_file(
                    file[0], flank_length
                )
                cropped_sequences.extend(processed_sequences)
                flanks.extend(processed_flanks)
            except Exception as e:
                logging.error("Error occurred while processing file: %s", file[0])
                logging.error(str(e))

        logging.info("Fasta sequences are prepared for MHCflurry!")
        return cropped_sequences, flanks
