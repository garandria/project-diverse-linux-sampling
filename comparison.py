'''
'''

import argparse


def csv_reader(filename, column=1, sep=';', comment='#'):
    '''
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
    '''
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
    '''
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
    with open('output.csv', 'a') as stream:
        stream.write('# CSV FILE : {} features\n'.format(len_csv))
        stream.write('# DIMACS FILE : {} features\n'.format(len_dimacs))
        for f in diff:
            stream.write('{}\n'.format(f))


if __name__ == '__main__':
    main()
