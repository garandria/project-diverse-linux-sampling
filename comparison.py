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


def dimacs_reader(filename, clean=False):
    '''Reads a dimacs file and returns a set containing all the options

    :param filename: path (file included) to the dimacs file
    :type: str
    :param clean: (optional) clean the option : get rid of extra '=' or '=n' or
    ...  added the option (default is False)
    :type: bool
    :return: set of options
    :rtype: set
    '''
    res = set()
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line[0] == 'c':
            # c 666 FEATURE_NAME
            feature = line.split(' ')[2].split('\n')[0]
            if clean:
                feature = feature.split('=')[0]
            res.add(feature)
            line = stream.readline()
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

    diff = set()
    csv = csv_reader(args.csv, sep=',')
    dimacs = dimacs_reader(args.dimacs, args.clean)
    len_csv = len(csv)
    len_dimacs = len(dimacs)
    if len_dimacs > len_csv:
        diff = dimacs - csv
    else:
        diff = csv - dimacs

    content = ''
    content += '# CSV FILE : {} features\n'.format(len_csv)
    content += '# DIMACS FILE : {} features\n'.format(len_dimacs)
    content += '\n'
    for f in diff:
        content += '{}\n'.format(f)
    outname = ''
    if args.clean:
        outname = 'output-clean.csv'
    else:
        outname = 'output.csv'
    with open(outname, 'w') as stream:
        stream.write(content)


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


if __name__ == '__main__':
    main()
