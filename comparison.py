'''This program compares a dimacs file (of linux configuration) and a
csv file containing all options.

For an example of dimacs file, see :
https://github.com/PettTo/Feature-Model-History-of-Linux/tree/master/2017/2017-09-11T13_10_57-07_00

For an example of a csv file with all options, see :
https://github.com/TuxML/Kanalyser/blob/master/alloptions-x64-v4.15.csv

'''

__author__ = "Georges Aaron RANDRIANAINA"
__email__ = "georges-aaron.randrianaina@ens-rennes.fr"

# To parse the command line argument
import argparse


def csv_reader(filename, column=1, sep=';', comment='#'):
    '''Reads a csv file of options and return a set containing all options

    :param filename: path (file included) to the csv file
    :type: str
    :param column: (optional) number of the column containing options
    (default is 1.)
    :type: int
    :param sep: (optional) separator used in the file (default is ';')
    :type: str
    :param comment: (optional) character for comment (default is '#')
    :type: str
    :return: set of all options
    :rtype: set
    '''
    res = set()
    col = column - 1
    with open(filename, 'r') as stream:
        stream.readline()       # first line (title)
        line = stream.readline()
        while line:
            if not (line[0] == comment):
                feature = line.split(sep)[col]
                res.add(feature)
            line = stream.readline()
    return res


def dimacs_reader(filename):
    '''Reads a dimacs file and returns a set containing all the options

    :param filename: path (file included) to the dimacs file
    :type: str
    :return: set of options
    :rtype: set
    '''
    res = set()
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line[0] == 'c':
            # c 666 FEATURE_NAME
            feature = line.split(' ')[2].rstrip('\n')
            res.add(feature)
            line = stream.readline()
    return res


def clean_set(mset):
    '''Cleans a set of feature

    For instance :
    "MY_OPTION=1" and "MY_OPTION=" are considered one option
    so it will add only one option MY_OPTION
    :param mset: a set of options
    :type: set
    :return: a set of real options
    :rtype: set
    '''
    res = set()
    for elt in mset:
        res.add(elt.split('=')[0].rstrim('_MODULE'))
    return res


def to_dot(dico):
    '''Write the dotviz code to build a tree for the dictionary
    :param dico: a dictionary like {'key': ['values'*]}
    :type: dict
    :return: a string containing the dotviz code
    :rtype: string
    '''
    res = 'graph {\n'
    for key in dico:
        res += 'TYPE -- {}\n'.format(key)
        for value in dico[key]:
            res += '{} -- {}\n'.format(key, value)
    res += '}'
    return res


def build_type_dict_from_csv(filename, option_col=1, type_col=2,
                             sep=',', comment='#'):
    '''Build a dictionary from a csv file like
    {'type': []}
    :param filename: name of the csv file
    :type: string
    :return: dictionary
    :rtype: dict
    '''
    ocol = option_col - 1
    tcol = type_col - 1
    dico = dict()
    with open(filename, 'r') as stream:
        stream.readline()       # first line (title)
        line = stream.readline()
        while line:
            if not (line[0] == comment):
                type = line.split(sep)[tcol].rstrip('\n')
                option = '"' + line.split(sep)[ocol] + '"'
                try:
                    dico[type].append(option)
                except KeyError:
                    dico[type] = [option]
            line = stream.readline()
    return dico


def build_option_type_dict(filename, option_col=1, type_col=2,
                           sep=',', comment='#'):
    '''Build a dictionary from a csv file like
    {'type': []}
    :param filename: name of the csv file
    :type: string
    :return: dictionary
    :rtype: dict
    '''
    ocol = option_col - 1
    tcol = type_col - 1
    dico = dict()
    with open(filename, 'r') as stream:
        stream.readline()       # first line (title)
        line = stream.readline()
        while line:
            if not (line[0] == comment):
                type = line.split(sep)[tcol].rstrip('\n')
                option = '"' + line.split(sep)[ocol] + '"'
                try:
                    dico[type].append(option)
                except KeyError:
                    dico[type] = [option]
            line = stream.readline()
    return dico


def diff(set1, set2):
    '''Gives the set of element in set1 but not in set2
    :param set1: a set
    :type: set
    :param set2: a set
    :type: set
    :return: a set
    :rtype: set
    '''
    res = set()
    for elt in set1:
        if elt not in set2:
            res.add(elt)
    return res


def main():
    '''The main function that parse the input arguments from the command
    line and use the previous defined function to read files. This
    functoin generates a file containing the number of features in
    each file (2 first line of the file) as comment then gives a list
    of options that the files do not have in common.

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean',
                        help='clean the name in the dimacs file',
                        action='store_true')
    parser.add_argument('-dimacs',
                        help='path (including the file) to the dimacs file',
                        required=True)
    parser.add_argument('-csv',
                        help='path (including the file) to the csv file',
                        required=True)
    args = parser.parse_args()

    # with open('tree.dot', 'w') as stream:
    #     stream.write(to_dot(build_type_dict_from_csv(args.csv)))

    csv = csv_reader(args.csv, sep=',')
    dimacs = dimacs_reader(args.dimacs, args.clean)
    diff_c_d = diff(csv, dimacs)
    diff_d_c = diff(dimacs, csv)
    
    content = ''
    content += '# CSV FILE : {} features\n'.format(len(csv))
    content += '# DIMACS FILE : {} features\n'.format(len(dimacs))
    content += '\n'
    content += '# DIMACS \\ CSV\n'
    content += '\n'
    for f in diff_d_c:
        content += '{}\n'.format(f)
    content += '\n'
    content += '# CSV \\ DIMACS\n'
    content += '\n'
    for f in diff_c_d:
        content += '{}\n'.format(f)

    outname = ''
    if args.clean:
        outname = 'output-clean.csv'
    else:
        outname = 'output.csv'
    with open(outname, 'w') as stream:
        stream.write(content)


if __name__ == '__main__':
    main()
