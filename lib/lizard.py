import sys

def print_lizard():
    '''
    Prints a lizard.
    '''
    art = r"""
                __
               /..\  
         \|/  (    ) \|/ 
          \\___>  <__//  
             '-.   ,-' 
               |  . \  
               \ `.  \  \|/  
                |  `. |  ||
                 \  : |__||
                __> `.,---'
               |.--'\`.\
                \\   \`.| 
                /|\ - |:|
                      |:|
                      |:|
                      |:/
          --.________,-_/
      """
    return sys.stdout.write(art)


# adapted from hjm
