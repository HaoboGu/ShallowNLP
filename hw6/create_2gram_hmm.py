# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter
import sys
from math import log10


def read_ngram(use_local_file):
    unigram_dict, bigram_dict, trigram_dict = {}, {}, {}
    input_file = open('examples/wsj_sec0.word_pos')

    if use_local_file:
        input_line = input_file.readline().strip('\n')
    else:
        input_line = sys.stdin.readline().strip('\n')
    while input_line:
        input_line = "<s>/BOS " + input_line + " <*\\s*>/EOS"
        input_line = re.sub(" +", " ", input_line)
        input_line = input_line.replace('\\/', '*\\*')  # use *\* to replace / in word.
        word_pos_pairs = input_line.split(" ")
        # unigrams
        for unigram in word_pos_pairs:
            unigram = (unigram.split('/')[0], unigram.split('/')[1])
            if unigram in unigram_dict:
                unigram_dict[unigram] += 1
            else:
                unigram_dict[unigram] = 1
        # bigrams
        for index in range(0, word_pos_pairs.__len__() - 1):
            bigram = word_pos_pairs[index] + ' ' + word_pos_pairs[index + 1]
            key1 = word_pos_pairs[index].split('/')[0] + ' ' + word_pos_pairs[index+1].split('/')[0]
            key2 = word_pos_pairs[index].split('/')[1] + ' ' + word_pos_pairs[index + 1].split('/')[1]
            bigram = (key1, key2)
            if bigram in bigram_dict:
                bigram_dict[bigram] += 1
            else:
                bigram_dict[bigram] = 1
        # trigrams
        for index in range(0, word_pos_pairs.__len__() - 2):
            trigram = word_pos_pairs[index] + ' ' + word_pos_pairs[index + 1] + ' ' + word_pos_pairs[index + 2]
            key1 = word_pos_pairs[index].split('/')[0] + ' ' +\
                   word_pos_pairs[index + 1].split('/')[0] + ' ' + word_pos_pairs[index + 2].split('/')[0]
            key2 = word_pos_pairs[index].split('/')[1] + ' ' + word_pos_pairs[index + 1].split('/')[1] \
                   + ' ' + word_pos_pairs[index + 2].split('/')[1]
            trigram = (key1, key2)
            if trigram in trigram_dict:
                trigram_dict[trigram] += 1
            else:
                trigram_dict[trigram] = 1
        if use_local_file:
            input_line = input_file.readline().strip('\n')
        else:
            input_line = sys.stdin.readline().strip('\n')
    if use_local_file:
        input_file.close()
    return unigram_dict, bigram_dict, trigram_dict


def convert_ngram(ngram):
    pos_ngram = {}
    for item in ngram:
        if item[1] in pos_ngram:
            pos_ngram[item[1]] = pos_ngram[item[1]] + ngram[item]
        else:
            pos_ngram[item[1]] = ngram[item]
    return pos_ngram


def cal_initial_prob(pos):
    pi = {}
    for item in pos:
        pi[item] = 0
    if "BOS" in pi:
        pi["BOS"] = 1
    else:
        print("no BOS")
    return pi


def cal_emission_prob(unigrams):  # calculate emission probability, store them in a dictionary
    emission = {}
    state_outsymbol = {}
    for word_pos in unigrams:
        if word_pos[1] not in state_outsymbol:
            state_outsymbol[word_pos[1]] = {}
            state_outsymbol[word_pos[1]][word_pos[0]] = unigrams[word_pos]
        elif word_pos[0] in state_outsymbol[word_pos[1]]:
            state_outsymbol[word_pos[1]][word_pos[0]] = state_outsymbol[word_pos[1]][word_pos[0]] + unigrams[word_pos]
        else:
            state_outsymbol[word_pos[1]][word_pos[0]] = unigrams[word_pos]

    for item in state_outsymbol:
        dic = state_outsymbol[item]
        s_count = sum(dic.values())
        for word in dic:
            prob = dic[word]/s_count
            emission[(word, item)] = prob
    return emission


def cal_transition_prob(bigram_dict, unigram_dict):
    # print(unigrams)
    bigram_dict = convert_ngram(bigram_dict)  # convert {(word,pos):count} to {pos:value}
    unigram_dict = convert_ngram(unigram_dict)
    transitions = {}
    log_transitions = {}
    for key, value in sorted(bigram_dict.items(), key=itemgetter(1), reverse=True):
        # for bigrams, p(w1|w0) = p(w0,w1)/p(w0)
        pre_state = key.split(' ')[0]
        cur_state = key.split(' ')[1]
        # unigram_key = (key[0].split(' ')[0], pre_state)
        p = value / unigram_dict[pre_state]
        log_p = log10(p)
        transitions[(pre_state, cur_state)] = p
        log_transitions[(pre_state, cur_state)] = log_p
    return transitions, log_transitions


def write_header(out_file, state_num, symbol_num, init_line, trans_line, emiss_line):
    f = open(out_file, "w")
    f.write("state_num=" + str(state_num) + '\n')
    f.write("sym_num=" + str(symbol_num) + '\n')
    f.write("init_line_num=" + str(init_line) + '\n')
    f.write("trans_line_num=" + str(trans_line) + '\n')
    f.write("emiss_line_num=" + str(emiss_line) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


def write_init(out_file, init_probs):
    f = open(out_file, "a")
    f.write('\\init\n')
    for item in init_probs:
        if init_probs[item] != 0:
            f.write(item + '\t' + str(init_probs[item]) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


def write_trans(out_file, tran_dict):
    f = open(out_file, "a")
    f.write('\\transition\n')
    for item in tran_dict:
        f.write(item[0] + '\t' + item[1] + '\t' + str(tran_dict[item]) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


def write_emission(out_file, emission_dict):
    f = open(out_file, "a")
    f.write('\\emission\n')
    for item in emission_dict:
        f.write(item[1] + '\t' + item[0] + '\t' + str(emission_dict[item]) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        out_hmm = "output.hmm"
    else:
        out_hmm = args[0]

    unigrams, bigrams, trigrams = read_ngram(use_local_file)
    # print(trigrams)
    words = []

    pos = []
    for word_pos in unigrams:
        # word_pos = item.split('/')
        if word_pos[0] not in words:
            words.append(word_pos[0])
        if word_pos[1] not in pos:
            pos.append(word_pos[1])

    pi = cal_initial_prob(pos)
    emission = cal_emission_prob(unigrams)  # emission is a dictionary, {(word, pos):prob}
    transition, log_transition = cal_transition_prob(bigrams, unigrams)
    state_num = pos.__len__()
    symbol_num = words.__len__()
    init_line = pi.__len__()
    trans_line = transition.__len__()
    emiss_line = emission.__len__()
    write_header(out_hmm, state_num, symbol_num, init_line, trans_line, emiss_line)
    write_init(out_hmm, pi)
    write_trans(out_hmm, transition)
    write_emission(out_hmm, emission)


