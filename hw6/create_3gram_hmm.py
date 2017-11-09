# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter
import sys
from math import log10

def read_ngram(use_local_file):
    """
    Read , process and return ngrams
    :param use_local_file: 1 means we are using local file, 0 means we must specify the input file in commands
    :return: ngram dictionaries {(word,pos):count}
    """
    unigram_dict, bigram_dict, trigram_dict = {}, {}, {}
    if use_local_file:
        input_file = open('examples/wsj_sec0.word_pos')
        input_line = input_file.readline().strip('\n')
    else:
        input_line = sys.stdin.readline().strip('\n')
    while input_line:
        input_line = "<s>/BOS " + input_line + " <*s*>/EOS"
        input_line = re.sub(" +", " ", input_line)
        # use *\* to replace / in word, because we split word and pos using /
        input_line = input_line.replace('\\/', '*\\*')
        word_pos_pairs = input_line.split(" ")
        # unigrams
        for unigram in word_pos_pairs:
            # when we are writing keys, *\* in word part should be replaced back to /
            unigram = (unigram.split('/')[0].replace('*\\*', '\\/'), unigram.split('/')[1])
            if unigram in unigram_dict:
                unigram_dict[unigram] += 1
            else:
                unigram_dict[unigram] = 1
        # bigrams
        for index in range(0, word_pos_pairs.__len__() - 1):
            key1 = word_pos_pairs[index].split('/')[0] + ' ' + word_pos_pairs[index+1].split('/')[0]  # word bigram
            key2 = word_pos_pairs[index].split('/')[1] + ' ' + word_pos_pairs[index + 1].split('/')[1]  # pos bigram
            # when we are writing keys, *\* in word part should be replaced back to /
            key1 = key1.replace('*\\*', '\\/')
            bigram = (key1, key2)
            if bigram in bigram_dict:
                bigram_dict[bigram] += 1
            else:
                bigram_dict[bigram] = 1
        # trigrams
        for index in range(0, word_pos_pairs.__len__() - 2):
            key1 = word_pos_pairs[index].split('/')[0] + ' ' + word_pos_pairs[index + 1].split('/')[0] + \
                   ' ' + word_pos_pairs[index + 2].split('/')[0]  # word trigram
            key2 = word_pos_pairs[index].split('/')[1] + ' ' + word_pos_pairs[index + 1].split('/')[1] + \
                   ' ' + word_pos_pairs[index + 2].split('/')[1]  # pos trigram
            # when we are writing keys, *\* in word part should be replaced back to /
            key1 = key1.replace('*\\*', '\\/')
            trigram = (key1, key2)
            # count trigram in dict
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


def read_unknown_words(unknown_filename):
    """
    Read unknown word probabilities into a dictionary.
    :param unknown_filename:
    :return: A dictionary {POS:probability}
    """
    unknown = {}
    f = open(unknown_filename)
    line = f.readline().strip('\n')

    while line:
        pos, prob = line.split(' ')
        unknown[pos] = float(prob)
        line = f.readline().strip('\n')
    f.close()
    return unknown


def convert_ngram(ngram):
    """
    Convert ngram dictionary in (word, pos):count form to pos:count form
    :param ngram: Input ngram dictionary in (word, pos):count form
    :return: pos_ngram dictionary in pos:count form
    """
    pos_ngram = {}
    for item in ngram:
        if item[1] in pos_ngram:
            pos_ngram[item[1]] = pos_ngram[item[1]] + ngram[item]
        else:
            pos_ngram[item[1]] = ngram[item]
    return pos_ngram


def cal_initial_prob(states):
    """
    Calculate initial probability of every pos(which is the state in trigram hmm).
    pi(BOS_BOS) = 1, pi(others) = 0 and we do not include zero items in dictionary.
    :param pos: Input pos list
    :return: Initial probability dictionary
    """
    pi = {}
    if "BOS_BOS" in states:
        pi["BOS_BOS"] = 1
    return pi


def cal_emission_prob(unigrams, unknown, pos_unigrams):  # calculate emission probability, store them in a dictionary
    """
    Calculate emission probabilities. Using unigram to count the probabilities and unknown dictionary to smooth.
    :param unigrams: Input unigrams
    :param unknown: Unknown probabilities of POS
    :return: The emission dictionary {(word, pos):probability}
    """
    pos = list(pos_unigrams.keys())
    emission = {}
    state_outsymbol = {}
    for word_pos in unigrams:
        if word_pos[1] not in state_outsymbol:  # word_pos[1] == pos
            state_outsymbol[word_pos[1]] = {}
            state_outsymbol[word_pos[1]][word_pos[0]] = unigrams[word_pos]
        elif word_pos[0] in state_outsymbol[word_pos[1]]:
            state_outsymbol[word_pos[1]][word_pos[0]] = state_outsymbol[word_pos[1]][word_pos[0]] + unigrams[word_pos]
        else:
            state_outsymbol[word_pos[1]][word_pos[0]] = unigrams[word_pos]

    for item in state_outsymbol:  # item: pos
        dic = state_outsymbol[item]
        s_count = sum(dic.values())
        if item in unknown:  # for tag which doesn't appears in unknown_prob_file, assume that p(unk|tag)=0
            smooth = (1 - unknown[item])
        else:
            smooth = 1
        for word in dic:
            prob = smooth * (dic[word]/s_count)
            for pre_pos in pos:
                key = pre_pos + '_' + item
                emission[(word, key)] = prob
        for item in unknown:
            for pre_pos in pos:
                key = pre_pos + '_' + item
                emission[("<unk>", key)] = unknown[item]
    return emission


def count(ngram_dict, key):
    """
    Get count number from ngrams, if the key is not in ngram_dict, returns 0
    :param ngram_dict:
    :param key:
    :return:
    """
    if key in ngram_dict:
        return ngram_dict[key]
    else:
        return 0


