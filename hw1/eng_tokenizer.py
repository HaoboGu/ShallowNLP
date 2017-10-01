#!/usr/bin/python

"""%prog [--help] [N]

This script prints the first N lines from STDIN.  If N is not specified, STDIN
is printed until exhausted."""

import sys


def tokenizer(abbrev_file):
        """Print the first n lines from STDIN
        """
        line = sys.stdin.readline()
        while line:
            # TODO: tokenize the line
            # line = tokenize(line)
            line = line.rstrip('\n')
            print(line)
            line = sys.stdin.readline()

if __name__ == "__main__":
        from optparse import OptionParser
        
        parser = OptionParser(__doc__)
        options, args = parser.parse_args()
        if len(args) == 0:
            print("No abbrev-list file!")
        else:
            tokenizer(args[0])    
        # n_lines_from_stdin(n)
