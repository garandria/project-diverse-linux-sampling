import argparse


def dict_assoc(filename):
    '''
    '''
    res = dict()
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line[0] == 'c':
            # c 666 FEATURE_NAME
            line_list = line.split(' ')
            number = int(line_list[1])
            feature = line_list[2].rstrip('\n')
            res[number] = feature
            line = stream.readline()
    return res


def translate(filename, dico):
    '''
    '''
    res = ''
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line[0] == 'c' or line[0] == 'p':
            line = stream.readline()
        while line:
            line_list = line.split(' ')
            for nb in line_list:
                var = int(nb)
                try:
                    if var < 0:
                        res += '(~ {}) '.format(dico[-var])
                    elif var > 0:
                        res += '{} '.format(dico[var])
                    else:
                        res += '\n'
                except KeyError:
                    res += '? '
    with open('converted-{}'.format(filename), 'w') as output:
        output.write(res)


def main():
    '''
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-data',
                        help='path (including the file) to the dimacs file',
                        required=True)
    parser.add_argument('-dimacs',
                        help='path (including the file) to the dimacs file',
                        required=True)

    args = parser.parse_args()

    translate(args.dimacs, dict_assoc(args.data))


if __name__ == '__main__':
    main()
