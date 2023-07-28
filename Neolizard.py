#!/usr/bin/env python
import os
import logging
from lib.logger_config import configure_lib_logger, configure_logger
from lib.argparse_config import parse_the_args
from lib.path_handler import PathHandler
from lib.cmd_runner import CommandRunner
from lib.qc import QCPipeline
from lib.m2a import MAFtoAVInputConverter
from lib.annovar_functions import AnnovarPipeline
from lib.cropping_flanks import CroppingFlanksPipeline
from lib.MHCflurry_prediction import MHCflurryPipeline
from lib.lizard import print_lizard
from lib.cutadapt import CutadaptPipeline

def main():
    '''
    Main function of the NeoLizard pipeline.
    Runs all requested steps.
    '''
    args = parse_the_args()  # Argparse
    os.makedirs(args.output, exist_ok=True)
    logfile = os.path.join(args.output, "NeoLizard.log") # File to write ALL logs to
    configure_logger(logfile)  # Configure the root logger
    configure_lib_logger(logfile) # Configure the logger for lib files

    pathing = PathHandler(args.input, args.output)

    if not pathing.validate_paths():
        logging.error("Invalid input paths. Aborting!")
        return

    command_runner = CommandRunner()

    for arg, value in vars(args).items():
        if arg == "qc" and value == True:
            # perform qc
            qc_pipeline = QCPipeline(pathing, command_runner)
            qc_pipeline.run_pipeline()

        if arg == "cutadapt" and value == True:
            # Perform cutadapt
            cutadapt_pipeline = CutadaptPipeline(pathing,command_runner)
            cutadapt_pipeline.run_cutadapt_pipeline(args.cutadapt_commands,args.cutadapt_remove)

        if arg == "cmd" and value != None:
            # Perform custom command
            output_folder = pathing.output_subfolder(value[0][0]) # Cmd is a list of lists. Every list contains the requested string.
            command_runner.configure_command(
                pathing.input_path, output_folder, value[0]
            )
            pathing.update_input_input(output_folder)
            args.cmd[0].pop(0)

        if arg == "m2a" and value == True:
            # Perform MAF to AVInput conversion
            m2a_pipeline = MAFtoAVInputConverter(pathing)
            m2a_pipeline.run_pipeline()

            # Gather sample names and mutation names here (filename to "." and filename to ".  + lineX")

        if arg == "annovar_annotate_variation" and value == True:
            # Perform annovar_annotate
            annovar_pipeline = AnnovarPipeline(pathing, command_runner)
            annovar_pipeline.run_annotate_variation_pipeline(
                args.annovar_annotate_variation_commands
            )

        if arg == "annovar_coding_change" and value == True:
            # Perform annovar_coding change
            annovar_pipeline = AnnovarPipeline(pathing, command_runner)
            annovar_pipeline.run_coding_change_pipeline(
                args.annovar_coding_change_commands
            )

        if arg =="mhcflurry" and value==True:
            # Perform MHCflurry binding affinity prediction. Add_flanks and alleles will be used in pipeline.
            cropping_flanks_pipeline = CroppingFlanksPipeline(pathing)
            flank_length = min(args.peptide_lengths) - 1
            sequences, flanks = cropping_flanks_pipeline.cropping_flanks_pipeline_run(flank_length)
            mhcflurry_pipeline = MHCflurryPipeline(pathing)
            mhcflurry_pipeline.run_mhcflurry_pipeline(sequences,flanks,args.peptide_lengths,args.add_flanks,args.alleles)


if __name__ == "__main__":
    main()
    print_lizard()
