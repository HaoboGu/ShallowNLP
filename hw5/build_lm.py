# !/usr/bin/python

from optparse import OptionParser
from operator import itemgetter
from math import log10


def write_data_chunk(unigram_dict, bigram_dict, trigram_dict, output_filename):
    output_file = open(output_filename, 'w')
    output_file.write("\\data\\\n")
    n_token_unigram = sum([int(v) for v in unigram_dict.values()])
    n_token_bigram = sum([int(v) for v in bigram_dict.values()])
    n_token_trigram = sum([int(v) for v in trigram_dict.values()])
    n_type_unigram = unigram_dict.__len__()
    n_type_bigram = bigram_dict.__len__()
    n_type_trigram = trigram_dict.__len__()
    output_file.write("ngram 1: type=" + str(n_type_unigram) + ' token=' + str(n_token_unigram) + '\n')
    output_file.write("ngram 2: type=" + str(n_type_bigram) + ' token=' + str(n_token_bigram) + '\n')
    output_file.write("ngram 3: type=" + str(n_type_trigram) + ' token=' + str(n_token_trigram) + '\n')
    output_file.write('\n')
    output_file.close()
    return (n_type_unigram, n_type_bigram, n_type_trigram), (n_token_unigram, n_token_bigram, n_token_trigram)


def process_unigrams(unigram_dict, n_tokens, output_filename):
    output_file = open(output_filename, 'a')
    output_file.write("\\1-grams:\n")
    for key, value in sorted(unigram_dict.items(), key=itemgetter(1), reverse=True):
        p = value/n_tokens[0]
        log_p = log10(p)
        output_file.write(str(value) + ' ' + str(p) + ' ' + str(log_p) + ' ' + key + '\n')
    output_file.close()


def process_bigrams(bigram_dict, unigram_dict, output_filename):
    output_file = open(output_filename, 'a')
    output_file.write("\\2-grams:\n")
    for key, value in sorted(bigram_dict.items(), key=itemgetter(1), reverse=True):
        # for bigrams, p(w1|w0) = p(w0,w1)/p(w0)
        pre_word = key.split(' ')[0]
        p = value / unigram_dict[pre_word]
        log_p = log10(p)
        output_file.write(str(value) + ' ' + str(p) + ' ' + str(log_p) + ' ' + key + '\n')
    output_file.close()


def process_trigrams(trigram_dict, bigram_dict, output_filename):
    output_file = open(output_filename, 'a')
    output_file.write("\\3-grams:\n")
    for key, value in sorted(trigram_dict.items(), key=itemgetter(1), reverse=True):
        # for bigrams, p(w1|w0) = p(w0,w1)/p(w0)
        words = key.split(' ')
        bigram = words[0] + ' ' + words[1]
        p = value / bigram_dict[bigram]
        log_p = log10(p)
        output_file.write(str(value) + ' ' + str(p) + ' ' + str(log_p) + ' ' + key + '\n')
    output_file.close()


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        use_local_file = 1
        if use_local_file:
            lm_file = "lm"
            ngram_count_file = 'examples/ngram_count_ex'
        else:
            training_data = args[0]
            ngram_count_file = args[1]
        unigram_dict, bigram_dict, trigram_dict = {}, {}, {}
        input_file = open(ngram_count_file)
        input_line = input_file.readline().strip('\n')
        unigram_dict, bigram_dict, trigram_dict = {}, {}, {}
        while input_line:
            words = input_line.split("\t")
            if words[1].split(' ').__len__() == 1:
                unigram_dict[words[1]] = int(words[0])
            elif words[1].split(' ').__len__() == 2:
                bigram_dict[words[1]] = int(words[0])
            elif words[1].split(' ').__len__() == 3:
                trigram_dict[words[1]] = int(words[0])
            input_line = input_file.readline().strip("\n")
        input_file.close()
        n_types, n_tokens = write_data_chunk(unigram_dict, bigram_dict, trigram_dict, lm_file)
        process_unigrams(unigram_dict, n_tokens, lm_file)
        process_bigrams(bigram_dict, unigram_dict, lm_file)
        process_trigrams(trigram_dict, bigram_dict, lm_file)




