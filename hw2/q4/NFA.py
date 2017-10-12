# !/usr/bin/python

import queue
from optparse import OptionParser


def parse_arc(line):
    words = line.split(' ')
    start = words[0].strip("(")
    end = words[1].strip("(")
    arc = words[2].strip("\n")
    arc = arc.strip(")")
    arc = arc.strip("\"")
    return start, end, arc


class NFA:
    states = []
    arcs = []
    symbols = []
    def __init__(self, start, final):
        self.start_state = start
        self.final_state = final

    def add_arc(self, arc):
        if arc not in self.arcs:
            self.arcs.append(arc)
        if arc[0] not in self.states:
            self.states.append(arc[0])
        if arc[1] not in self.states:
            self.states.append(arc[1])
        if arc[2] not in self.symbols:
            self.symbols.append(arc[2])

    def move(self, start, symbol):
        # Move from start using symbol
        dest = []
        for e in self.arcs:
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


class DFA:
    states = []
    arcs = []  # (start, end, symbol)
    symbols = []

    def __init__(self, start_state):
        self.start_state = start_state

    def add_arc(self, arc):
        if arc not in self.arcs:
            self.arcs.append(arc)
        if arc[0] not in self.states:
            self.states.append(arc[0])
        if arc[1] not in self.states:
            self.states.append(arc[1])
        if arc[2] not in self.symbols:
            self.symbols.append(arc[2])

    def move(self, start, symbol):
        # Move from start using symbol, if it isn't a valid move, return -1
        for e in self.arcs:
            if e[0] == start and e[2] == symbol:
                return e[1]
        return -1

    def set_final_state(self, final_state_nfa):
        self.final_state = []
        for item in self.states:
            if final_state_nfa in item:
                self.final_state.append(item)

    def receive(self, input_line):
        input_line = input_line.strip('\n')
        symbols = input_line.split(' ')
        symbols = [item.strip('"') for item in symbols]
        current = self.start_state
        for item in symbols:
            if item != "*e*":
                next_state = self.move(current, item)
                if next_state == -1:
                    return False
                else:
                    current = next_state
        return (current in self.final_state)


def read_nfa(nfa_filename):
    nfa_file = open(nfa_filename)
    line = nfa_file.readline()
    final_state = line.strip("\n")  # First line is final state
    line = nfa_file.readline()
    start, end, arc = parse_arc(line)
    start_state = start  # First start state is start state of NFA
    nfa = NFA(start_state, final_state)
    nfa.add_arc((start, end, arc))
    line = nfa_file.readline()
    while line:
        if line != '\n':
            start, end, arc = parse_arc(line)
            nfa.add_arc((start, end, arc))
        line = nfa_file.readline()
    nfa_file.close()
    return nfa


def convert_nfa2dfa(nfa_filename):
    nfa = read_nfa(nfa_filename)
    dfa_start_state = nfa.find_ep_closure(nfa.start_state)
    dfa = DFA(dfa_start_state)
    dfa_states = [dfa_start_state]
    unmarked = queue.Queue()
    unmarked.put(dfa_start_state)
    while not unmarked.empty():
        current = unmarked.get()  # current dfa state (a set of nfa states)
        for i in nfa.symbols:
            if i != "*e*":
                next_states = []
                for c_states in current:
                    c_next = nfa.move(c_states, i)
                    for item in nfa.find_ep_closure(c_next):
                        if item not in next_states:
                            next_states.append(item)

                if next_states not in dfa_states and next_states:
                    dfa_states.append(next_states)
                    unmarked.put(next_states)
                if next_states:
                    dfa.add_arc((current, next_states, i))
                    # print(current, i, next_states)
    dfa.set_final_state(nfa.final_state)
    return dfa


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("please specify input file")
    else:
        # nfa_filename = "fsa1"
        # input_filename = 'ex'
        nfa_filename = args[0]
        input_filename = args[1]
        input_file = open(input_filename)
        input_line = input_file.readline()
        while input_line:
            input_line = input_line.strip('\n')
            dfa = convert_nfa2dfa(nfa_filename)
            # print(dfa.final_state)
            if dfa.receive(input_line):
                print(input_line, "==> yes")
            else:
                print(input_line, "==> no")
            input_line = input_file.readline()

