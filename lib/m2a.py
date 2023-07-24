#!/usr/bin/env python

## Some of the MAF input lines have missing tabs, this doesn't seem to be a problem in avinput format for ANNOVAR so they are retained.

import os


def get_indices(head):
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
    except:
        print("Conversion failed")
    return indices


def maf_2_avinput(file, output_dir):
    outfile_path = os.path.join(output_dir, os.path.basename(file)[:-4] + ".avinput")

    with open(file, "r") as maf, open(outfile_path, "w") as outfile:
        head = None
        for line in maf:
            if line.startswith("#"):
                continue

            items = line.split("\t")
            if not head:
                head = items
                try:
                    col_titles = [
                        "col_chrom",
                        "col_start",
                        "col_end",
                        "col_ref",
                        "col_t1",
                        "col_t2",
                    ]
                    col_indices = get_indices(head)
                    pairs = {}
                    for n, i in enumerate(col_titles):
                        pairs[i] = col_indices[n]
                    continue
                except:
                    raise

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


def convert_maf_to_avinput(path, output):
    output_dir = os.path.join(output, "avinput_files")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.isfile(path):
        maf_2_avinput(path, output_dir)
    elif os.path.isdir(path):
        files = os.listdir(path)
        files = [x for x in files if not x.startswith(".")]
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                maf_2_avinput(file_path, output_dir)
