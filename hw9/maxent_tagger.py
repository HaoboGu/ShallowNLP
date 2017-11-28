# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter
import os
import subprocess

def add_count2dictionary(key, dict):
    if key in dict:
        dict[key] = dict[key] + 1
    else:
        dict[key] = 1
    return dict


def set_features(i, wp_pairs, feature_count):
    """
    Set 6 common features for rare and non-rare words.
    The 6 features are: prevT, prevTwoTags, prevW, prev2W, nextW, next2W.
    :param i: word's index in the sentence
    :param wp_pairs: word/pos pair
    :return:
    """
    word_feat_dict = {}
    length = wp_pairs.__len__()
    if i == 0:  # first word of the sentence
        word_feat_dict["prevT=BOS"] = 1
        word_feat_dict["prevTwoTags=BOS+BOS"] = 1
        word_feat_dict["prevW=<s>"] = 1
        word_feat_dict["prev2W=<s>"] = 1
        add_count2dictionary("prevT=BOS", feature_count)
        add_count2dictionary("prevTwoTags=BOS+BOS", feature_count)
        add_count2dictionary("prevW=<s>", feature_count)
        add_count2dictionary("prev2W=<s>", feature_count)
    elif i == 1:  # second word of the sentence
        prev_w, prev_p = wp_pairs[0].split('/')
        word_feat_dict["prevT="+prev_p] = 1
        word_feat_dict["prevTwoTags=BOS+"+prev_p] = 1
        word_feat_dict["prevW="+prev_w] = 1
        word_feat_dict["prev2W=<s>"] = 1
        add_count2dictionary("prevT="+prev_p, feature_count)
        add_count2dictionary("prevTwoTags=BOS+"+prev_p, feature_count)
        add_count2dictionary("prevW="+prev_w, feature_count)
        add_count2dictionary("prev2W=<s>", feature_count)
    else:  # other words in the sentence
        prev_w, prev_p = wp_pairs[i-1].split('/')
        prev_2w, prev_2p = wp_pairs[i-2].split('/')
        word_feat_dict["prevT="+prev_p] = 1
        word_feat_dict["prevTwoTags="+prev_2p+"+"+prev_p] = 1
        word_feat_dict["prevW="+prev_w] = 1
        word_feat_dict["prev2W="+prev_2w] = 1
        add_count2dictionary("prevT="+prev_p, feature_count)
        add_count2dictionary("prevTwoTags="+prev_2p+"+"+prev_p, feature_count)
        add_count2dictionary("prevW="+prev_w, feature_count)
        add_count2dictionary("prev2W="+prev_2w, feature_count)
    if i == length-1:  # last word of the sentence
        word_feat_dict["nextW=</s>"] = 1
        word_feat_dict["next2W=</s>"] = 1
        add_count2dictionary("nextW=</s>", feature_count)
        add_count2dictionary("next2W=</s>", feature_count)
    elif i == length-2:  # the second last word of the sentence
        next_w = wp_pairs[length-1].split('/')[0]
        word_feat_dict["nextW="+next_w] = 1
        word_feat_dict["next2W=</s>"] = 1
        add_count2dictionary("nextW="+next_w, feature_count)
        add_count2dictionary("next2W=</s>", feature_count)
    else:  # other words of the sentence
        next_w = wp_pairs[i+1].split('/')[0]
        next_2w = wp_pairs[i+2].split('/')[0]
        word_feat_dict["nextW="+next_w] = 1
        word_feat_dict["next2W=" + next_2w] = 1
        add_count2dictionary("nextW="+next_w, feature_count)
        add_count2dictionary("next2W=" + next_2w, feature_count)
    return word_feat_dict



def read_data(train_filename):
    f = open(train_filename)
    line = f.readline().strip('\n')
    features = []  # (word, word's features, word_num, word's pos) tuples
    word_count = {}  # word count dictionary
    feature_count = {}
    sentence_num = 1
    while line:
        line = re.sub(" +", " ", line)  # Eliminate redundant spaces
        line = line.replace('\\/', '*\\*')  # use *\* to replace / in word, because we split word and pos using /
        line = line.replace(',', 'comma')
        wp_pairs = line.split(' ')  # a list of word/pos pairs
        for index in range(0, wp_pairs.__len__()):
            word, pos = wp_pairs[index].split('/')
            word = word.replace('*\\*', '\\/')
            word_feat_dict = set_features(index, wp_pairs, feature_count)
            word_num = str(sentence_num)+'-'+str(index)
            features.append([word, word_feat_dict, word_num, pos])
            word_count = add_count2dictionary(word, word_count)  # add word count to dictionary
        line = f.readline().strip('\n')
        sentence_num += 1
    f.close()
    return word_count, feature_count, features