def cal_transition_prob(pos_unigrams, pos_bigrams, pos_trigrams, l1, l2, l3):
    """
    Calculate trigram transition probability
    :param bigram_dict: Input bigram dictionary{(word, pos):count}
    :param unigram_dict: Input unigram dictionary{(word, pos):count}
    :return: Transition probability dictionary {(from_state, to_state):probability}
    """
    possible_trigrams = []
    for item1 in pos_unigrams:
        for item2 in pos_unigrams:
            for item3 in pos_unigrams:
                possible_trigrams.append(item1 + ' ' + item2 + ' ' + item3)
    s_unigram = sum(pos_unigrams.values())
    t = pos_unigrams.__len__()-2
    transitions = {}
    for trigram in possible_trigrams:

        pre_bigram = trigram.split(' ')[0] + ' ' + trigram.split(' ')[1]
        post_bigram = trigram.split(' ')[1] + ' ' + trigram.split(' ')[2]
        cur_unigram = trigram.split(' ')[2]  # trigram = t1_t2_t3, t1 is the first pos, t3 is the current pos
        mid_unigram = trigram.split(' ')[1]
        p1 = count(pos_unigrams, cur_unigram) / s_unigram
        if mid_unigram == "EOS":
            if cur_unigram == "EOS":
                p2 = 1
                p3 = 1
            else:
                p2 = 0
                p3 = 0
        else:  # pos_mid is not EOS
            p2 = count(pos_bigrams, post_bigram) / count(pos_unigrams, mid_unigram)
            if cur_unigram == "BOS":  # current pos is BOS, p3 = 0
                p3 = 0
            elif count(pos_bigrams, pre_bigram) == 0:  # previous bigram is not in training file
                p3 = 1/(t+1)
            else:
                p3 = count(pos_trigrams, trigram) / count(pos_bigrams, pre_bigram)
        #         print(p3)
        # print(trigram, p1, p2, p3)
        p = l1 * p1 + l2 * p2 + l3 * p3
        transitions[trigram] = p

    return transitions


def write_header(out_file, state_num, symbol_num, init_line, trans_line, emiss_line):
    """
    Write header of hmm file
    :param out_file:
    :param state_num:
    :param symbol_num:
    :param init_line:
    :param trans_line:
    :param emiss_line:
    :return:
    """
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
    """
    Write initial probability of hmm
    :param out_file:
    :param init_probs:
    :return:
    """
    f = open(out_file, "a")
    f.write('\\init\n')
    for item in init_probs:
        if init_probs[item] != 0:
            f.write(item + '\t' + str(init_probs[item]) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


def write_trans(out_file, tran_dict):
    """
    Write transition probability of hmm
    :param out_file:
    :param tran_dict:
    :return:
    """
    f = open(out_file, "a")
    f.write('\\transition\n')
    for item in tran_dict:
        seq = item.split(' ')

        f.write(seq[0]+'_'+seq[1] + '\t' + seq[1]+'_'+seq[2] + '\t' + str(tran_dict[item]) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


def write_emission(out_file, emission_dict):
    """
    Write emission probability of hmm
    :param out_file:
    :param emission_dict:
    :return:
    """
    f = open(out_file, "a")
    f.write('\\emission\n')
    for item in emission_dict:
        word = item[0].replace('<*s*>', '</s>')
        f.write(item[1] + '\t' + word + '\t' + str(emission_dict[item]) + '\n')
    f.write('\n')
    f.write('\n')
    f.close()


def generate_states(unigrams):
    """
    Using input unigram to generate states in trigram hmm. The state list should contain all possible POS_pair,
    not only POS pairs appeared in training file
    :param bigrams: Input bigrams
    :return: List of states, each state is consist of 2 POS: [POS1_POS2]
    """
    states = []
    for item in unigrams:
        for item2 in unigrams:
            states.append(item + '_' + item2)
    return states


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        out_hmm = "q2.hmm"
        l1 = 0.1
        l2 = 0.1
        l3 = 0.8
        unknown_filename = "examples/unk_prob_sec22"
    else:
        out_hmm = args[0]
        l1 = float(args[1])
        l2 = float(args[2])
        l3 = float(args[3])
        unknown_filename = args[4]

    unigrams, bigrams, trigrams = read_ngram(use_local_file)
    pos_unigrams = convert_ngram(unigrams)
    pos_bigrams = convert_ngram(bigrams)
    pos_trigrams = convert_ngram(trigrams)
    unknown = read_unknown_words(unknown_filename)
    states = generate_states(pos_unigrams)
    pi = cal_initial_prob(states)
    emission = cal_emission_prob(unigrams, unknown, pos_unigrams)  # emission is a dictionary, {(word, pos):prob}
    # transition, log_transition = cal_transition_prob(bigrams, unigrams, l1, l2, l3)

    transition = cal_transition_prob(pos_unigrams, pos_bigrams, pos_trigrams, l1, l2, l3)

    words = []
    pos = []
    for word_pos in unigrams:
        if word_pos[0] not in words:
            words.append(word_pos[0])
        if word_pos[1] not in pos:
            pos.append(word_pos[1])
    words.append('<unk>')
    state_num = states.__len__()  # State contains BOS and EOS
    symbol_num = words.__len__()  # Symbol contains <s> and </s>

    init_line = pi.__len__()  # Only non-zero initial probability
    trans_line = transition.__len__()  # Contains transitions from BOS and to EOS
    emiss_line = emission.__len__()  # Contains emissions from EOS but BOS
    write_header(out_hmm, state_num, symbol_num, init_line, trans_line, emiss_line)
    write_init(out_hmm, pi)
    write_trans(out_hmm, transition)
    write_emission(out_hmm, emission)


