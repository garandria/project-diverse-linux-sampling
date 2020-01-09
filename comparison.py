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
import file

UNDEFINED = 'UNDEFINED'


def prepare(feat_repr, feat_type):
    res = dict()
    for feat in feat_repr:
        if feat in feat_type:
            if feat_type[feat] in res:
                res[feat_type[feat]][feat] = feat_repr[feat]
            else:
                res[feat_type[feat]] = {feat: feat_repr[feat]}
        else:
            if UNDEFINED in res:
                res[UNDEFINED][feat] = feat_repr[feat]
            else:
                res[UNDEFINED] = {feat: feat_repr[feat]}
    return res


def to_dot(dico):
    for t in dico:
        res = 'graph {\n'
        for f in dico[t]:
            res += '"{}" -- "{}"\n'.format(t, f)
            for r in dico[t][f]:
                res += '"{}" -- "{}"\n'.format(f, r)
        res += '}'
        with open('dot/{}'.format(t), 'w') as stream:
            stream.write(res)


# def to_dot(dico, type_dico, limit=10):
#     '''Write the dotviz code to build a tree for the dictionary
#     :param dico: a dictionary like {option: [reprentation+]}
#     :type: dict
#     :param type_dico: a dictionary like {option : type}
#     :type: dict
#     :param limit: number of children of the tree
#     :type: int
#     :return: a string containing the dotviz code
#     :rtype: string
#     '''
#     res = 'graph {\n'
#     dico_length = len(dico)
#     tmp_limit = limit
#     if dico_length < limit:
#         tmp_limit = dico_length
#     types = set()
#     for key in list(dico)[:tmp_limit]:
#         if key in type_dico:
#             if not(type_dico[key] in types):
#                 res += 'ROOT -- "{}"\n'.format(type_dico[key])
#                 types.add(type_dico[key])
#             res += '"{}" -- "{}"\n'.format(type_dico[key], key)
#         else:
#             if not('UNKNOWN' in types):
#                 res += 'ROOT -- UNKNOWN\n'
#                 types.add('UNKNOWN')
#             res += 'UNKNOWN -- "{}"\n'.format(key)
#         if len(dico[key]) > limit:
#             for i in range(limit):
#                 res += '"{}" -- "{}"\n'.format(key, dico[key][i])
#         else:
#             for elt in dico[key]:
#                 res += '"{}" -- "{}"\n'.format(key, elt)
#     res += '}'
#     return res


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

    csv = file.CSVFile(args.csv)
    dimacs = file.DimacsFile(args.dimacs)
    result = """CSV : {}
Nb features    : {:10}
Nb types       : {:10}

================================================================================

DIMACS : {}
Nb features            : {:10}
Nb clauses             : {:10}
Nb undefined variables : {:10} ({}%)
Total variables        : {:10}

================================================================================

Nb features diff : {}

================================================================================

""".format(csv.getFileName(), csv.getNbFeatures(), csv.getNbTypes(),
           dimacs.getFileName(), dimacs.getRealNbFeatures(),
           dimacs.getNbClauses(),
           dimacs.getNbVariables() - dimacs.getRealNbFeatures(),
           (dimacs.getNbVariables() - dimacs.getRealNbFeatures())
           * 100 // dimacs.getNbVariables(), dimacs.getNbVariables(),
           abs(csv.getNbFeatures() - dimacs.getRealNbFeatures()))

    dimacs_minus_csv = dimacs.diff(csv.getFeaturesSet())
    csv_minus_dimacs = csv.diff(dimacs.getRealFeaturesSet())
    difference = "DIMACS \\ CSV : {}\n".format(len(dimacs_minus_csv))
    for elt in dimacs_minus_csv:
        difference += "{}\n".format(elt)
    difference += """
================================================================================
"""
    difference += "\n"
    difference += "CSV \\ DIMACS : {}\n".format(len(csv_minus_dimacs))
    for elt in csv_minus_dimacs:
        difference += "{}, {}\n".format(elt, csv.getType(elt))
    difference += """
================================================================================
"""
    filename = 'output' + csv.getFileName()\
                             .split('/')[-1]\
                             .split('-')[-1]\
                             .strip('.csv')
    with open(filename, 'w') as stream:
        stream.write(result + difference)
    print("=> File written : {}".format(filename))

    # dimacs_features = ''
    # for i in dimacs.getRealFeaturesSet():
    #     dimacs_features += '{}\n'.format(i)
    # with open('dimacs_features', 'w') as stream:
    #     stream.write(dimacs_features)
    # to_dot(prepare(dimacs.getNameVariationDict(), csv.getFeatures()))
    # to_dot({'MTD': dimacs.getNameVariationDict()['MTD']})


if __name__ == '__main__':
    main()
