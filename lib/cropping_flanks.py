def parse_header(header):
    parts = header.split()
    mutation_info = filter(lambda x: x.startswith('p.'), parts)[2:]
    if "del" in mutation_info:
        start_aa = mutation_info.split("_")[0][1:]
        end_aa = mutation_info.split("_")[1].split("del")[0][1:]
        mutation = "deletion"
    if "fs*" in mutation_info:
        # in case of large mutation
        pass
    else:
        # in case of snp
        position = int(mutation_info[1:-1])
        mutated_aa = mutation_info[-1]
        wildtype_aa = mutation_info[0]
        mutation = f"{wildtype_aa}{position}{mutated_aa}"
        start_aa,end_aa = None,None

    return mutation, start_aa, end_aa



def crop_sequence(sequence, start_aa, end_aa, flank_length):
    if start_aa is None or end_aa is None:
        return sequence

    start_index = sequence.find(start_aa)
    end_index = sequence.find(end_aa) + len(end_aa)

    if end_index - start_index > 0:  # Mutation
        cropped_sequence = sequence[max(0, start_index - flank_length):end_index + flank_length]
    else:  # Deletion
        middle_index = (start_index + end_index) // 2
        cropped_sequence = sequence[max(0, middle_index - flank_length):middle_index + flank_length]

    return cropped_sequence


def process_fasta_file(input_file, output_file, flank_length):
    sequences = []
    shaved_off = []

    with open(input_file, 'r') as file:
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

    with open(output_file, 'w') as file:
        for header, sequence in sequences:
            if "WILDTYPE" in header:
                continue

            mutation, start_aa, end_aa = parse_header(header)
            cropped_sequence = crop_sequence(sequence, start_aa, end_aa, flank_length)
            file.write(header + "\n")
            file.write(cropped_sequence.replace("*", "") + "\n")

            if start_aa is not None and end_aa is not None:
                shaved_off.append((sequence[:sequence.find(start_aa)], sequence[sequence.find(end_aa) + len(end_aa):]))

    return shaved_off


# Example usage:
input_file = 'testing_area/0eaa3a5b-268a-4234-ae6e-408813a10bdf.wxs.aliquot_ensemble_masked_out.fasta'
output_file = 'testing_area/cropped_sequences.fasta'
flank_length = 5

shaved_off = process_fasta_file(input_file, output_file, flank_length)
print('Shaved off sequences:', shaved_off)




sequences = []
shaved_off = []
with open(input_file, 'r') as file:
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

