"""Utils"""

import re
import pandas as pd
from pysat.formula import CNF

class DimacsFla:
    """DimacsFla class represents the DIMACS formula of the current Linux Kernel.

    :param dimacs: path to the file of the formula in dimacs format
    :type dimacs: str
    """
    
    def __init__(self, dimacs):
        """Constructor
        """
        self.__dimacs = self._dimacs_read(dimacs)
        self.__formula = CNF(dimacs)

    def _dimacs_read(self, dimacs):
        """Read a dimacs file

        :param dimacs: Dimacs format file
        :type dimacs: str
        :return: dictionary {variable: feature}
        :rtype: dict
        """
        variables = dict()
        with open(dimacs, 'r') as f:
            dimacs_lines = f.readlines()
            for line in dimacs_lines:
                if line.startswith("c"):
                    m = re.search('(c) (\d+) (\w+)', line)
                    var_id = int(m.group(2))
                    var_name = m.group(3)  
                    variables[var_id] = var_name
        return variables

    def get_variables(self):
        """Gives the dictionary of {id: variable}
        
        :return: variables from the DIMACS formula
        :rtype: dict
        """
        return self.__dimacs

    def get_kmodule(self, symbol):
        """Retrieve the DIMACS ID of module variable associated with the given 
        symbol.

        :param symbol: symbol name
        :type symbole: str
        :return: {symbol}_MODULE ID iff symbol is a modyle; None otherwise
        :rtype: int iff symbol is a module; NoneType otherwise
        """
        for k, v in self.__dimacs.items():
            if v == "{}_MODULE".format(symbol):
                return k

class Alloptions:
    """Alloptions class represents the csv of all options of a Linux Kernel.

    Use Kanalyser (https://github.com/TuxML/Kanalyser/) to generate a csv file of
    all symboles and their type.

    :param alloptions: src csv file
    :type alloptions: str
    """

    def __init__(self, alloptions):
        """Constructor method"""
        self.__alloptions = pd.read_csv(alloptions)

    def get_options(self):
        """Gives the dataframe containing options and their types
        
        :return: options and their types
        :rtype: pd.Dataframe
        """
        return self.__alloptions
    
    def get_kconfig_type(self, symbol):
        """Retrieve the type of a kconfig symbol

        :param symbol: name of the option
        :type symbol: str
        :return: type of the option
        :rtype: str
        """
        ktype = self.__alloptions\
                    .query("option == " + '"' + option_name + '"')['type']
        return ktype.values[0]
