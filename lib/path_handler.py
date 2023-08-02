import os
import logging
import sys

class PathHandler:
    '''
    Class for handling the general dir paths.
    '''
    def __init__(self, input_path, output_path):
        '''
        Input and output paths will be initiated as absolute paths.
        '''
        if not os.path.exists(input_path):
            logging.info(f"The specified input file/folder '{input_path}' does not exist. Aborting!")
            sys.exit(1)

        self.main_input_path = os.path.abspath(input_path)
        self.main_output_path = os.path.abspath(output_path)

        self.input_path = os.path.abspath(input_path)
        self.output_path = os.path.abspath(output_path)

    def output_subfolder(self,dir_name:str)->str:
        '''
        Output subfolder will be returned and created if it doesn't exist.
        '''
        dir = os.path.join(self.output_path,dir_name)
        if not os.path.exists(dir):
            os.makedirs(os.path.join(self.output_path,dir_name))
            logging.info(f"Subfolder '{dir}' created.")
        return dir

    def file_list(self,path:str)->list:
        '''
        Returns list of tuples containing paths and filenames of all files.
        '''
        if not os.path.exists(path):
            logging.error(f"The specified input file/folder '{path}' does not exist. Aborting!")
            sys.exit(1)
        elif os.path.isdir(path):
            dir_list = os.listdir(path)
            dir_list = [(os.path.join(path,x),x) for x in dir_list if not x.startswith(".")]
            logging.info(f"Processing {len(dir_list)} files in '{path}'")
            return dir_list
        elif os.path.isfile(path):
            return [(path, os.path.basename(path))]
    
    def update_input(self,path:str):
        '''
        Update the general input path.
        '''
        if not os.path.exists(path):
            logging.error(f"The specified input file/folder '{path}' does not exist. Aborting!")
            sys.exit(1)
        path = os.path.abspath(path)
        self.input_path = os.path.abspath(path)

    def reset_input(self):
        '''
        Reset the general input path.
        '''
        self.input_path = self.main_input_path
    
    def update_output(self,path:str):
        '''
        Update the general output path.
        '''
        if not os.path.exists(path):
            logging.error(f"The specified input file/folder '{path}' does not exist. Aborting!")
            sys.exit(1)
        path = os.path.abspath(path)
        self.output_path = os.path.abspath(path)
    
    def reset_output(self):
        '''
        Reset the general output path.
        '''
        self.output_path = self.main_output_path

    def validate_paths(self)->bool:
        '''
        Validate the general input and output path.
        '''
        if not os.path.exists(self.input_path):
            logging.error(f"The specified input file/folder '{self.input_path}' does not exist.")
            return False
        if not os.path.exists(self.output_path):
            logging.error(f"The specified output folder '{self.output_path}' does not exist.")
            return False
        return True