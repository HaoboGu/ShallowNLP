# !/usr/bin/python

from optparse import OptionParser
import re
import time
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
        if float(seq[1]) > 1:
            print("warning: the prob is not in [0,1] range:" + line)
        else:
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
        if float(seq[2]) > 1:
            print("warning: the prob is not in [0,1] range:"+line)
        else:
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
    symbols = {}
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
            symbols[seq[1]] = 1
        line = hmm_file.readline()
    return emissions, symbols


def read_hmm(hmm_filename):
    """
    Read hmm file, store them in 3 dictionaries
    :param hmm_filename:
    :return:Initial probability dictionary(pi), transition dictionary and emission dictionary

    """
    f = open(hmm_filename)
    line = f.readline()
    while line:
        line = re.sub('\s+', ' ', line)
        if line == '\\init ':
            pi = read_init_probs(f)
        elif line == '\\transition ':
            transitions = read_transitions(f)
        elif line == '\\emission ':
            emissions, symbols = read_emissions(f)
        line = f.readline()
    return pi, transitions, emissions, symbols


def read_testfile(test_filename, hmm):
    """
    Read test data. Each line in test_file is an observation.
    :param test_filename:
    :return: a list of observations
    """
    observations = []
    f = open(test_filename)
    line = f.readline().strip('\n')
    while line:
        line = re.sub('\s+', ' ', line)
        seq = line.split(' ')
        for i in range(0, seq.__len__()):
            if seq[i] not in hmm.symbols:
                seq[i] = "<unk>"
        observations.append([seq, line])
        line = f.readline().strip('\n')
    return observations


class HMM:
    def __init__(self, init, trans, emiss, symbols):
        self.pi = init  # {state:prob}
        self.trans = trans  # {(from_state, to_state):prob}
        self.emiss = emiss  # {(state, word): prob}
        self.symbols = symbols  # [symbols]
        self.word_pos = {}
        for item in self.emiss:
            if item[1] not in self.word_pos:
                self.word_pos[item[1]] = [item[0]]
            else:
                self.word_pos[item[1]] = self.word_pos[item[1]] + [item[0]]


def move(hmm, state_pool, word):
    """
    Move from current state to next state according to next emission word.
    :param hmm: hmm model
    :param state_pool: current state pool, format: {state:(string, prob)}
    :param word: next word emitted by next state
    :return: next state pool
    """
    #
    new_state_pool = {}
    for cur_state in state_pool:
        for next_state in hmm.word_pos[word]:
            if (cur_state, next_state) in hmm.trans and (next_state, word) in hmm.emiss:
                lg_p = log10(hmm.emiss[(next_state, word)]) + log10(hmm.trans[(cur_state, next_state)]) \
                       + state_pool[cur_state][1]
                if next_state in new_state_pool:
                    # If several paths to a same state
                    if lg_p > new_state_pool[next_state][1]:
                        # Probability is greater
                        string = state_pool[cur_state][0] + [next_state]
                        new_state_pool[next_state] = (string, lg_p)
                else:
                    string = state_pool[cur_state][0] + [next_state]
                    new_state_pool[next_state] = (string, lg_p)
    return new_state_pool


def viterbi(hmm, line):

    state_pool = {}  # current state pool, format: {state:(string, prob)}
    for init in hmm.pi:
        state_pool[init] = ([init], log10(hmm.pi[init]))
    for word in line:
        state_pool = move(hmm, state_pool, word)  # update state_pool, contains all possible
    if state_pool.__len__() == 0:
        print("none")
        return ()
    else:
        lgs = {}
        for final_state in state_pool:
            lgs[state_pool[final_state][1]] = final_state
        best = lgs[max(lgs.keys())]
        return state_pool[best]


if __name__ == "__main__":
    start = time.time()
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 1
    if use_local_file:
        input_filename = "examples/hmm1"
        test_filename = "examples/test.word"
        output_filename = "examples/sys1"
    else:
        input_filename = args[0]
        test_filename = args[1]
        output_filename = args[2]

    pi, transitions, emissions, symbols = read_hmm(input_filename)
    hmm = HMM(pi, transitions, emissions, list(symbols.keys()))
    test_data = read_testfile(test_filename, hmm)
    f = open(output_filename, 'w')
    for item in test_data:
        re = viterbi(hmm, item[0])
        if re.__len__() == 0:
            out_str = item[1] + " => *NONE*"
            f.write(out_str)
        else:
            out_str = item[1] + " =>"
            for state in re[0]:
                out_str = out_str + ' ' + state
            out_str = out_str + ' ' + str(re[1]) + '\n'
            f.write(out_str)
    f.close()
    end = time.time()
    print(end-start)


