'''This file contains classes to process CSV & dimacs files of linux
   features

For an example of dimacs file, see :
https://github.com/PettTo/Feature-Model-History-of-Linux/tree/master/2017/2017-09-11T13_10_57-07_00

For an example of a csv file with all options, see :
https://github.com/TuxML/Kanalyser/blob/master/alloptions-x64-v4.15.csv

'''
import os
from pysat.formula import CNF
from pysat.solvers import Solver


DOT_DIR = 'dot'
IMG_DIR = 'img'


class CSVFile:
    """Class that takes info from csv file of features"""

    def __init__(self, filename, column=1, sep=',', comment='#'):
        self.__filename = filename
        self.__features = dict()
        column -= 1
        with open(filename, 'r') as stream:
            stream.readline()       # first line (title)
            line = stream.readline()
            while line:
                if not line[0] == comment:
                    feature = line.split(sep)[column]
                    # assert feature != '', 'CSV : feature empty'
                    ftype = line.split(sep)[column + 1]\
                                .rstrip('\n')\
                                .strip()
                    # assert ftype != '', 'CSV : ftype empty'
                    self.__features[feature] = ftype.strip()
                    line = stream.readline()
        self.__nb_features = len(self.__features)
        self.__features_set = set(self.__features)
        self.__type_dict = None
        self.__type_len = None

    def getFileName(self):
        return self.__filename

    def getType(self, feat):
        return self.__features[feat]

    def getFeaturesSet(self):
        return self.__features_set

    def getFeatures(self):
        return self.__features

    def getNbFeatures(self):
        return self.__nb_features

    def getNbTypes(self):
        if self.__type_len is None:
            self.__buildTypeDict()
            self.__type_len = len(self.__type_dict)
        return self.__type_len

    def getTypeDict(self):
        if self.__type_dict is None:
            self.__buildTypeDict()
        return self.__type_dict

    def __buildTypeDict(self):
        self.__type_dict = dict()
        for feat in self.__features:
            try:
                self.__type_dict[self.__features[feat]].add(feat)
            except KeyError:
                self.__type_dict[self.__features[feat]] = {feat}

    def diff(self, other):
        res = set()
        for elt in self.__features_set:
            if not (elt in other):
                res.add(elt)
        return res


class DimacsFile:
    """ Class for dimacs files"""

    def __init__(self, filename):
        self.__filename = filename
        self.__features = dict()
        self.__variables = set()
        self.__nb_variables = 0
        self.__nb_clauses = 0
        stream = open(filename, 'r')
        content = stream.readlines()
        stream.close()
        for line in content:
            if line[0] == 'c':
                # c 666 FEATURE_NAME
                feature = line.split()[2].rstrip('\n').strip()
                number = int(line.split()[1].strip())
                self.__features[feature] = number
                self.__variables.add(number)
            elif line[0] == 'p':
                mline = list(map(int, line.split()[2:]))
                self.__nb_variables, self.__nb_clauses = mline[0], mline[1]
            else:
                mlist = line.split()[:-1]
                mlist = list(map(int, mlist))
                mlist = list(map(abs, mlist))
                for k in mlist:
                    self.__variables.add(k)
        self.__features_set = set(self.__features)
        self.__features_clean_set = self.__cleanSet(self.__features_set)
        self.__nb_features = len(self.__features_clean_set)
        self.__name_variation_dict = None
        assert self.__nb_variables == len(self.__variables)

    def getFileName(self):
        return self.__filename

    def getRealNbFeatures(self):
        return self.__nb_features

    def getNbClauses(self):
        return self.__nb_clauses

    def getNbVariables(self):
        return self.__nb_variables

    def getRealFeaturesSet(self):
        return self.__features_clean_set

    def getFeaturesSet(self):
        return self.__features_set

    def getVariableOf(self, feature):
        return self.__features[feature]

    # def __cleanName(self, name):
    #     if '=' in name:
    #         return name.split('=')[0].split('_MODULE')[0].strip()
    #     else:
    #         return name.split('_MODULE')[0].strip()

    def __cleanName(self, name):
        if '=' in name:
            return name.split('=')[0].split('_MODULE')[0].strip()
        else:
            if '_MODULE' in name:
                return name[:-7].strip()
            else:
                return name.strip()

    def __cleanSet(self, mset):
        res = set()
        for elt in mset:
            res.add(self.__cleanName(elt))
        return res

    @staticmethod
    def __my_contains(prefix, word):
        ''' Checking the prefix '''
        if word.startswith(prefix):
            if prefix[-3:] == "MOD":
                return not word[len(prefix):].startswith("ULE")
            return True

    def __buildNameVariationDiff(self):
        self.__name_variation_dict = dict()
        features_list_sorted = sorted(list(self.__features_clean_set),
                                      key=len, reverse=True)
        added = set()
        for feat in features_list_sorted:
            for rep in self.__features:
                if rep not in added and DimacsFile.__my_contains(feat, rep):
                        # str.startswith(rep, feat):
                    try:
                        self.__name_variation_dict[feat].add(rep)
                    except KeyError:
                        self.__name_variation_dict[feat] = {rep}
                    added.add(rep)

    def getNameVariationDict(self):
        if self.__name_variation_dict is None:
            self.__buildNameVariationDiff()
        return self.__name_variation_dict

    def diff(self, other):
        res = set()
        for elt in self.__features_clean_set:
            if not (elt in other):
                res.add(elt)
        return res

    def getNameTreeOf(self, feature):
        # from PIL import Image
        res = 'graph {\n'
        for elt in self.getNameVariationDict()[feature]:
            res += '"{}" -- "{} "\n'.format(feature, elt)
        res += '}'
        with open('{}/{}.dot'.format(DOT_DIR, feature), 'w') as stream:
            stream.write(res)
        os.system('dot -T png -O {}/{}.dot'.format(DOT_DIR, feature))
        # Image.open('{}.dot'.format(feature)).show()
        os.system('eom {}/{}.dot.png'.format(IMG_DIR, feature))

    def getNamesOf(self, name):
        if self.__name_variation_dict is None:
            self.getNameVariationDict()
        else:
            return self.getNameTreeOf()[name]


