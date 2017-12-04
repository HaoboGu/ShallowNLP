# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter
import os
import subprocess
import time
import math
from scipy import spatial


def normalize(vector):
    """
    Normalize the vector according to hw10.pdf
    :param vector:
    :return: normalized vector
    """
    z = 0
    normalized_vector = []
    for item in vector:
        z += item ** 2
    z = math.sqrt(z)
    for item in vector:
        normalized_vector.append(item / z)
    return normalized_vector


def read_vectors(filename, if_normalize):
    """
    Read vectors.txt into a dictionary. If if_normalize is non-zero, normalize the vectors.
    :param filename: filename of vectors.txt
    :param if_normalize: an integer indicates if we normalize the vector
    :return:
    """
    f = open(filename)
    vector_dict = {}
    line = f.readline().strip('\n')
    while line:
        seq = line.split(' ')
        word = seq[0]
        embedding = []
        for item in seq[1:]:
            embedding = embedding + [float(item)]
        vector_dict[word] = embedding
        line = f.readline().strip('\n')

    if if_normalize != 0:
        # normalize embedding vectors
        for key in vector_dict:
            vector_dict[key] = normalize(vector_dict[key])
    f.close()

    return vector_dict


def find_embedding(word, embedding_dict):
    """
    Find and return word embedding vector
    :param word:
    :param embedding_dict:
    :return:
    """
    if word in embedding_dict:
        return embedding_dict[word]
    else:
        return [0] * 50


def find_closest_word(predict_vector, embedding, sim_flag):
    """
    Find closest word of predicted vector. If sim_flag = 0, Euclidean distance is used. Otherwise, cosine similarity
    is used
    :param predict_vector:
    :param embedding:
    :param sim_flag: indicate which similarity function to use
    :return:
    """
    # s = time.time()
    closest_word = list(embedding.keys())[0]
    best_distance = math.sqrt(sum([(a-b)**2 for a, b in zip(predict_vector, embedding[closest_word])]))
    for item in embedding:
        if sim_flag == 0:
            # Use euclidean distance
            distance = math.sqrt(sum([(a-b)**2 for a, b in zip(predict_vector, embedding[item])]))
        else:
            # Use cosine similarity
            distance = spatial.distance.cosine(predict_vector, embedding[item])
        if distance < best_distance:
                closest_word = item
                best_distance = distance
    # e = time.time()
    # print(e - s, 's')
    return closest_word


def process_data(in_dir, out_dir, sim_flag, embedding):
    for filename in os.listdir(in_dir):
        in_file = open(in_dir + '/' + filename)
        out_file = open(out_dir + '/' + filename, 'w')
        input_line = in_file.readline().strip('\n')
        while input_line:
            a, b, c, d = input_line.split(' ')
            a_ebd = find_embedding(a, embedding)
            b_ebd = find_embedding(b, embedding)
            c_ebd = find_embedding(c, embedding)
            predict_d_ebd = [b-a+c for a, b, c in zip(a_ebd, b_ebd, c_ebd)]
            predict_word = find_closest_word(predict_d_ebd, embedding, sim_flag)
            output_string = a + ' ' + b + ' ' + c + ' ' #+ predict_word + '\n'
            out_file.write(output_string)
            input_line = in_file.readline().strip('\n')
        print(filename, " processed")
        in_file.close()
        out_file.close()


if __name__ == "__main__":
    start = time.time()
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 1
    if use_local_file:
        vector_filename = "examples/vectors.txt"
        input_dir = "examples/question-data"
        output_dir = "exp00"
        flag1 = 0
        flag2 = 0
    else:
        vector_filename = args[0]
        input_dir = args[1]
        output_dir = args[2]
        flag1 = int(args[3])
        flag2 = int(args[4])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    word_embedding = read_vectors(vector_filename, flag1)
    print(word_embedding.__len__())
    process_data(input_dir, output_dir, flag2, word_embedding)
    end = time.time()
    print(end - start)
    