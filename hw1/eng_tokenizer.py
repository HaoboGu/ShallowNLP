# !/usr/bin/python

"""

This script is a tokenizer used to split texts to words by punctuations/whitespaces. Some phrases won't be splitted.

"""

import sys
import re

def add_whitespace(match):
    return ' ' + match.group(0) + ' '
def tokenize(string, abbrev_file):
    regex = '\W'
    punctuations = ['.', ',', '-', '%', '#', '!', '=', '$', '&']
    pattern = re.compile(regex) # compile a regex to a pattern
    words = string.split(' ')
    splitted = ''
    for item in words:
        if not item:
            continue
        item = pattern.sub(add_whitespace, item)
        splitted = splitted + ' ' + item + ' '
    print(splitted)
    splitted = re.sub(" +", " ", splitted) # delete extra whitespaces
    print(splitted)
    return 1

def create_abbrev_list(abbrev_file):
    f = open(abbrev_file)
    line = f.readline()
    abbrev_list = []
    while line:
        line = line.rstrip('\n')
        abbrev_list.append(line)
        line = f.readline()
    f.close()
    return abbrev_list

def process(abbrev_file):
        """Process the input_file, generate output_file
        """
        use_file = 1
        if use_file == 1:
            input_file = open('input_file','r')
            line = input_file.readline()
        else:
            line = sys.stdin.readline()
        abbrev_list = create_abbrev_list(abbrev_file)
        while line:
            # line = tokenize(line)
            line = line.rstrip('\n')
            # output_line = tokenize(line, abbrev_list)
            if use_file == 1:
                line = input_file.readline()
            else:
                line = sys.stdin.readline()
        if use_file == 1:
            input_file.close()

if __name__ == "__main__":
        from optparse import OptionParser
        
        parser = OptionParser(__doc__)
        options, args = parser.parse_args()
        args = ['abbrev-list']
        if len(args) == 0:
            print("No abbrev-list file!")
        else:
            # process(args[0])    
            tokenize('i love you- ---that asd1#sa', 1)
        # n_lines_from_stdin(n)
