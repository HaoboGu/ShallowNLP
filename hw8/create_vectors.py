# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter
import os


def proc_file(input_filename):
    word_dictionary = {}
    f = open(input_filename)
    line = f.readline().strip('\n')
    while line:  # This loop is used to skip header
        line = f.readline().strip('\n')
    line = f.readline().lower()
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


def write_result(input_filename, target_label, output_filename, word_dictionary):
    out_f = open(output_filename, 'a')
    out_f.write(input_filename + ' ' + target_label)

    for item in sorted(word_dictionary.items(), key=itemgetter(0)):
        out_f.write(' ' + item[0] + ' ' + str(item[1]))
    out_f.write("\n")
    out_f.close()


def create_vector(dirs, ratio, train_vector_file, test_vector_file):
    os.remove(train_vector_file)
    os.remove(test_vector_file)
    for sub_dir in dirs:
        label = os.path.basename(sub_dir)
        file_list = sorted(os.listdir(sub_dir))  # get all files in this sub-directory
        num_in_dir = file_list.__len__()
        train_file_list = file_list[:int(num_in_dir * ratio)]  # get training file list
        test_file_list = file_list[int(num_in_dir * ratio):]  # get testing files list
        for training_file in train_file_list:  # convert training file to one line in train.vector.txt
            training_file_path = os.path.join(sub_dir, training_file)  # get path
            train_dictionary = proc_file(training_file_path)
            write_result(training_file_path, label, train_vector_file, train_dictionary)
        for testing_file in test_file_list:  # convert testing file to one line in test.vector.txt
            testing_file_path = os.path.join(sub_dir, testing_file)  # get path
            test_dictionary = proc_file(testing_file_path)
            write_result(testing_file_path, label, test_vector_file, test_dictionary)


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        train_vector_filename = "train.vectors.txt"
        test_vector_filename = "test.vectors.txt"
        ratio = 0.9
        dir1 = "examples/20_newsgroups/talk.politics.guns"
        dir2 = "examples/20_newsgroups/talk.politics.mideast"
        dir3 = "examples/20_newsgroups/talk.politics.misc"
        dirs = [dir1, dir2, dir3]
    else:
        num_args = len(args)
        train_vector_filename = args[0]
        test_vector_filename = args[1]
        ratio = args[2]
        dirs = []
        for i in range(3, num_args):
            dirs.append(args[i])
    create_vector(dirs, ratio, train_vector_filename, test_vector_filename)



