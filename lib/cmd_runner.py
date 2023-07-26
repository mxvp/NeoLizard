import subprocess
import logging

class CommandRunner:
    def __init__(self):
        pass


    def run(self, command):
        '''
        Run command using subprocess, will log everything.
        '''
        logging.info(f"Running command: {' '.join(command)}")

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

            while True:
                output = process.stdout.readline()
                if not output and process.poll() is not None:
                    break
                if output:
                    logging.info(output.strip())

            return_code = process.wait()
            if return_code != 0:
                logging.error(f"Command failed with return code {return_code}")

        except Exception as e:
            logging.error(f"Error occurred while running command: {' '.join(command)}")
            logging.error(str(e))

    @ staticmethod 
    def configure_command(self,input,output,cmds:str):
        '''
        Configure command to be run following standard procedure.
        '''
        cmds = [i for i in cmds.split(" ")]
        return [cmds[0],'--input',input,'--output',output] + cmds[1:]