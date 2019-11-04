
class CSVFile:

    def __init__(self, filename, column=1, sep=',', comment='#'):
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
        self.__type_dict_built = False

    def getType(self, option):
        return self.__options[option]

    def getOptions(self):
        return set(self.__options)

    def getTypeDict(self):
        if not self.__type_dict_built:
            self.__buildTypeDict()
            self.__type_dict_built = False

    def __buildTypeDict(self):
        self.__type_dict = dict()
        for feat in self.__features:
            try:
                self.__type_dict[feat].add(self.__features[feat])
            except KeyError:
                self.__type_dict[feat] = {self.__features[feat]}


class DimacsFile:

    def __init__(self, filename):
        self.__features = dict()
        self.__variables = set()
        with open(filename, 'r') as stream:
            line = stream.readline()
            while line:
                if line[0] == 'c':
                    # c 666 FEATURE_NAME
                    feature = line.split()[2].rstrip('\n').strip()
                    number = int(line.split()[1].strip())
                    self.__features[feature] = number
                    self.__variables.add(number)
                elif line[0] == 'p':
                    stream.readline()
                else:
                    line = stream.readline()
                    mlist = line.split()
                    mlist = list(map(mlist, int))
                    mlist = list(map(mlist, abs))
                    for k in mlist:
                        self.__variables.add(k)
        self.__features_clean_set = self.__cleanSet(set(self.__features))
        self.__name_variation_dict_built = False

    def getNbFeatures(self):
        return len(self.__features)

    def getRealNbFeatures(self):
        return len(self.__features_clean_set)

    def getNbVariables(self):
        return len(self.__variables)

    def getVariableOf(self, feature):
        return self.__features[feature]

    def __cleanSet(mset):
        res = set()
        for elt in mset:
            if '=' in elt:
                res.add(elt.split('=')[0].split('_MODULE')[0].strip())
            else:
                res.add(elt.split('_MODULE')[0].strip())
        return res

    def __buildNameVariationDiff(self):
        self.__name_variation = dict()
        for feat in self.__features_clean_set:
            for rep in self.__features:
                if str.startswith(rep, feat):
                    try:
                        self.__name_variation[feat].add(rep)
                    except KeyError:
                        self.__name_variation[feat] = {rep}

    def getNameVariationDict(self):
        if not self.__name_variation_dict_built:
            self.__buildNameVariationDiff()
            self.__name_variation_dict_built = True
