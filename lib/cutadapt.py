import os
import subprocess

def cutadapt(path,output,cutadapt_commands):
    try:
        process = subprocess.Popen(
            ['cutadapt']+cutadapt_commands+['-o',os.path.join(output,'Processed/',os.path.basename(path)), path],
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

def perform_cutadapt(path,output,cutadapt_commands,cutadapt_remove):
    # Processing the commands
    cutadapt_commands=[i for i in cutadapt_commands.split(' ')]

    # Pathing

    if not os.path.exists(os.path.join(output,'Processed')):
        os.mkdir(os.path.join(output,'Processed'))
    if os.path.isdir(path):
        dir_list=os.listdir(path)
        dir_list = [x for x in dir_list if not x.startswith('.')]
        print(f"Processing {len(dir_list)} files in '", path,"'")
        for file in dir_list:
            cutadapt(path+'/'+file,output,cutadapt_commands)
            if cutadapt_remove:
                os.remove(path+'/'+file)
        if cutadapt_remove:
            os.rmdir(path)
    else:
        cutadapt(path,output,cutadapt_commands)
        if cutadapt_remove:
                os.remove(path)
    return print("Preprocessing with Cutadapt completed!")
    