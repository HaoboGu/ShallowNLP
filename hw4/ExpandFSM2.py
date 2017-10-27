# !/usr/bin/python

from optparse import OptionParser
import re
import queue


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
                # print(print_seq[0])
            else:
                print_seq.append('('+tran[0]+' ('+tran[1]+' '+tran[2]+'))\n')
        f.writelines(self.final_state+'\n')
        for item in print_seq:
            f.writelines(item)


class FST:
    states = []
    transitions = []  # [(start, end, input, output, probability)]

    def __init__(self, start, final):
        self.start_state = start
        self.final_state = final

    def add_transition(self, tran):
        if tran not in self.transitions:
            self.transitions.append(tran)
            if tran[0] not in self.states:  # start state of this transition
                self.states.append(tran[0])
            if tran[1] not in self.states:
                self.states.append(tran[1])  # end state of this transition

    def move(self, state, state_data, input_symbol):
        """
        Move from current state to next state. Return a set of possible next states
        :param state: current state
        :param state_data: (current_string, current_prob)
        :param input_symbol:
        :return: next_states: [(next_state, (next_string, next_prob)), (), ...]
        """
        next_states = []
        for item in self.transitions:  # [(start, end, input, output, probability)]
            if item[0] == state and item[2] == input_symbol:  # if start state and input symbol of a transition match
                # store next_state's information with tuple(next_state, (next_string, next_prob))
                next_state = (item[1], (str(state_data[0]) + " " + str(item[3]), float(item[4]) * float(state_data[1])))
                next_states.append(next_state)
        return next_states


    def add_states_to_dictionary(self, states, pool):
        """
        Transform states in tuple form and add them to dictionary pool. Eliminate multiple paths pointing to one node.
        :param states: [(state, (string, prob)), (), ...]
        :param pool: current state pool
        :return: dictionary{state: (string, prob)}
        """
        for state in states:
            if state[0] not in pool:
                pool[state[0]] = state[1]
            elif state[1][1] > pool[state[0]][1]:  # if current state's prob is greater than what is in the dictionary
                pool[state[0]] = state[1]
        return pool

    def viterbi(self, input_line):
        """
        viterbi algorithm, decide whether input line is accepted by this fst
        :param input_line:
        :return: (output_string,  best_prob) if the input string is accepted;
                 [] if the input is not accepted
        """
        input_line = input_line.strip('\n')
        symbols = input_line.split(' ')
        state_pool = {}  # {state:([string], prob)}
        state_pool[self.start_state] = ("", 1)
        for symbol in symbols:
            new_pool = {}
            for state in state_pool:
                next_states = self.move(state, state_pool[state], symbol)
                # add to new dictionary and eliminate useless path according to prob
                new_pool = self.add_states_to_dictionary(next_states, new_pool)
            if new_pool.__len__() == 0:
                return []
            state_pool = new_pool
        if self.final_state in new_pool:
            return new_pool[self.final_state]
        else:
            return []

    def write_fst(self, output_filename):
        f = open(output_filename, 'w')
        print_seq = []
        for tran in self.transitions:
            if tran[0] == self.start_state:
                print_seq.insert(0, '('+tran[0]+' ('+tran[1]+' '+tran[2]+' '+tran[3]+'))\n')
                # print(print_seq[0])
            else:
                print_seq.append('('+tran[0]+' ('+tran[1]+' '+tran[2]+' '+tran[3]+'))\n')
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
        if words.__len__() > 0:
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
    Combine lexicon entries and morphological rules into expanded FST in carmel form.
    In expanded FSM, each path corresponds to an entry in the lexicon.
    :param filename_lexicon: lexicon entries
    :param filename_morph: morphological rules
    :return: expanded FST for input lexicon entries
    """
    lexicons = read_lexicons(filename_lexicon)
    morph_rules = create_fsa(filename_morph)
    # then convert FSA to FST
    output_fst = FST(morph_rules.start_state, morph_rules.final_state)
    for word, ty in lexicons:
        for tran in morph_rules.transitions:
            if ty == tran[2]:
                # "-" is added to separate two labels in next steps
                output_fst.add_transition((ty+"_"+word, tran[1], "*e*", word+'/'+ty))  # state(word) -> state(form_end)
                output_fst.add_transition((tran[0], ty+"_"+word[0], word[0], "*e*"))  # state(form_start) -> state(word[0])
        for index in range(1, len(word)-1):
            output_fst.add_transition((ty+"_"+word[:index], ty+"_"+word[:index + 1], word[index], "*e*"))
        index = len(word) - 1
        output_fst.add_transition((ty + "_" + word[:index], ty + "_" + word[:index + 1], word[index], "*e*"))
    for tran in morph_rules.transitions:
        if tran[2] == "*e*":
            output_fst.add_transition((tran[0], tran[1], tran[2], "*e*"))
    return output_fst


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        lexicon_filename = args[0]
        morph_rules_filename = args[1]
        output_filename = args[2]
        # lexicon_filename = "examples/lexicon_ex"
        # morph_rules_filename = "examples/morph_rules_ex"
        # output_filename = "output_fst"
        output_fsm = convert(lexicon_filename, morph_rules_filename)
        output_fsm.write_fst(output_filename)
