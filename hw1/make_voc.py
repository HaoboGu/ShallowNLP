# !/usr/bin/python

"""

This script creates a vocabulary from the input text.

"""

import sys
import re


def make_voc():
    """ Process the input_file, generate output_file if use_file is 1.
        If use_file is 0, just use the standard output
    """
    use_file = 0
    if use_file == 1:
        input_file = open('input_file', 'r')
        output_file = open('output_file', 'w')
        line = input_file.readline()
    else:
        line = sys.stdin.readline()
    voc = {}
    while line:
        # line = tokenize(line)
        line = line.rstrip('\n')
        line = re.sub(r"[ ]+", " ", line)
        words = line.split(' ')
        for item in words:
            if item:
                if item in voc:
                    voc[item] += 1
                else:
                    voc[item] = 1
        if use_file == 1:
            line = input_file.readline()
        else:
            line = sys.stdin.readline()
    # Sort the dictionary by its value and then reverse it
    sorted_pair = [(key, voc[key]) for key in sorted(voc, key=voc.get, reverse=True)]
    for item in sorted_pair:
        output_line = item[0] + '\t' + str(item[1])
        if use_file == 1:
            output_file.writelines(output_line + '\n')
        else:
            print(output_line)
    if use_file == 1:
        input_file.close()
        output_file.close()


if __name__ == "__main__":
    make_voc()
