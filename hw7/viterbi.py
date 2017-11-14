# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter
import sys
from math import log10


def read_init_probs(hmm_file):
    """
    Read initial probabilities and store them in a dictionary {state:prob}
    :param hmm_file:
    :return: Initial probability dictionary
    """
    init_prob = {}
    line = hmm_file.readline().strip('\n')
    while line:
        line = re.sub('\s+', ' ', line)
        if line == ' ':
            break
        seq = line.strip(' ').split(' ')
        init_prob[seq[0]] = float(seq[1])
        line = hmm_file.readline().strip('\n')
    return init_prob


def read_transitions(hmm_file):
    """
    Read transitions and store them in a dictionary {(from_state, to_state):prob}
    :param hmm_file:
    :return: Transition dictionary
    """
    transitions = {}
    line = hmm_file.readline().strip('\n')
    while line:
        line = re.sub('\s+', ' ', line)
        if line == ' ':
            break
        seq = line.strip(' ').split(' ')
        transitions[(seq[0], seq[1])] = float(seq[2])
        line = hmm_file.readline()

    return transitions


def read_emissions(hmm_file):
    """
    Read emissions and store them in a dictionary {(current_state, word):prob}
    :param hmm_file:
    :return: Emission dictionary
    """
    emissions = {}
    line = hmm_file.readline().strip('\n')
    while line:
        line = re.sub('\s+', ' ', line)
        if line == ' ':
            break
        seq = line.strip(' ').split(' ')
        if float(seq[2]) > 1:
            print("warning: the prob is not in [0,1] range:"+line)
        else:
            emissions[(seq[0], seq[1])] = float(seq[2])
        line = hmm_file.readline()
    return emissions


def read_hmm(hmm_filename):
    f = open(hmm_filename)
    line = f.readline()
    while line:
        line = re.sub('\s+', ' ', line)
        if line == '\\init ':
            pi = read_init_probs(f)
        elif line == '\\transition ':
            transitions = read_transitions(f)
        elif line == '\\emission ':
            emissions = read_emissions(f)
        line = f.readline()
    return pi, transitions, emissions


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 1
    if use_local_file:
        input_filename = "examples/hmm1"
        test_filename = "examples/test.word"
        output_filename = "sys"
    else:
        input_filename = args[0]
        test_filename = args[1]
        output_filename = args[2]

    pi, transitions, emissions = read_hmm(input_filename)


