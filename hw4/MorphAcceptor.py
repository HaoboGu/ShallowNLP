# !/usr/bin/python

from optparse import OptionParser
import subprocess


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    if len(args) == 1:
        print("Error: please specify input file")
    else:
        fsm_filename = args[0]
        word_list_filename = args[1]
        output_filename = args[2]
        # fsm_filename = "output_fsm"
        # word_list_filename = "examples/wordlist_ex"
        # output_filename = "q2_result_ex"
        command = ["carmel"]
        command.append("-sli")
        command.append(fsm_filename)

        word_file = open(word_list_filename)
        word = word_file.readline().strip('\n')
        output_file = open(output_filename, 'w')
        while word:
            word_str = ""
            for i in range(0, word.__len__()):
                word_str = word_str + word[i] + ' '
            o = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = o.communicate(bytes(word_str, encoding="utf-8"))
            if out:
                output_file.writelines(word + " => yes\n")
            else:
                output_file.writelines(word + " => no\n")
            word = word_file.readline().strip("\n")
