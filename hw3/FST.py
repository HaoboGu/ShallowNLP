# !/usr/bin/python

from optparse import OptionParser
import re


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

    # def find_epsilon_closure(self, current_states):
    #     """ Find epsilon closure for states in current state_pool, add additional states (with prob and output_string)
    #     in state pool. """
    #
    #     q = queue.Queue()
    #     # current_states = [(state, (string, prob)), (), ...]
    #     for state in current_states:
    #         # put tuple(state, (current_string, current_prob)) in queue
    #         q.put(state)  #
    #     while not q.empty():
    #         current = q.get()
    #         if current not in current_states:
    #             # in epsilon closure, multiple paths to one node are allowed
    #             # multiple paths will be eliminated outside of this method
    #             current_states.append(current)
    #         next_epsilon_states = self.move(current[0], current[1], "*e*")
    #         for item in next_epsilon_states:
    #             q.put(item)
    #     return current_states

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


def parse_arc(sequence, is_first):
    words = sequence.split(' ')
    words = [word.strip("(") for word in words if word.strip("(")]
    words = [word.strip(")") for word in words if word.strip(")")]
    if is_first and words.__len__() == 4:  # with start state but without prob
        words.append(1)
        return words
    elif is_first and words.__len__() == 5:  # with start state and prob
        return words
    elif not is_first and words.__len__() == 3:  # without start state and prob
        words.append(1)
        return words
    elif not is_first and words.__len__() == 4:  # without start state but with prob
        return words
    else:
        print("Error: input line is illegal")


def parse_line(line):
    line = re.sub(" +", " ", line)
    line = re.sub("\) \(", "\n", line)
    arcs = line.split('\n')
    transitions = []
    info = parse_arc(arcs[0], True)  # parse first node (with start state)
    start = info[0]
    transitions.append((start, info[1], info[2], info[3], info[4]))
    for arc in arcs[1:]:
        info = parse_arc(arc, False)
        transitions.append((start, info[0], info[1], info[2], info[3]))  # nodes in one line share one start state
    return transitions


def create_fst(fst_filename):
    f = open(fst_filename)
    line = f.readline()
    final_state = line.strip("\n")  # First line is final state
    line = f.readline().strip("\n")  # Second line have start state
    transitions = parse_line(line)
    fst = FST(transitions[0][0], final_state)  # get start state from transitions
    for tran in transitions:
        fst.add_transition(tran)
    line = f.readline().strip("\n")
    while line:
        transitions = parse_line(line)
        for tran in transitions:
            fst.add_transition(tran)
        line = f.readline().strip("\n")
    f.close()
    return fst


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        # fst_filename = "wfst2"
        # input_filename = 'ex2'
        fst_filename = args[0]
        input_filename = args[1]
        fst = create_fst(fst_filename)
        # for item in fst.transitions:
        #     print(item)
        input_file = open(input_filename)
        input_line = input_file.readline()
        while input_line:
            input_line = input_line.strip('\n')
            x = fst.viterbi(input_line)
            if x:
                prob = "%g" % (x[1])
                print(input_line, " => ", x[0].strip(' '), prob)
            else:
                print(input_line, " => *none* 0")
            input_line = input_file.readline()

