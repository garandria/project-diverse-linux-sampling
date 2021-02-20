"""SANITY CHECK"""

from pysat.formula import CNF
from pysat.solvers import *
import os
import utils
import argparse

def sanity_check_optionsvalues(dimacs, alloptions, verbose=False):
    """Sanity checks the formula

    :param dimacs: DIMACS file contaning the formula to check
    :type dimacs: str
    :param alloptions: CSV file of all options
    :type alloptions: str
    """

    impossible_values = dict()
    def add_impossible_value(option, value):
        if option not in impossible_values:
            impossible_values[option] = {value}
        else:
            impossible_values[option].add(value)

    dimacs = utils.DimacsFla(dimacs)
    fla = dimacs.get_formula()
    variables = dimacs.get_variables()

    alloptions = utils.Alloptions(alloptions)

    # sanity check
    with Solver(bootstrap_with=fla.clauses) as l:
        if verbose:
            print("* At the beginning, fla is", l.solve(assumptions=[]))
        for k, v in variables.items():
            # TODO: if I will remember there is a true option called
            # SOMETHINGXXX_MODULE
            # not in Linux options (dummy variables to emulate tristate)
            # not in Linux options (dummy variables to emulate choices)
            if (v.endswith("_MODULE") or "CHOICE_" in v):  
                continue # ignore

            kconfig_type = alloptions.get_kconfig_type(v)

            if (kconfig_type == 'BOOL'):
                # we try true/false values                
                if not l.solve(assumptions=[k]):
                    if verbose:
                        print("[B] {}:{} cannot take the 'y' value "\
                              "(dead feature)".format(k, v))
                    add_impossible_value(v, 'y')
                if not l.solve(assumptions=[-k]):
                    if verbose:
                        print("[B] {}:{} cannot take the 'n' value"\
                              "(core feature)".format(k, v))
                    add_impossible_value(v, 'n')
            elif(kconfig_type == 'TRISTATE'):
                # we have to find the other "module" variable that emulates the
                # "m" value
                kmodule = dimacs.get_kmodule(v)
                
                # if an option "opt" is a module, a variable "opt_MODULE" should
                # exist in the formula. If it is not the case, either the
                # formula is not consistent or alloptions and the formula were
                # not generated from the same Linux Kernel version.               
                assert kmodule is not None,\
                    "Module not represented as module in the fomula"
                
                # we have to try y, n, and m
                # yes: k and !kmodule
                if not l.solve(assumptions=[k, -kmodule]):
                    if verbose:
                        print("[T] {}:{} cannot take the 'y' value"\
                              .format(k, v))
                    add_impossible_value(v, 'y')
                # no: !k and !kmodule
                if not l.solve(assumptions=[-k, -kmodule]):
                    if verbose:
                        print("[T] {}:{} cannot take the 'n' value"\
                              .format(k, v))
                    add_impossible_value(v, 'n')
                # module: !k and kmodule 
                if not l.solve(assumptions=[-k, kmodule]):
                    if verbose:
                        print("[T] {}:{} cannot take the 'm' value"\
                              .format(k, v))
                    add_impossible_value(v, 'm')
                # this case is not possible: k and kmodule
                # print("trying", v, k, "with three values")
            elif(kconfig_type == 'STRING'):
                continue # TODO?
            elif(kconfig_type == 'INT'):
                continue # TODO?
            else:
                continue # TODO?
            # print(k, v)

    return impossible_values

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alloptions", type=str, help="alloptions-csv file",
                        required=True)
    parser.add_argument("--dimacs", type=str, help="dimacs file name",
                        required=True)
    # parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    sanity_check_optionsvalues(args.dimacs, args.alloptions, True)


if __name__ == "__main__":
    main()
