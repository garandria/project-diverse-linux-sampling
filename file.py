import os

DOT_DIR = 'dot'
IMG_DIR = 'img'


class CSVFile:

    def __init__(self, filename, column=1, sep=',', comment='#'):
        self.__filename = filename
        self.__features = dict()
        self.__separator = sep
        self.__comment = comment
        self.__column = column - 1
        with open(filename, 'r') as stream:
            stream.readline()       # first line (title)
            line = stream.readline()
            while line:
                if not (line[0] == comment):
                    feature = line.split(self.__separator)[self.__column]
                    # assert feature != '', 'CSV : feature empty'
                    ftype = line.split(self.__separator)[self.__column + 1]\
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
        self.__features_clean_set = self.__cleanSet(set(self.__features))
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

    def getVariableOf(self, feature):
        return self.__features[feature]

    def __cleanName(self, name):
        if '=' in name:
            return name.split('=')[0].split('_MODULE')[0].strip()
        else:
            return name.split('_MODULE')[0].strip()

    def __cleanSet(self, mset):
        res = set()
        for elt in mset:
            res.add(self.__cleanName(elt))
        return res

    def __buildNameVariationDiff(self):
        self.__name_variation_dict = dict()
        features_list_sorted = sorted(list(self.__features_clean_set),
                                      key=len, reverse=True)
        added = set()
        for feat in features_list_sorted:
            for rep in self.__features:
                if rep not in added and str.startswith(rep, feat):
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
