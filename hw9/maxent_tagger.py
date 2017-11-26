# !/usr/bin/python

from optparse import OptionParser
import re
from operator import itemgetter


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
    :param i:
    :param wp_pairs:
    :return:
    """
    word_feat_dict = {}
    length = wp_pairs.__len__()
    if i == 0:  # first word of the sentence
        word_feat_dict["prevT=BOS"] = 1
        word_feat_dict["prevTwoTags=BOS-BOS"] = 1
        word_feat_dict["prevW=<s>"] = 1
        word_feat_dict["prev2W=<s>"] = 1
        add_count2dictionary("prevT=BOS", feature_count)
        add_count2dictionary("prevTwoTags=BOS-BOS", feature_count)
        add_count2dictionary("prevW=<s>", feature_count)
        add_count2dictionary("prev2W=<s>", feature_count)
    elif i == 1:  # second word of the sentence
        prev_w, prev_p = wp_pairs[0].split('/')
        word_feat_dict["prevT="+prev_p] = 1
        word_feat_dict["prevTwoTags=BOS-"+prev_p] = 1
        word_feat_dict["prevW="+prev_w] = 1
        word_feat_dict["prev2W=<s>"] = 1
        add_count2dictionary("prevT="+prev_p, feature_count)
        add_count2dictionary("prevTwoTags=BOS-"+prev_p, feature_count)
        add_count2dictionary("prevW="+prev_w, feature_count)
        add_count2dictionary("prev2W=<s>", feature_count)
    else:  # other words in the sentence
        prev_w, prev_p = wp_pairs[i-1].split('/')
        prev_2w, prev_2p = wp_pairs[i-2].split('/')
        word_feat_dict["prevT="+prev_p] = 1
        word_feat_dict["prevTwoTags="+prev_2p+"-"+prev_p] = 1
        word_feat_dict["prevW="+prev_w] = 1
        word_feat_dict["prev2W="+prev_2w] = 1
        add_count2dictionary("prevT="+prev_p, feature_count)
        add_count2dictionary("prevTwoTags="+prev_2p+"-"+prev_p, feature_count)
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


def read_train(train_filename):
    f = open(train_filename)
    line = f.readline().strip('\n')
    features = []  # (word, word's fetures) pair
    word_count = {}  # word count dictionary
    feature_count = {}
    while line:
        line = re.sub(" +", " ", line)  # Eliminate redundant spaces
        line = line.replace('\\/', '*\\*')  # use *\* to replace / in word, because we split word and pos using /
        wp_pairs = line.split(' ')  # a list of word/pos pairs
        for index in range(0, wp_pairs.__len__()):
            word, pos = wp_pairs[index].split('/')
            word = word.replace('*\\*', '\\/')
            word_feat_dict = set_features(index, wp_pairs, feature_count)
            features.append([word, word_feat_dict])
            word_count = add_count2dictionary(word, word_count)  # add word count to dictionary
        line = f.readline().strip('\n')
    f.close()
    return word_count, feature_count, features


def proc_rare_word(word_count, feature_count, features, rare_thres):
    new_features = []
    uppercase_pattern = re.compile(r"[A-Z]")
    number_pattern = re.compile(r"[0-9]")
    hyphen_pattern = re.compile(r"-")

    for word, word_feature_dict in features:
        if word_count[word] < rare_thres:
            # print("rare!")
            # TODO: add rare features
            if uppercase_pattern.match(word):
                word_feature_dict["containUC"] = 1
            else:
                word_feature_dict["containUC"] = 0
            add_count2dictionary("containUC", feature_count)
            if number_pattern.match(word):
                word_feature_dict["containNum"] = 1
            else:
                word_feature_dict["containNum"] = 0
            add_count2dictionary("containNum", feature_count)
            if hyphen_pattern.match(word):
                word_feature_dict["containHyp"] = 1
            else:
                word_feature_dict["containHyp"] = 0
            add_count2dictionary("containHyp", feature_count)
            word_len = len(word)
            for i in range(0, 4):
                if i < word_len:
                    word_feature_dict["pref="+word[:i+1]] = 1
                    add_count2dictionary("pref="+word[:i+1], feature_count)
                if word_len-i > 0:
                    word_feature_dict["suf="+word[word_len-i-1:]] = 1
                    add_count2dictionary("suf="+word[word_len-i-1:], feature_count)

        else:
            # print('non-rare!')
            # TODO: add non-rare feature
            word_feature_dict["curW="+word] = 1
            add_count2dictionary("curW="+word, feature_count)
        new_features.append([word, word_feature_dict])
    return new_features


def remove_rare_features(features, feature_count, feat_thres):
    new_features = []
    for word, word_feature_dict in features:
        for fea in word_feature_dict:
            new_word_feature_dict = {}
            if feature_count[fea] >= feat_thres or fea.split('=')[0] == 'curW':
                new_word_feature_dict[fea] = word_feature_dict[fea]
        new_features.append([word, new_word_feature_dict])
    return new_features

if __name__ == "__main__":
    parser = OptionParser(__doc__)
    options, args = parser.parse_args()
    use_local_file = 1
    if use_local_file:
        train_filename = "examples/wsj_sec0.word_pos"
        test_filename = "test.word_pos"
        rare_thres = 2
        feat_thres = 2
        output_dir = "output"
    else:
        train_filename = args[0]
        test_filename = args[1]
        rare_thres = int(args[2])
        feat_thres = int(args[3])
        output_dir = args[4]

    word_count, feature_count, features = read_train(train_filename)
    print(feature_count.__len__())
    features = proc_rare_word(word_count, feature_count, features, rare_thres)
    features = remove_rare_features(features, feature_count, feat_thres)
    
