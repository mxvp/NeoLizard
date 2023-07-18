import os
import subprocess

def annotate_variation(input,output,commands):
    # Output folder 'annotations'
    if not os.path.exists(os.path.join(output,'annotations')):
        os.mkdir(os.path.join(output,'annotations'))
    output_folder=os.path.join(output,'annotations')

    output_file = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(input))[0]}')

    subprocess.run(['perl', 'annovar/annotate_variation.pl']+[input]+['-out', output_file]+commands)

    return


def coding_change(input,output,commands):
    # Output folder 'fastas'
    if not os.path.exists(os.path.join(output,'fastas')):
        os.mkdir(os.path.join(output,'fastas'))
    output_folder=os.path.join(output,'fastas')

    output_file = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(input))[0]}.fasta')


    subprocess.run(['perl', 'annovar/coding_change.pl']+[input]+['--outfile', output_file]+commands)

    return



def perform_annovar(function,input,output,annovar_commands):
    # Processing the commands
    annovar_commands=[i for i in annovar_commands.split(' ')]
    if os.path.isdir(input):
            dir_list=os.listdir(input)
            dir_list = [x for x in dir_list if not x.startswith('.')]
            print(f"Processing {len(dir_list)} files in '", input,"'")
            if function=='annotate_variation':
                for file in dir_list:
                    annotate_variation(input+'/'+file,output,annovar_commands)
            else:
                for file in dir_list:
                    if file.endswith('.exonic_variant_function'):
                        coding_change(input+'/'+file,output,annovar_commands)
    else:
        if function=='annotate_variation':
            annotate_variation(input+'/'+file,output,annovar_commands)
        else:
            coding_change(input+'/'+file,output,annovar_commands)

    return print("ANNOVAR completed")