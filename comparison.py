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


def csv_reader(filename, column=1, sep=',', comment='#'):
    '''Reads a csv file of options and return a dictionary which the
    keys are options and values the type of the option

    :param filename: path (file included) to the csv file
    :type: str
    :param column: (optional) number of the column containing options
    (default is 1.)
    :type: int
    :param sep: (optional) separator used in the file (default is ',')
    :type: str
    :param comment: (optional) character for comment (default is '#')
    :type: str
    :return: a table like {option : type} association
    :rtype: dict
    '''
    res = dict()
    col = column - 1
    with open(filename, 'r') as stream:
        stream.readline()       # first line (title)
        line = stream.readline()
        while line:
            if not (line[0] == comment):
                feature = line.split(sep)[col]
                assert feature != '', 'CSV : feature empty'
                ftype = line.split(sep)[col + 1].rstrip('\n').strip()
                assert ftype != '', 'CSV : ftype empty'
                res[feature] = ftype.strip()
            line = stream.readline()
    return res


def dimacs_reader(filename):
    '''Reads a dimacs file and returns a set containing all the options

    :param filename: path (file included) to the dimacs file
    :type: str
    :return: set of options
    :rtype: set
    '''
    res = dict()
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line[0] == 'c':
            # c 666 FEATURE_NAME
            feature = line.split()[2].rstrip('\n').strip()
            number = line.split()[1].strip()
            res[feature] = int(number)
            # print(feature)
            # input()
            # assert feature != '', 'DIMACS : feature empty'
            # res.add(feature)
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
        if '=' in elt:
            res.add(elt.split('=')[0].rstrip('_MODULE').strip())
        else:
            res.add(elt.strip())
    return res


def to_dot(dico, type_dico, limit=10):
    '''Write the dotviz code to build a tree for the dictionary
    :param dico: a dictionary like {option: [reprentation+]}
    :type: dict
    :param type_dico: a dictionary like {option : type}
    :type: dict
    :param limit: number of children of the tree
    :type: int
    :return: a string containing the dotviz code
    :rtype: string
    '''
    res = 'graph {\n'
    dico_length = len(dico)
    tmp_limit = limit
    if dico_length < limit:
        tmp_limit = dico_length
    types = set()
    for key in list(dico)[:tmp_limit]:
        if key in type_dico:
            if not(type_dico[key] in types):
                res += 'ROOT -- "{}"\n'.format(type_dico[key])
                types.add(type_dico[key])
            res += '"{}" -- "{}"\n'.format(type_dico[key], key)
        else:
            if not('UNKNOWN' in types):
                res += 'ROOT -- UNKNOWN\n'
                types.add('UNKNOWN')
            res += 'UNKNOWN -- "{}"\n'.format(key)
        if len(dico[key]) > limit:
            for i in range(limit):
                res += '"{}" -- "{}"\n'.format(key, dico[key][i])
        else:
            for elt in dico[key]:
                res += '"{}" -- "{}"\n'.format(key, elt)
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
                    dico[type].append(option.strip())
                except KeyError:
                    dico[type] = [option.strip()]
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
    # l = list(set2)
    for elt in set1:
        if not (elt in set2):
            res.add(elt)
            # print('"{}" {}'.format(elt, l.index(elt)))
    return res


def opt_repr(cset, mset):
    '''Create a dictionary with the option and the representation
"
    :param cset: a set of only option (clean)
    :type: set
    :param mset: a set of options (with added chars)
    :type: set
    '''
    dico = dict()
    for elt in cset:
        for rep in mset:
            if str.startswith(rep, elt) and elt != rep:
                try:
                    dico[elt].append(rep)
                except KeyError:
                    dico[elt] = [rep]
    return dico


def main():
    '''The main function that parse the input arguments from the command
    line and use the previous defined function to read files. This
    functoin generates a file containing the number of features in
    each file (2 first line of the file) as comment then gives a list
    of options that the files do not have in common.

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-dimacs',
                        help='path (including the file) to the dimacs file',
                        required=True)
    parser.add_argument('-csv',
                        help='path (including the file) to the csv file',
                        required=True)
    args = parser.parse_args()

    # dimacs = dimacs_reader(args.dimacs)
    # with open('tree.dot', 'w') as stream:
    #     stream.write(to_dot(opt_repr(clean_set(dimacs), dimacs),
    #                         csv_reader(args.csv), limit=50))

    csv = csv_reader(args.csv, sep=',')
    dimacs = dimacs_reader(args.dimacs)
    
    # l = list(dimacs)
    # l.sort()
    # tmp = ''
    # for elt in l:
    #     tmp += '{}\n'.format(elt)
    # with open('dimacs_tmp', 'w') as stream:
    #     stream.write(tmp)
    
    dimacs_cleaned = clean_set(set(dimacs))
    print('CSV \\ DIMACS')
    diff_c_d = diff(csv, dimacs_cleaned)
    print('DIMACS \\ CSV')
    diff_d_c = diff(dimacs_cleaned, csv)
    print('=> {}'.format(csv == dimacs_cleaned))
    print('=> {} {}'.format(len(dimacs_cleaned), len(csv)))
    # modif = opt_repr(dimacs_cleaned, dimacs)
    tmp1 = ''
    lc = list(csv)
    lc.sort()
    for k in lc:
        tmp1 += '{}\n'.format(k)
    with open('csv_options', 'w') as stream:
        stream.write(tmp1)
    tmp2 = ''
    ld = list(dimacs_cleaned)
    ld.sort()
    # print('"{}"\n'.format(ld[0]))
    for k in ld:
        tmp2 += '{}\n'.format(k)
    with open('dimacs_options', 'w') as stream:
        stream.write(tmp2)
        
    content = ''
    content += '# CSV FILE : {} features\n'.format(len(csv))
    content += '# DIMACS FILE : {} features\n'.format(len(dimacs_cleaned))
    content += '\n'
    content += '# DIMACS \\ CSV {} features\n'.format(len(diff_d_c))
    content += '\n'
    for f in diff_d_c:
        content += '{}\n'.format(f)
    content += '\n'
    content += '# CSV \\ DIMACS {} features\n'.format(len(diff_c_d))
    content += '\n'
    for f in diff_c_d:
        content += '{}\n'.format(f)

    with open('output.csv', 'w') as stream:
        stream.write(content)


if __name__ == '__main__':
    main()
