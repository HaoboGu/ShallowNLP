# !/usr/bin/python

"""

This script is a tokenizer used to split texts to words by punctuations/whitespaces. Some phrases won't be splitted.

"""

import sys
import re

def add_whitespace(match):
    return ' ' + match.group(0) + ' '

def tokenize(string, abbrev_list):
    p_abbrev = re.compile(r"(\w\.)+$")
    p_numbers = re.compile(r"(-?\d+)(\.\d+)?%?$")
    p_large_numbers = re.compile(r"-?[0-9]{1,3},(\d{3},)*\d{3}(\.\d+)?%?$")
    p_puncs_end = re.compile(r"[\W]$")
    p_puncs = re.compile(r"\W{1}")
    p_puncs_start = re.compile(r"^\W")
    p_email = re.compile(r"^[\w.+-]+@[a-zA-Z0-9-]+\.[A-Za-z0-9-.]+$")  # \w includes '_', so \w shouldn't be used at end
    p_url = re.compile(r"^((https?|ftp|file)://)?[-\w+&@#/%?=~|!:,.;]+\.[-\w+&@#/%?=~|!:,.;]+[-\w+&@#/%=~|]$")
    p_unixpath = re.compile(r"^([~\.\/][\w\/ !$`&*()+]+)*$")
    p_winpath = re.compile(r"^[A-Za-z]:\/([/-<>|~:*?\.\w]+)+(\/|(\.[\w]+))*")
    p_contraction = re.compile(r"(n\'t)|(\'ve)|(\'d)|(\'ll)|(\'s)|(\'m)|(\'re)|(\'all)")  # TODO: add [a-zA-Z]+ or not?
    p_apostrophe_atend = re.compile(r"\w+\'$")
    p_dash = re.compile(r"-{2}")
    # p_puncs = re.compile(r"\W+")

    prev_result = ' '
    result = string
    print(abbrev_list)
    while prev_result != result:
        prev_result = result
        result = ''
        words = prev_result.split(' ')
        for item in words:
            if not item:
                continue
            item = item.strip(' ')
            # 1. abbreviations, in (\w\.)+ form or in the list

            if p_abbrev.match(item):
                item = p_abbrev.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                print("match: abbrev1: ", item)
            elif item in abbrev_list:
                result = result + ' ' + item + ' '
                print("match: abbrev!", item)
            # 2. normal numbers, without comma
            elif p_numbers.match(item):
                print("match: number!", item)
                item = p_numbers.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 3. large numbers with comma
            elif p_large_numbers.match(item):
                print("match: large_number!", item)
                item = p_large_numbers.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 9. hyphen in dash
            elif p_dash.search(item):
                item = p_dash.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 4. emails
            elif p_email.match(item):
                print("match: email!", item)
                item = p_email.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 6. unix/linux paths
            elif p_unixpath.match(item):
                print("match: path!", item)
                item = p_unixpath.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            elif p_winpath.match(item):
                print("match: path!", item)
                item = p_winpath.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 7. apostrophe at end(noun's possessive）
            elif p_apostrophe_atend.search(item):
                print("match: apostrophe at end!", item)
                result = result + ' ' + item + ' '
            # 8. contractions
            elif p_contraction.search(item):
                item = p_contraction.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                print("match:contraction: ", item)
            elif p_puncs_start.match(item):
                item = p_puncs_start.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                print('punctuation at start', item)
            # normal words with a punctuation at end (should be split)
            elif p_puncs_end.search(item):
                item = p_puncs_end.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                print('punctuation at end', item)
            # 5. urls
            elif p_url.match(item):
                print("match: url!", item)
                item = p_url.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            elif p_puncs.search(item):
                item = p_puncs.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                print('punctuation in line', item)
            else:
                result = result + ' ' + item + ' ' 
                continue
        result = re.sub(" +", " ", result)  # delete extra whitespaces
        print(result)
    print("final result:")
    print(result)
    return result

def create_abbrev_list(abbrev_file):
    f = open(abbrev_file)
    line = f.readline()
    abbrev_list = []
    while line:
        line = line.rstrip('\n')
        abbrev_list.append(line)
        line = f.readline()
    f.close()
    return abbrev_list

def process(abbrev_file):
        """Process the input_file, generate output_file
        """
        use_file = 1
        if use_file == 1:
            input_file = open('input_file', 'r')
            output_file = open('output_file', 'w')
            line = input_file.readline()
        else:
            line = sys.stdin.readline()
        abbrev_list = create_abbrev_list(abbrev_file)
        while line:
            # line = tokenize(line)
            line = line.rstrip('\n')
            output_line = tokenize(line, abbrev_list)
            if use_file == 1:
                line = input_file.readline()
                output_file.writelines(output_line+'\n')
            else:
                line = sys.stdin.readline()
        if use_file == 1:
            input_file.close()
            output_file.close()
if __name__ == "__main__":
        from optparse import OptionParser
        
        parser = OptionParser(__doc__)
        options, args = parser.parse_args()
        args = ['abbrev-list']
        if len(args) == 0:
            print("No abbrev-list file!")
        else:
            # process(args[0])
            abbrev_list = create_abbrev_list(args[0])
            process(args[0])
            # tokenize("Lorillard Inc., asd--asd  crocidolite in 1956. ", abbrev_list)

        # n_lines_from_stdin(n)