def proc_rare_word(word_count, feature_count, features, rare_thres):
    new_features = []
    uppercase_pattern = re.compile(r"[A-Z]")
    number_pattern = re.compile(r"[0-9]")
    hyphen_pattern = re.compile(r"-")
    for word, word_feature_dict, word_num, pos in features:
        if word_count[word] < rare_thres:
            if uppercase_pattern.match(word):
                word_feature_dict["containUC"] = 1
                add_count2dictionary("containUC", feature_count)
            if number_pattern.match(word):
                word_feature_dict["containNum"] = 1
                add_count2dictionary("containNum", feature_count)
            if hyphen_pattern.match(word):
                word_feature_dict["containHyp"] = 1
                add_count2dictionary("containHyp", feature_count)
            word_len = len(word)
            for i in range(0, 4):
                # 4 characters are considered, prefix and suffix may overlap with each other
                if i < word_len:  # add prefix features
                    word_feature_dict["pref="+word[:i+1]] = 1
                    add_count2dictionary("pref="+word[:i+1], feature_count)
                if word_len-i > 0:  # add suffix features
                    word_feature_dict["suf="+word[word_len-i-1:]] = 1
                    add_count2dictionary("suf="+word[word_len-i-1:], feature_count)
        else:
            # non-rare word!
            word_feature_dict["curW="+word] = 1
            add_count2dictionary("curW="+word, feature_count)
        new_features.append([word, word_feature_dict, word_num, pos])
    return new_features


def remove_rare_features(features, feature_count, feat_thres):
    new_features = []
    new_feature_count = {}
    for word, word_feature_dict, word_num, pos in features:
        new_word_feature_dict = {}
        for fea in word_feature_dict:  # for every feature of word
            if feature_count[fea] >= feat_thres or fea.split('=')[0] == 'curW':
                # only add non-rare features and curW features to the final feature dictionary
                new_word_feature_dict[fea] = word_feature_dict[fea]
                add_count2dictionary(fea, new_feature_count)
        new_features.append([word, new_word_feature_dict, word_num, pos])
    return new_features, new_feature_count


def proc_test_features(test_features, kept_feature_count):
    kept_test_features = []
    for word, word_feature_dict, word_num, pos in test_features:
        kept_word_feature_dict = {}
        for fea in word_feature_dict:
            if fea in kept_feature_count:
                kept_word_feature_dict[fea] = word_feature_dict[fea]
        kept_test_features.append([word, kept_word_feature_dict, word_num, pos])
    return kept_test_features

def write_train_voc(word_count, output_dir, filename):
    output_filename = os.path.join(output_dir, filename)
    f = open(output_filename, 'w')
    for item in sorted(word_count.items(), key=itemgetter(1), reverse=True):
        f.write(item[0]+' '+str(item[1])+'\n')
    f.close()


def write_feats(feature_count, output_dir, filename):
    output_filename = os.path.join(output_dir, filename)
    f = open(output_filename, 'w')
    for item in sorted(feature_count.items(), key=itemgetter(1), reverse=True):
        f.write(item[0] + ' ' + str(item[1]) + '\n')
    f.close()


def write_vectors(word_features, output_dir, filename):
    # word_features = [word, word_feature_dictionary, word_num, word_pos]
    output_filename = os.path.join(output_dir, filename)
    f = open(output_filename, 'w')
    for word, word_feature_dict, word_num, pos in word_features:
        out_string = word_num + '-' + word + ' ' + pos
        for fea in word_feature_dict:
            out_string = out_string + ' ' + fea + ' ' + str(word_feature_dict[fea])
        f.write(out_string+'\n')
    f.close()


if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 0
    if use_local_file:
        train_filename = "examples/wsj_sec0.word_pos"
        test_filename = "test.word_pos"
        rare_thres = 5
        feat_thres = 10
        output_dir = "output"
    else:
        train_filename = args[0]
        test_filename = args[1]
        rare_thres = int(args[2])
        feat_thres = int(args[3])
        output_dir = args[4]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # read and process training data
    word_count, feature_count, features = read_data(train_filename)
    write_train_voc(word_count, output_dir, "train_voc")
    all_features = proc_rare_word(word_count, feature_count, features, rare_thres)
    write_feats(feature_count, output_dir, "init_feats")
    kept_features, kept_feature_count = remove_rare_features(all_features, feature_count, feat_thres)
    write_feats(kept_feature_count, output_dir, "kept_feats")
    write_vectors(kept_features, output_dir, "final_train.vectors.txt")

    # read and process testing data
    test_word_count, test_feature_count, test_features = read_data(test_filename)
    all_test_features = proc_rare_word(test_word_count, test_feature_count, test_features, rare_thres)
    kept_test_features = proc_test_features(all_test_features, kept_feature_count)
    write_vectors(kept_test_features, output_dir, "final_test.vectors.txt")

    train_txt_path = os.path.join(output_dir, "final_train.vectors.txt")
    train_vector_path = os.path.join(output_dir, "final_train.vectors")
    import_command = ['mallet', 'import-file', '--input', train_txt_path, '--output', train_vector_path]
    train_classifier_command = ['mallet', 'train-classifier', '--input', train_vector_path,
                                '--output-classifier', 'me-model', '--trainer', 'MaxEnt']
    test_txt_path = os.path.join(output_dir, "final_test.vectors.txt")
    test_command = ['mallet', 'classify-file', '--input', test_txt_path, '--output', 'test_result',
                    '--classifier', 'me-model']

    o = subprocess.call(import_command)
    o = subprocess.call(train_classifier_command)
    o = subprocess.call(test_command)
    # TODO: 1. write final_test.vectors.txt and run mallet commands
    # 2. comma in different files
    # 3. confirm containXX number
    # 4. confirm the order of features
    # 5. confirm the representation of BOS
    
