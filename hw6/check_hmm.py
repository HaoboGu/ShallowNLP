# !/usr/bin/python

from optparse import OptionParser
import re

def check_init(hmm_file, init_num):
    """
    Check initial probabilities
    :param hmm_file:
    :param init_num:
    :return:
    """
    return False

def read_init_probs(hmm_file):
    """
    Read initial probabilities and store them in a dictionary {state:prob}
    :param hmm_file:
    :return: Initial probability dictionary
    """
    init_prob = {}
    line = hmm_file.readline().strip('\n')
    while line:
        line = line.replace('\t', ' ')
        line = re.sub(' +', ' ', line)
        seq = line.strip(' ').split(' ')
        if seq.__len__() == 2:
            init_prob[seq[0]] = float(seq[1])
            line = hmm_file.readline().strip('\n')
        else:
            break


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
        line = line.replace('\t', ' ')
        line = re.sub(' +', ' ', line)
        seq = line.strip(' ').split(' ')
        if seq.__len__() == 3:
            transitions[(seq[0], seq[1])] = float(seq[2])
            line = hmm_file.readline()
        else:
            break
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
        line = line.replace('\t', ' ')
        line = re.sub(' +', ' ', line)
        seq = line.strip(' ').split(' ')
        if seq.__len__() == 3:
            emissions[(seq[0], seq[1])] = float(seq[2])
            line = hmm_file.readline()
        else:
            break
    return emissions


def check_hmm(hmm_filename):
    """
    Check whether hmm file is correct, print the result to standard output.
    We have to check:
        1. Whether the sum of initial probability equals 1
        2. Whether the sum of transition probability equals 1
        3. Whether the sum of emission probability equals 1
        4. Whether the num of states/num of symbol/num of init line/num of trans line/num of emission line equals other
        parts of hmm file
    :param hmm_filename:
    :return:
    """
    f = open(hmm_filename)
    state_num_line = f.readline().strip('\n')
    sym_num_line = f.readline().strip('\n')
    init_num_line = f.readline().strip('\n')
    trans_num_line = f.readline().strip('\n')
    emiss_num_line = f.readline().strip('\n')
    state_num = state_num_line.split('=')[1]
    symbol_num = sym_num_line.split('=')[1]
    init_num = init_num_line.split('=')[1]
    trans_num = trans_num_line.split('=')[1]
    emiss_num = emiss_num_line.split('=')[1]
    line = f.readline()
    while line:
        if line == '\\init\n':
            pi = read_init_probs(f)
        elif line == '\\transition\n':
            transitions = read_transitions(f)
        elif line == '\\emission\n':
            emissions = read_emissions(f)
        line = f.readline()
            # print("other kinds of line")
    states = []
    symbols = []

    for item in transitions:
        if item[0] not in states:
            states.append(item[0])
        if item[1] not in states:
            states.append(item[1])
    for item in emissions:
        if item[0] not in states:
            states.append(item[0])
        if item[1] not in symbols:
            symbols.append(item[1])
    if states.__len__() != int(state_num):
        print('warning: different numbers of state_num: claimed=' + str(state_num) +
              ', read=' + str(states.__len__()))
    else:
        print('state_num=' + str(state_num))

    if symbols.__len__() != int(symbol_num):
        print('warning: different numbers of sym_num: claimed=' + str(symbol_num) +
              ', read=' + str(symbols.__len__()))
    else:
        print('sym_num=' + str(symbol_num))

    if pi.__len__() != int(init_num):
        print('warning: different numbers of init_line_num: claimed=' + str(init_num) +
              ', real=' + str(pi.__len__()))
    else:
        print('init_line_num=' + str(init_num))

    if transitions.__len__() != int(trans_num):
        print('warning: different numbers of trans_line_num: claimed=' + str(trans_num) +
              ', real=' + str(transitions.__len__()))
    else:
        print('trans_line_num=' + str(trans_num))

    if emissions.__len__() != int(emiss_num):
        print('warning: different numbers of emission_line_num: claimed=' + str(emiss_num) +
              ', real=' + str(emissions.__len__()))
    else:
        print('emission_line_num=' + str(emiss_num))

    s_pi = 0
    for item in pi:
        s_pi += pi[item]
    if abs(s_pi - 1) > 0.000000001:
        print('warning: the init_prob_sum is ' + str(s_pi))

    for state in states:
        s_trans = 0
        for item in transitions:
            if item[0] == state:
                s_trans += transitions[item]
        if abs(s_trans - 1) > 0.000000001:  # write in readme
            print('warning: the trans_prob_sum for state ' + str(state) + ' is ' + str(s_trans))

    for state in states:
        s_emiss = 0
        for item in emissions:
            if item[0] == state:
                s_emiss += emissions[item]
        if abs(s_emiss - 1) > 0.000000001:  # write in readme
            print('warning: the emiss_prob_sum for state ' + str(state) + ' is ' + str(s_emiss))
    #
    # print(pi)
    # print(transitions)
    # print(emissions)


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 1
    if use_local_file:
        hmm_file = "examples/hmm_ex2"
    else:
        hmm_file = args[0]

    check_hmm(hmm_file)
