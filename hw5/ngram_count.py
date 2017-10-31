# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        use_local_file = 0
        if use_local_file:
            training_data = "examples/training_data_ex"
            ngram_count_file = 'ngram_count_ex'
        else:
            training_data = args[0]
            ngram_count_file = args[1]
        unigram_dict = {}
        bigram_dict = {}
        trigram_dict = {}
        input_file = open(training_data)
        input_line = input_file.readline().strip('\n')
        while input_line:

            input_line = "<s> " + input_line + " </s>"
            input_line = re.sub(" +", " ", input_line)
            # print(input_line)
            words = input_line.split(" ")
            # print(words, words.__len__())
            # unigrams
            for unigram in words:

                if unigram in unigram_dict:
                    unigram_dict[unigram] += 1
                else:
                    unigram_dict[unigram] = 1
            # bigrams
            for index in range(0, words.__len__()-1):
                bigram = words[index] + ' ' + words[index+1]
                if bigram in bigram_dict:
                    bigram_dict[bigram] += 1
                else:
                    bigram_dict[bigram] = 1
            # trigrams
            for index in range(0, words.__len__()-2):
                trigram = words[index] + ' ' + words[index+1] + ' ' + words[index+2]
                if trigram in trigram_dict:
                    trigram_dict[trigram] += 1
                else:
                    trigram_dict[trigram] = 1
            input_line = input_file.readline().strip('\n')
        input_file.close()
        output_file = open(ngram_count_file, 'w')
        # sorting
        for key, value in sorted(unigram_dict.items(), key=itemgetter(1), reverse=True):
            output_file.write(str(value) + '\t' + str(key) + '\n')
        for key, value in sorted(bigram_dict.items(), key=itemgetter(1), reverse=True):
            output_file.write(str(value) + '\t' + str(key) + '\n')
        for key, value in sorted(trigram_dict.items(), key=itemgetter(1), reverse=True):
            output_file.write(str(value) + '\t' + str(key) + '\n')
        output_file.close()