class Checker:
    """ """

    def __init__(self, dimacs_file, csv_file, verbose=False):
        self.__dimacs = DimacsFile(dimacs_file)
        self.__csv = CSVFile(csv_file)
        self.__cnf = CNF(from_file=dimacs_file)
        self.__formula = Solver(bootstrap_with=self.__cnf.clauses)
        assert self.__formula.solve() is True, "initial formula is UNSAT"
        self.__config_d = None
        self.__verbose = verbose

    def clean(self):
        self.__formula = Solver(bootstrap_with=self.__cnf.clauses)
        assert self.__formula.solve() is True, "initial formula is UNSAT"


    def set_dot_config_file(self, filename):
        self.__config_d = Checker.__read_file(filename)

    def check_tristate(self, dot_config_file=None):
        if dot_config_file is not None:
            self.set_dot_config_file(dot_config_file)
        if self.__verbose:
            print("=> ADDING FEATURES FROM .CONFIG FILE [TRISTATE]")
            print("-----------------------------------------------")
        for feature in self.__config_d:
            if feature in self.__dimacs.getFeaturesSet():
                if feature in self.__csv.getFeaturesSet():
                    if self.__csv.getType(feature) == "TRISTATE":
                        feat_mod = "{}_MODULE".format(feature)
                        var_for_name = self.__dimacs.getVariableOf(feature)
                        var_for_module = self.__dimacs.getVariableOf(feat_mod)
                        if self.__config_d[feature] == 'y':
                            if self.__verbose:
                                print("+ Adding clause: {}({})"
                                      .format(feature, var_for_name))
                            if not self.__formula\
                                       .add_clause([var_for_name],
                                                   no_return=False):
                                if self.__verbose:
                                    print("== UNSAT")
                                return {"return" : False,
                                        "last_clause" : feature,
                                        "In" : True}
                            if self.__verbose:
                                print("+ Adding clause: {}({})"
                                      .format(feat_mod, var_for_module))
                            if not self.__formula\
                                       .add_clause([-var_for_module],
                                                   no_return=False):
                                if self.__verbose:
                                    print("== UNSAT")
                                return {"return" : False,
                                        "last_clause" : feat_mod,
                                        "In" : True}
                        elif self.__config_d[feature] == 'm':
                            if self.__verbose:
                                print("+ Adding clause: {}({})"
                                      .format(feature, var_for_name))
                            if not self.__formula\
                                       .add_clause([var_for_name],
                                                   no_return=False):
                                if self.__verbose:
                                    print("== UNSAT")
                                return {"return" : False,
                                        "last_clause" : feature,
                                        "In" : True}
                            if self.__verbose:
                                print("+ Adding clause: {}({})"
                                      .format(feat_mod, var_for_module))
                            if not self.__formula\
                                       .add_clause([var_for_module],
                                                   no_return=False):
                                if self.__verbose:
                                    print("== UNSAT")
                                return {"return" : False,
                                        "last_clause" : feat_mod,
                                        "In" : True}
            #     else:
            #         print("/!\\ {} not in CSV".format(feature))
            # else:
            #     print("/!\\ {} not in DIMACS".format(feature))
        if self.__verbose:
            print()
            print("=> ADDING FEATURES THAT ARE NOT IN THE .CONFIG [TRISTATE]")
            print("---------------------------------------------------------")
        for feature in self.__csv.getFeaturesSet():
            if feature not in set(self.__config_d)\
               and feature in self.__dimacs.getFeaturesSet():
                if self.__csv.getType(feature) == "TRISTATE":
                    feat_mod = "{}_MODULE".format(feature)
                    var_for_name = self.__dimacs.getVariableOf(feature)
                    var_for_module = self.__dimacs.getVariableOf(feat_mod)
                    if self.__verbose:
                        print("+ Adding clause: {} ({})"
                              .format(feature, -var_for_name))
                    if not self.__formula\
                               .add_clause([-var_for_name], no_return=False):
                        if self.__verbose:
                            print("== UNSAT")
                        return {"return" : False,
                                "last_clause" : feature,
                                "In" : False}
                    if self.__verbose:
                        print("+ Adding clause: {} ({})"
                              .format(feat_mod, -var_for_module))
                    if not self.__formula\
                               .add_clause([-var_for_module], no_return=False):
                        if self.__verbose:
                            print("== UNSAT")
                        return {"return" : False,
                                "last_clause" : feat_mod,
                                "In" : False}
        if self.__verbose:
            print("== SAT")
        return {"return" : True,
                "last_clause" : None,
                "In" : None}

    def check_bool(self, dot_config_file=None):
        if dot_config_file is not None:
            self.set_dot_config_file(dot_config_file)
        if self.__verbose:
            print("=> ADDING FEATURES FROM .CONFIG FILE [BOOL]")
            print("-----------------------------------------------")
        for feature in self.__config_d:
            if feature in self.__dimacs.getFeaturesSet():
                if feature in self.__csv.getFeaturesSet():
                    if self.__csv.getType(feature) == "BOOL":
                        var_name = self.__dimacs.getVariableOf(feature)
                        if self.__verbose:
                            print("+ Adding clause: {} ({})"
                                  .format(feature, var_name))
                        if not self.__formula\
                                   .add_clause([var_name], no_return=False):
                            if self.__verbose:
                                print("== UNSAT")
                            return {"return" : False,
                                    "last_clause" : feature,
                                    "In" : True}
            #     else:
            #         print("/!\\ {} not in CSV".format(feature))
            # else:
            #     print("/!\\ {} not in DIMACS".format(feature))
        if self.__verbose:
            print()
            print("=> ADDING FEATURES THAT ARE NOT IN THE .CONFIG [BOOL]")
            print("-----------------------------------------------------")
        for feature in self.__csv.getFeaturesSet():
            if feature not in set(self.__config_d)\
               and feature in self.__dimacs.getFeaturesSet():
                if self.__csv.getType(feature) == "BOOL":
                    var_name = self.__dimacs.getVariableOf(feature)
                    if self.__verbose:
                        print("+ Adding clause: {} ({})".format(feature, -var_name))
                    if not self.__formula\
                           .add_clause([-var_name], no_return=False):
                        if self.__verbose:
                            print("== UNSAT")
                        return {"return" : False,
                                "last_clause" : feature,
                                "In" : False}
        if self.__verbose:
            print("== SAT")
        return {"return" : True,
                "last_clause" : None,
                "In" : None}

    @staticmethod
    def __read_file(filename):
        res = dict()
        with open(filename, 'r') as stream:
            for line in stream:
                if line[0] != '#' and line != '\n':
                    feature = line[7:]
                    flist = feature.split('=')
                    res[flist[0]] = flist[1].rstrip('\n')
        return res

    def get_nb_tristate(self):
        res = {"y" : 0, "m" : 0}
        for elt in self.__config_d:
            if self.__config_d[elt] == 'y':
                res["y"] += 1
            elif self.__config_d[elt] == 'm':
                res["m"] += 1
        return res
