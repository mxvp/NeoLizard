import os
import subprocess

def cutadapt(path,cutadapt_commands):
    try:
        process = subprocess.Popen(
            ['cutadapt', cutadapt_commands,f'-o Processed/{os.path.basename}', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())  # Print each line of output in real-time
            
        process.communicate()  # Wait for the process to complete
        
        return None
    except FileNotFoundError:
        return "Cutadapt is not properly installed"

def perform_cutadapt(path,cutadapt_commands,cutadapt_remove):
    os.mkdir('Processed')
    if os.path.isdir(path):
        dir_list=os.listdir(path)
        dir_list = [x for x in dir_list if not x.startswith('.')]
        print(f"Processing {len(dir_list)} files in '", path,"'")
        for file in dir_list:
            cutadapt(path+'/'+file,cutadapt_commands)
            if cutadapt_remove:
                os.remove(path+'/'+file)
    else:
        cutadapt(path,cutadapt_commands)
        if cutadapt_remove:
                os.rmdir(path)
    return print("Preprocessing with Cutadapt completed!")