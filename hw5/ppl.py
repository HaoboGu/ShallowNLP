# !/usr/bin/python

from optparse import OptionParser
from math import log10


def read_lm(lm_filename):
    lm = open(lm_filename)
    line = lm.readline()  # first line
    lm.readline()
    lm.readline()
    lm.readline()
    ngrams = {}
    while line:
        line = line.strip('\n')
        seq = line.split(' ')
        if seq.__len__() == 4:
            key = seq[3]
            ngrams[key] = float(seq[1])
        elif seq.__len__() == 5:
            key = seq[3] + ' ' + seq[4]
            ngrams[key] = float(seq[1])
        elif seq.__len__() == 6:
            key = seq[3] + ' ' + seq[4] + ' ' + seq[5]
            ngrams[key] = float(seq[1])
        line = lm.readline()
    lm.close()
    return ngrams


def get_p(key, ngrams):
    if key in ngrams:
        return ngrams[key]
    else:
        return 0


def write_prob(num, output_file, key, if_known, if_seen=1, lg_p=0):
    output_file.write(str(num) + ': lg P(' + key + ') = ')
    if if_known:
        if if_seen == 0:
            output_file.write(str(lg_p) + ' (unseen ngrams)\n')
        else:
            output_file.write(str(lg_p) + '\n')
    else:
        output_file.write('-inf (unknown word)\n')


def write_sent_data(output_file, lg_sum, word_num, oov_num):
    output_file.write('1 sentence, ' + str(word_num) + ' words, ' + str(oov_num) + ' OOVs\n')
    cnt = word_num + 1 - oov_num
    ppl = 10 ** (-lg_sum / cnt)
    output_file.write('lgprob=' + str(lg_sum) + ' ppl=' + str(ppl) + '\n\n\n\n')


def write_corpus_data(output_file, sent_num, total_word_num, total_oov_num, total_lg_sum):
    cnt = total_word_num + sent_num - total_oov_num
    output_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
    output_file.write('sent_num=' + str(sent_num) + ' word_num=' +
                      str(total_word_num) + ' oov_num=' + str(total_oov_num) + '\n')
    ave_p = total_lg_sum / cnt
    ppl = 10 ** (-total_lg_sum / cnt)
    output_file.write('lgprob=' + str(total_lg_sum) + ' ave_lgprob=' + str(ave_p) + ' ppl=' + str(ppl) + '\n')


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) != 6:
        print("Error: number of args incorrect")
    else:
        use_local_file = 0
        if use_local_file:
            lm_file = "wsj_sec0_19.lm"
            l1 = 1
            l2 = 0.0
            l3 = 0.0
            test_data_file = "examples/wsj_sec22.word"
            output_filename = "perplexity"
        else:
            lm_file = args[0]
            l1 = float(args[1])
            l2 = float(args[2])
            l3 = float(args[3])
            test_data_file = args[4]
            output_filename = args[5]
        ngrams = read_lm(lm_file)  # get ngram dictionary
        input_file = open(test_data_file)
        line = input_file.readline().strip('\n')
        output_file = open(output_filename, 'w')
        s_lg_sum, s_word_num, s_oov_num = [], [], []
        sent_num = 0
        while line:
            sent_num += 1
            word_num = line.split(' ').__len__()
            line = '<s> ' + line + ' </s>'
            output_file.write("Sent #" + str(sent_num) + ' :' + line + '\n')  # write sentence line
            words = line.split()
            oov_num, lg_sum = 0, 0
            # first word in sentence
            if words[1] in ngrams:
                bigram_key = words[0] + ' ' + words[1]
                bigram_p = get_p(bigram_key, ngrams)
                p = l2 * bigram_p + l1 * ngrams[words[1]]
                lg_p = log10(p)
                lg_sum += lg_p
                write_prob(1, output_file, words[1] + ' | ' + words[0], 1, bigram_p, lg_p)  # known word
            else:
                oov_num += 1
                write_prob(1, output_file, words[1] + ' | ' + words[0], 0)  # unknown word
            # start from 2nd word
            for i in range(2, words.__len__()):
                if words[i] in ngrams:
                    bigram_key = words[i-1] + ' ' + words[i]
                    trigram_key = words[i-2] + ' ' + words[i-1] + ' ' + words[i]
                    bigram_p, trigram_p = get_p(bigram_key, ngrams), get_p(trigram_key, ngrams)
                    p = l1 * ngrams[words[i]] + l2 * bigram_p + l3 * trigram_p
                    lg_p = log10(p)
                    lg_sum += lg_p
                    out_key = words[i] + ' | ' + words[i-2] + ' ' + words[i-1]
                    write_prob(i, output_file, out_key, 1, bigram_p * trigram_p, lg_p)  # known word
                else:
                    oov_num += 1
                    out_key = words[i] + ' | ' + words[i - 2] + ' ' + words[i - 1]
                    write_prob(i, output_file, out_key, 0)  # unknown word
            write_sent_data(output_file, lg_sum, word_num, oov_num)
            s_lg_sum.append(lg_sum)
            s_word_num.append(word_num)
            s_oov_num.append(oov_num)
            line = input_file.readline().strip('\n')
        total_word_num = sum(s_word_num)
        total_oov_num = sum(s_oov_num)
        total_lg_sum = sum(s_lg_sum)
        write_corpus_data(output_file, sent_num, total_word_num, total_oov_num, total_lg_sum)
        output_file.close()

