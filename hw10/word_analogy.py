# !/usr/bin/python

from optparse import OptionParser
from operator import itemgetter
import os
import time
import math
from scipy import spatial
import numpy

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
    vector1 = numpy.array([predict_vector])
    vector2 = numpy.array(list(embedding.values()))
    keys = numpy.array(list(embedding.keys()))
    re = spatial.distance.cdist(vector1, vector2)
    return keys[numpy.argmin(re)]


def process_data(in_dir, out_dir, sim_flag, embedding):
    results = []

    for filename in os.listdir(in_dir):
        in_file = open(in_dir + '/' + filename)
        out_file = open(out_dir + '/' + filename, 'w')
        input_line = in_file.readline().strip('\n')
        predicted = []
        correspond_word = []
        while input_line:
            a, b, c, d = input_line.split(' ')
            a_ebd = find_embedding(a, embedding)
            b_ebd = find_embedding(b, embedding)
            c_ebd = find_embedding(c, embedding)
            predict_d = [b-a+c for a, b, c in zip(a_ebd, b_ebd, c_ebd)]
            predicted.append(predict_d)
            correspond_word.append([a, b, c, d])
            input_line = in_file.readline().strip('\n')
        vector2 = numpy.array(list(embedding.values()))
        keys = numpy.array(list(embedding.keys()))
        if sim_flag == 0:
            # Use euclidean distance
            dis_matrix = spatial.distance.cdist(predicted, vector2)  # compute distance matrix
        else:
            # Use cosine distance
            dis_matrix = spatial.distance.cdist(predicted, vector2, metric='cosine')  # compute distance matrix
        tp = 0
        for index in range(0, dis_matrix.shape[0]):
            predict_word = keys[numpy.argmin(dis_matrix[index])]
            aa = correspond_word[index][0]
            bb = correspond_word[index][1]
            cc = correspond_word[index][2]
            if predict_word == correspond_word[index][3]:
                tp += 1
            output_string = aa + ' ' + bb + ' ' + cc + ' ' + predict_word + '\n'
            out_file.write(output_string)
        results.append([filename, tp, dis_matrix.shape[0]])
        # print(tp, dis_matrix.shape[0], tp/dis_matrix.shape[0])
        in_file.close()
        out_file.close()

    total_tp = 0
    total_samples = 0
    for item in sorted(results, key=itemgetter(0)):
        print(item[0]+':')
        total_tp += item[1]
        total_samples += item[2]
        print("ACCURACY TOP1:", '{:.2%}'.format(item[1]/item[2]), '('+str(item[1])+'/'+str(item[2])+')')
    print("\nTotal accuracy:", '{:.2%}'.format(total_tp/total_samples), '('+str(total_tp)+'/'+str(total_samples)+')')


if __name__ == "__main__":
    start = time.time()
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        vector_filename = "examples/vectors.txt"
        input_dir = "examples/question-data"
        output_dir = "exp11"
        flag1 = 1
        flag2 = 1
    else:
        vector_filename = args[0]
        input_dir = args[1]
        output_dir = args[2]
        flag1 = int(args[3])
        flag2 = int(args[4])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    word_embedding = read_vectors(vector_filename, flag1)
    process_data(input_dir, output_dir, flag2, word_embedding)
    end = time.time()
    # print(end - start)
