#!/usr/bin/env python
from lib.argparse_config import parse_the_args
from lib.qc import perform_qc
from lib.lizard import print_lizard

def main():
    args=parse_the_args()
    
    if args.qc:
        perform_qc(args.input)
    print_lizard()

if __name__ == '__main__':
    main()
