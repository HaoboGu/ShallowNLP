# !/usr/bin/python

from optparse import OptionParser
import re


def read_lexicons(lexicon_filename):
    """
    Read lexicons from lexicon file
    :param lexicon_filename:
    :return: lexicons
    """
    lexicon = []
    f = open(lexicon_filename)
    line = f.readline()
    while line:
        line = line.strip("\n")
        line = re.sub(" +", " ", line)
        if line:
            words = line.split(" ")
        lexicon.append((words[0], words[1]))
        line = f.readline()
    f.close()
    return lexicon


def read_morph_rules(morph_filename):  # same with read FST ?
    morph_rules = []
    f = open(morph_filename)
    print("read morph:  \n")
    line = f.readline()
    while line:
        line = line.strip("\n")
        if line:
            words = line.split(" ")
        for item in words:
            if item:
                print(item)
        line = f.readline()
    f.close()
    return morph_rules

def convert(lexicon_filename, morph_filename):
    """
    Combine lexicon entries and morphological rules into expanded FSM in carmel form. 
    In expanded FSM, each path corresponds to an entry in the lexicon. 
    :param lexicon_filename: lexicon entries
    :param morph_filename: morphological rules
    :return: expanded FSM for input lexicon entries
    """
    output_fsm = []
    lexicons = read_lexicons(lexicon_filename)
    morph_rules = read_morph_rules(morph_filename)

    return output_fsm

if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        # morph_rules_filename = args[0]
        # lexicon_filename = args[1]
        lexicon_filename = "examples/lexicon_ex"
        morph_rules_filename = "examples/morph_rules_ex"
        output_fsm = convert(lexicon_filename, morph_rules_filename)
        for item in output_fsm:
            print(item)
        # fst = create_fst(fst_filename)
        # # for item in fst.transitions:
        # #     print(item)
        # input_file = open(input_filename)
        # input_line = input_file.readline()
        # while input_line:
        #     input_line = input_line.strip('\n')
        #     x = fst.viterbi(input_line)
        #     if x:
        #         prob = "%g" % (x[1])
        #         print(input_line, " => ", x[0].strip(' '), prob)
        #     else:
        #         print(input_line, " => *none* 0")
        #     input_line = input_file.readline()

