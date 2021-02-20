"""CHECK CONFIGURATION"""

from pysat.formula import CNF
from pysat.solvers import *
import utils
import argparse


def config_check(config, dimacs, alloptions_file, verbose=False):
    """Checks configuration's integrity

    :param config: .config file
    :type config: str
    :param dimacs: DIMACS file
    :type dimacs: str
    :param alloptions: alloptions csv file
    :type alloptions: str
    :return: SAT, LAST CLAUSE, UNSATISFIABILITY CORE
    :rtype: tuple
    """
    dconfig = utils.read_config(config)
    
    dimacs = utils.DimacsFla(dimacs)
    fla = dimacs.get_formula()
    variables = dimacs.get_variables()

    alloptions = utils.Alloptions(alloptions_file)

    assumptions = []

    with Solver(bootstrap_with=fla.clauses) as l:
        if verbose:
            print("* At the beginning, fla is", l.solve(assumptions=assumptions))
        for k, v in variables.items():
            if (v.endswith("_MODULE") or "CHOICE_" in v):
                continue    # ignore

            # SYMBOLS \IN .CONFIG
            if v in dconfig:
                kconfig_type = alloptions.get_kconfig_type(v)
                vprint = ""
                if kconfig_type == "TRISTATE":
                    kmodule = dimacs.get_kmodule(v)
                    if dconfig[v] == 'y':
                        vprint = "[T] {}:{} ^ {}:{}_MODULE"\
                                                .format(k, v, -kmodule, v)
                        assumptions.extend([k, -kmodule])
                    elif dconfig[v] == 'm':
                        vprint = "[T] {}:{} ^ {}:{}_MODULE"\
                                                .format(-k, v, kmodule, v)
                        assumptions.extend([-k, kmodule])
                    if verbose:
                        print(vprint)
                    # SOLVE
                    if not l.solve(assumptions=assumptions):
                        if verbose:
                            vcore = " ^ ".join(list(map(
                                (lambda x : '~' + variables[abs(x)] if (x < 0)
                                 else variables[x]), l.get_core())))
                            print("---")
                            print("/!\ UNSATISFIABLE")
                            print("Unsatisfiable core:", vcore)
                        return False, assumptions[-2:], l.get_core()
                if kconfig_type == "BOOL":
                    vprint = "[B] {}:{}".format(k, v)
                    if verbose:
                        print(vprint)
                    assumptions.append(k)
                    # SOLVE
                    if not l.solve(assumptions=assumptions):
                        if verbose:
                            vcore = " ^ ".join(list(map(
                                (lambda x : '~' + variables[abs(x)] if (x < 0)
                                 else variables[x]), l.get_core())))
                            print("---")
                            print("/!\ UNSATISFIABLE")
                            print("Unsatisfiable core:", vcore)
                        return False, assumptions[-1], l.get_core()
        # NOT IN .CONFIG
        for k, v in variables.items():
            if (v.endswith("_MODULE") or "CHOICE_" in v):
                continue    # ignore
            
            if (v in alloptions.get_options()) and (v not in dconfig):
                kconfig_type = alloptions.get_kconfig_type(v)

                if kconfig_type == "TRISTATE":
                    kmodule = dimacs.get_kmodule(v)
                    vprint = "[T] {}:{} ^ {}:{}_MODULE"\
                        .format(-k, v, -kmodule, v)
                    if verbose:
                        print(vprint)
                    assumptions.extend([-k, -kmodule])
                    # SOLVE
                    if not l.solve(assumptions=assumptions):
                        if verbose:
                            vcore = " ^ ".join(list(map(
                                (lambda x : '~' + variables[abs(x)] if (x < 0)
                                 else variables[x]), l.get_core())))
                            print("---")
                            print("/!\ UNSATISFIABLE")
                            print("Unsatisfiable core:", vcore)
                        return False, assumptions[-2:], l.get_core()
                elif kconfig_type == "BOOL":
                    vprint = "[B] {}:{}".format(-k, v)
                    if verbose:
                        print(vprint)
                    assumptions.append(-k)
                    # SOLVE
                    if not l.solve(assumptions=assumptions):
                        if verbose:
                            vcore = " ^ ".join(list(map(
                                (lambda x : '~' + variables[abs(x)] if (x < 0)
                                 else variables[x]), l.get_core())))
                            print("---")
                            print("/!\ UNSATISFIABLE")
                            print("Unsatisfiable core:", vcore)
                        return False, assumptions[-1], l.get_core()
    if verbose:
        print("---")
        print("[DONE] SAT")
    return True, None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help=".config file",
                        required=True)
    parser.add_argument("--dimacs", type=str, help="dimacs file",
                        required=True)
    parser.add_argument("--alloptions", type=str, help="alloptions-csv file",
                        required=True)
    
    # parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    config_check(args.config, args.dimacs, args.alloptions, True)


if __name__ == "__main__":
    main()
