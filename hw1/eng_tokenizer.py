# !/usr/bin/python

"""

This script is a tokenizer used to split texts to words by punctuations/whitespaces. Some phrases won't be split.

"""

import sys
import re

def add_whitespace(match):
    return ' ' + match.group(0) + ' '

def tokenize(string, abbrev_list):
    p_abbrev = re.compile(r"(\b([a-zA-Z]\.)+$)")
    p_split_end = re.compile(r"[})\]>,@+!#$\":;?&*]$")
    p_split_start = re.compile(R"^[!\"$%()\[\]*+,<>=?^_{}]")
    p_abbrev_filter = re.compile(r"(^([a-zA-Z]\.)+)(?=\W)")
    # p_abbrev_filter2 = re.compile(r"(\W([a-zA-Z]\.)+)$")
    p_numbers = re.compile(r"(-?\d+)(\.\d+)?%?$")
    p_large_numbers = re.compile(r"-?[0-9]{1,3},(\d{3},)*\d{3}(\.\d+)?%?")
    p_fraction = re.compile(r"(-?[0-9]+[\/][0-9]+%?)")
    p_puncs_end = re.compile(r"[\W]$")
    p_puncs = re.compile(r"\W")
    p_puncs_start = re.compile(r"^\W")
    p_email = re.compile(r"^[\w.+-]+@[a-zA-Z0-9-]+\.[A-Za-z0-9-.]+$")
    p_url = re.compile(r"^((((https?|ftp|file)://)[-\w+&@#/%?=~|!:,.;]+\.)|(www\.))[-\w+&@#/%?=~|!:,.;]+[-\w+&@#/%=~|]$")
    p_unixpath = re.compile(r"^([~\.\/\\][\w\/ !$`&*()+]+)*$")
    p_winpath = re.compile(r"^[A-Za-z]:[/\\]([-/<>|~:*?.\w\\]+)+([/\\]|(\.[\w]+))*")
    p_contraction = re.compile(r"((n\'t)|(\'ve)|(\'d)|(\'ll)|(\'s)|(\'m)|(\'re)|(\'all))")
    p_apostrophe_atend = re.compile(r"\w+s\'$")
    p_dash = re.compile(r"-{2}")
    p_ellipsis = re.compile(r"\.{3}")
    p_word = re.compile(r"[a-zA-Z0-9]+")
    p_ip = re.compile(r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
    prev_result = ' '
    result = string

    while prev_result != result:
        prev_result = result
        result = ''
        words = prev_result.split(' ')
        for item in words:
            if not item:
                continue
            item = item.strip(' ')
            # 1. abbreviations, in (\w\.)+ form or in the list
            if p_split_end.search(item):
                item = p_split_end.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            elif p_split_start.search(item):
                item = p_split_start.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            elif p_ip.search(item):
                item = p_ip.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 11. contractions
            elif p_contraction.search(item):
                item = p_contraction.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print("match:contraction: ", item)
            elif p_abbrev.search(item):
                if p_puncs_start.match(item):
                    item = p_puncs_start.sub(add_whitespace, item)
                else:
                    item = p_abbrev.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print("match: abbrev1: ", item)
            elif p_abbrev_filter.search(item):
                item = p_abbrev_filter.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print("match: abbrev1: ", item)
            # 14. urls
            elif p_url.match(item):
                # print("match: url!", item)
                item = p_url.sub(add_whitespace, item)
                result = result + ' ' + item + ' '

            # elif p_abbrev_filter2.search(item):
            #     item = p_abbrev_filter2.sub(add_whitespace, item)
            #     result = result + ' ' + item + ' '
            #     print(item)
            elif item in abbrev_list or item == "o'clock":
                result = result + ' ' + item + ' '
                # 8. unix/linux paths
            elif p_unixpath.search(item):
                # print("match: path!", item)
                item = p_unixpath.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 9. windows paths
            elif p_winpath.search(item):
                # print("match: winpath!", item)
                item = p_winpath.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # 2. fractions
            elif p_fraction.search(item):
                item = p_fraction.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print("match: fraction!", item)

            # 3. large numbers with comma
            elif p_large_numbers.search(item):
                item = p_large_numbers.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print("match: large_number!", item)
            # 4. normal numbers, without comma
            elif p_numbers.search(item):
                item = p_numbers.sub(add_whitespace, item)
                # print("match: number!", item)
                result = result + ' ' + item + ' '
            # 5. hyphen in dash
            elif p_dash.search(item):
                item = p_dash.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 6. periods in ellipsis
            elif p_ellipsis.search(item):
                item = p_ellipsis.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print("match: ellipsis: ", item)
            # 7. emails
            elif p_email.search(item):
                # print("match: email!", item)
                item = p_email.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
            # 10. apostrophe at end(noun's possessive）
            elif p_apostrophe_atend.search(item):
                # print("match: apostrophe at end!", item)
                result = result + ' ' + item + ' '
            # 12. normal words with a punctuation at end (should be split)
            elif p_puncs_end.search(item):
                item = p_puncs_end.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print('punctuation at end', item)
            # 13. normal words with a punctuation at its start (should be split)
            elif p_puncs_start.match(item):
                item = p_puncs_start.sub(add_whitespace, item)
                result = result + ' ' + item + ' '
                # print('punctuation at start', item)
            # 15. punctuations between words
            elif p_puncs.search(item):
                item = p_puncs.subn(add_whitespace, item, count=1)
                result = result + ' ' + item[0] + ' '
                # print('punctuation in line', item[0])
            # 16. match words
            elif p_word.match(item):
                result = result + ' ' + item + ' '
            # 17. used for testing other undefined cases
            else:
                result = result + ' ' + item + ' '
                continue

        result = re.sub(" +", " ", result)  # delete extra whitespaces
        result = result.rstrip(' ')
        # print(result)
    # print("final result:")
    # print(result)
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
        use_file = 0
        if use_file == 1:
            input_file = open('ex2', 'r')
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
                print(output_line)
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
            abbrev_list = create_abbrev_list(args[0])
            process(args[0])
            # tokenize(" asdn't.. sino-U.S. N.Y.-based s.b. a(a.v.b.))asd", abbrev_list)
