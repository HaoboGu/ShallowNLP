# !/usr/bin/python

import queue
from optparse import OptionParser
import re


def parse_arc(line):
    line = re.sub(" +", " ", line)
    words = line.strip('\n').split(' ')
    # print(words)
    start = words[0].strip("(")
    end = words[1].strip("(")
    input_symbol = words[2]
    output_symbol = words[3].strip(")")
    if words.__len__() == 5:
        prob = words[4].strip(")")
    else:
        prob = 1
    return start, end, input_symbol, output_symbol, prob


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
            # print(new_pool)
        if self.final_state in new_pool:
            return new_pool[self.final_state]
        else:
            return []


def create_fst(fst_filename):
    f = open(fst_filename)
    line = f.readline()
    final_state = line.strip("\n")  # First line is final state
    line = f.readline().strip("\n")
    start, end, input_symbol, output_symbol, prob = parse_arc(line)
    fst = FST(start, final_state)
    fst.add_transition((start, end, input_symbol, output_symbol, prob))
    line = f.readline().strip("\n")
    while line:
        start, end, input_symbol, output_symbol, prob = parse_arc(line)
        fst.add_transition((start, end, input_symbol, output_symbol, prob))
        # print("transition: ", start, end, input_symbol, output_symbol, prob)
        line = f.readline().strip("\n")
    f.close()
    return fst


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("please specify input file")
    else:
        fst_filename = "wfst2"
        input_filename = 'ex2'
        # nfa_filename = args[0]
        # input_filename = args[1]
        fst = create_fst(fst_filename)
        input_file = open(input_filename)
        input_line = input_file.readline()
        while input_line:
            input_line = input_line.strip('\n')
            x = fst.viterbi(input_line)
            if x:
                print(x[0].strip(' '), x[1])
            else:
                print("none, 0")
            input_line = input_file.readline()

