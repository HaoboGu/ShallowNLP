# !/usr/bin/python

from optparse import OptionParser
import re
import queue
import copy


class FSA:
    states = []
    transitions = []
    symbols = []
    ori_transitions = []

    def __init__(self, start, final):
        self.start_state = start
        self.final_state = final

    def add_transition(self, tran):
        if tran not in self.transitions:
            self.transitions.append(tran)
        if tran[0] not in self.states:
            self.states.append(tran[0])
        if tran[1] not in self.states:
            self.states.append(tran[1])
        if tran[2] not in self.symbols:
            self.symbols.append(tran[2])

    def move(self, start, symbol):
        # Move from start using symbol
        dest = []
        for e in self.transitions:
            if e[0] == start and e[2] == symbol:
                dest.append(e[1])
        # print("no such a link")
        return dest

    def find_ep_closure(self, state):
        closure = []
        q = queue.Queue()
        for item in state:
            closure.append(item)
            q.put(item)
        while not q.empty():
            current_state = q.get()
            if current_state not in closure:
                closure.append(current_state)
            next_states = self.move(current_state, "*e*")
            for item in next_states:
                q.put(item)
        return closure

    def prepare_expand(self):
        self.ori_transitions = self.transitions
        self.transitions = []
        for tran in self.ori_transitions:
            if tran[2] == "*e*":
                self.add_transition(tran)

    def write_fsa(self, output_filename):
        f = open(output_filename, 'w')
        print_seq = []
        for tran in self.transitions:
            if tran[0] == self.start_state:
                print_seq.insert(0, '('+tran[0]+' ('+tran[1]+' '+tran[2]+'))\n')
                print(print_seq[0])
            else:
                print_seq.append('('+tran[0]+' ('+tran[1]+' '+tran[2]+'))\n')
        f.writelines(self.final_state+'\n')
        for item in print_seq:
            f.writelines(item)


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


def parse_line(line):
    line = re.sub(" +", " ", line)
    line = re.sub("\) \(", "\n", line)
    arcs = line.split('\n')
    transitions = []
    info = parse_arc(arcs[0], True)  # parse first node (with start state)
    start = info[0]
    transitions.append((start, info[1], info[2]))
    for arc in arcs[1:]:
        info = parse_arc(arc, False)
        transitions.append((start, info[0], info[1]))  # nodes in one line share one start state
    return transitions


def parse_arc(sequence, is_first):
    words = sequence.split(' ')
    words = [word.strip("(") for word in words if word.strip("(")]
    words = [word.strip(")") for word in words if word.strip(")")]
    if is_first and words.__len__() == 3:  # with start state
        return words
    elif not is_first and words.__len__() == 2:  # without start state and prob
        return words
    else:
        print("Error: input line is illegal")


def create_fsa(fsa_filename):
    f = open(fsa_filename)
    line = f.readline()
    final_state = line.strip("\n")  # First line is final state
    line = f.readline().strip("\n")  # Second line have start state
    transitions = parse_line(line)
    fsa = FSA(transitions[0][0], final_state)  # get start state from transitions
    for tran in transitions:
        fsa.add_transition(tran)
    line = f.readline().strip("\n")
    while line:
        transitions = parse_line(line)
        for tran in transitions:
            fsa.add_transition(tran)
        line = f.readline().strip("\n")
    f.close()
    return fsa


def convert(filename_lexicon, filename_morph):
    """
    Combine lexicon entries and morphological rules into expanded FSM in carmel form. 
    In expanded FSM, each path corresponds to an entry in the lexicon. 
    :param filename_lexicon: lexicon entries
    :param filename_morph: morphological rules
    :return: expanded FSM for input lexicon entries
    """
    lexicons = read_lexicons(filename_lexicon)
    morph_rules = create_fsa(filename_morph)
    output_fsa = copy.deepcopy(morph_rules)
    output_fsa.prepare_expand()
    for word, ty in lexicons:
        for tran in output_fsa.ori_transitions:
            if ty == tran[2]:
                output_fsa.add_transition((word, tran[1], "*e*"))
                output_fsa.add_transition((tran[0], word[0], word[0]))
        for index in range(1, len(word)):
            output_fsa.add_transition((word[:index], word[:index + 1], word[index]))
    return output_fsa


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        # morph_rules_filename = args[0]
        # lexicon_filename = args[1]
        # output_filename = args[2]
        lexicon_filename = "examples/lexicon_ex"
        morph_rules_filename = "examples/morph_rules_ex"
        output_filename = "examples/output_fsm"
        output_fsm = convert(lexicon_filename, morph_rules_filename)
        output_fsm.write_fsa(output_filename)

