# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        train_filename = "examples/wsj_sec0.word_pos"
        test_filename = "test.word_pos"
        rare_thres = 1
        feat_thres = 1
        output_dir = "output"
    else:
        train_filename = args[0]
        test_filename = args[1]
        rare_thres = int(args[2])
        feat_thres = int(args[3])
        output_dir = args[4]




