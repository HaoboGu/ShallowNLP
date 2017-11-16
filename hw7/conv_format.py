# !/usr/bin/python

from optparse import OptionParser
import sys


def convert():
    """
    Read and convert output of viterbi to word/tag format.
    Print result using stdout. In application, the stdout will be redirected to an output file.
    :return:
    """
    use_local_file = 0
    if use_local_file == 1:
        f = open("examples/sys5")
        line = f.readline().strip('\n')
    else:
        line = sys.stdin.readline().strip('\n')
    while line:
        sent, state_seq = line.split(" => ")
        words = sent.split(' ')
        states = state_seq.split(' ')
        out_str = ''
        for i in range(0, words.__len__()):
            word_pos = words[i] + '/' + states[i+1].split('_')[1]
            out_str = out_str + word_pos + ' '
        print(out_str.strip(' '))
        if use_local_file == 1:
            line = f.readline().strip('\n')
        else:
            line = sys.stdin.readline().strip('\n')
    if use_local_file == 1:
        f.close()


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    convert()


