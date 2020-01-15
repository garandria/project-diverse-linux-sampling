from file import DimacsFile, CSVFile
from pysat.formula import CNF
from pysat.solvers import Solver
import argparse

DIMACS = "../kconfigreader/out.dimacs"
CONFIGFILE = "../linux-4.14.152/.config"
CSV = "../linux-4.14.152/alloptions-x86.4.14.152.csv"


def checking(config_file, dimacs, csv, s,
             allow_boolean, allow_tristate):
    # allow_integer, allow_string, allow_hexadecimal
    conf_features = read_file(config_file)
    print("=> ADDING FEATURES FROM CONFIG")
    print("   ---------------------------")
    for feature in conf_features:
        if feature in dimacs.getFeaturesSet():
            if feature in csv.getFeaturesSet():
                if allow_tristate and csv.getType(feature) == "TRISTATE":
                    feat_mod = "{}_MODULE".format(feature)
                    var_for_name = dimacs.getVariableOf(feature)
                    var_for_module = dimacs.getVariableOf(feat_mod)
                    to_add = []
                    if conf_features[feature] == 'y':
                        to_add = [var_for_name, -var_for_module]
                    elif conf_features[feature] == 'm':
                        to_add = [var_for_module, -var_for_name]
                    else:
                        to_add = [-var_for_module, -var_for_name]
                    print("Adding clause: {}/MODULE ({}/{})"
                          .format(feature, var_for_name, var_for_module))
                    for c in to_add:
                        if not s.add_clause([c], no_return=False):
                            print("UNSAT")
                            return False
                if allow_boolean and csv.getType(feature) == "BOOL":
                    var_name = dimacs.getVariableOf(feature)
                    print("+ Adding clause: {} ({})".format(feature, var_name))
                    if not s.add_clause([var_name], no_return=False):
                        print("UNSAT")
                        return False
            else:
                print("- {} not in CSV".format(feature))
        else:
            print("- {} not in DIMACS".format(feature))
    print()
    print("=> ADDING FEATUERS THAT ARE NOT IN THE CONFIG (hence they are neg)")
    print("   ---------------------------------------------------------------")
    for feature in csv.getFeaturesSet():
        if feature not in set(conf_features) and feature in dimacs.getFeaturesSet():
            if allow_tristate and csv.getType(feature) == "TRISTATE":
                feat_mod = "{}_MODULE".format(feature)
                var_for_name = dimacs.getVariableOf(feature)
                var_for_module = dimacs.getVariableOf(feat_mod)
                print("+ Adding clause: {}/MODULE ({}/{})"
                      .format(feature, var_for_name, var_for_module))
                for c in [-var_for_name, -var_for_module]:
                    if not s.add_clause([c], no_return=False):
                        print("UNSAT")
                        return False
            if allow_boolean and csv.getType(feature) == "BOOL":
                var_name = dimacs.getVariableOf(feature)
                print("+ Adding clause: {} ({})".format(feature, var_name))
                if not s.add_clause([-var_name], no_return=False):
                    print("UNSAT")
                    return False
    return True

def read_file(file):
    res = dict()
    with open(file, 'r') as stream:
        for line in stream:
            if line[0] != '#' and line != '\n':
                feature = line[7:]
                flist = feature.split('=')
                res[flist[0]] = flist[1]
    return res


def main():
    ''' main function '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--boolean", action="store_true",
                        help="allows the program to check the booleans")
    parser.add_argument("--tristate", action="store_true",
                        help="allows the program to check the tristates")
    parser.add_argument("--string", action="store_true",
                        help="allows the program to check the strings")
    parser.add_argument("--integer", action="store_true",
                        help="allows the program to check the integers")
    parser.add_argument("--hexadecimal", action="store_true",
                        help="allows the program to check the hexadecimal")
    parser.add_argument("dimacs_file", type=str, default=DIMACS,
                        help="dimacs file")
    parser.add_argument("csv_file", type=str, default=CSV, help="csv file")
    parser.add_argument("config_files", type=str, nargs="+",
                        help=".config files")
    args = parser.parse_args()

    dimacs = DimacsFile(args.dimacs_file)
    csv = CSVFile(args.csv_file)
    cnf = CNF(from_file=args.dimacs_file)
    s = Solver(bootstrap_with=cnf.clauses)
    assert s.solve() is True, "initial formula is UNSAT"
    for file in args.config_files:
        tmp_s = s
        checking(file, dimacs, csv, tmp_s, args.boolean, args.tristate)

if __name__ == '__main__':
    main()
