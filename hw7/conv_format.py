# !/usr/bin/python

from optparse import OptionParser
import time
import sys



def read_result(use_local_file, out_filename):
    if use_local_file == 1:
        f = open("examples/sys5")
        line = f.readline().strip('\n')
    else:
        line = sys.stdin.readline().strip('\n')
    of = open(output_filename, 'w')
    while line:
        sent, state_seq = line.split(" => ")
        words = sent.split(' ')
        states = state_seq.split(' ')
        print(words.__len__(), states.__len__())
        print(states)
        outstr = ''
        for i in range(0, words.__len__()):
            word_pos = words[i] + '/' + states[i+1].split('_')[1]
            outstr = outstr + word_pos + ' '
        of.write(outstr.strip(' ') + '\n')
        if use_local_file == 1:
            line = f.readline().strip('\n')
        else:
            line = sys.stdin.readline().strip('\n')
    if use_local_file == 1:
        f.close()
    of.close()

if __name__ == "__main__":
    start = time.time()
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 1
    if use_local_file:
        output_filename = "examples/sys5_res"
    else:
        output_filename = args[2]
    read_result(use_local_file, output_filename)

    end = time.time()
    print(end-start)


