#!/usr/bin/env python

## EXTRACTING ALL THE .MAF FILES FROM THE GDC DOWNLOAD FOLDER

import os
import shutil
import gzip

def expand_tcga_mafs(source_dir:str,dest_dir:str)->None:
    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Iterate over the files in the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.maf.gz'):
                # Create the source and destination file paths
                source_file = os.path.join(root, file)
                destination_file = os.path.join(dest_dir, file)

                # Copy the file to the destination directory
                shutil.copy2(source_file, destination_file)

                print(f"Copied {file} to folder B")

                # Gunzip the file
                unzipped_file = os.path.splitext(destination_file)[0]  # Remove .gz extension
                with gzip.open(destination_file, 'rb') as f_in:
                    with open(unzipped_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                print(f"Gunzipped {file} in folder B")