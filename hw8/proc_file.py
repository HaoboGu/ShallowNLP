# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter


def write_result(input_filename, target_label, output_filename, word_dictionary):
    out_f = open(output_filename, 'w')
    out_f.write(input_filename + ' ' + target_label)

    for item in sorted(word_dictionary.items(), key=itemgetter(0)):
        out_f.write(' ' + item[0] + ' ' + str(item[1]))
    out_f.close()


def proc_file(input_filename):
    f = open(input_filename)
    line = f.readline().strip('\n')
    while line:
        line = f.readline().strip('\n')
        # print([line])
    line = f.readline().lower()
    word_dictionary = {}
    while line:
        line = line.strip('\n')
        line = re.sub("[^a-z]+", ' ', line).strip(' ')
        line = re.sub(" +", ' ', line)
        if line:
            words = line.split(' ')
            for word in words:
                if word in word_dictionary:
                    word_dictionary[word] = word_dictionary[word] + 1
                else:
                    word_dictionary[word] = 1
        line = f.readline().lower()
    f.close()
    return word_dictionary


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        input_filename = "examples/20_newsgroups/talk.politics.guns/55094"
        target_label = "c1"
        output_filename = "output_ex"
    else:
        input_filename = args[0]
        target_label = args[1]
        output_filename = args[2]
    word_dictionary = proc_file(input_filename)

    write_result(input_filename, target_label, output_filename, word_dictionary)



