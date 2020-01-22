import os
import argparse
from file import DimacsFile, CSVFile, Checker


DIMACS = "../../kconfigreader/out.dimacs"
CONFIG_DIR = "../../linux-4.14.152"
CSV = "../../linux-4.14.152/alloptions-x86.4.14.152.csv"
CONF = ["tinyconfig", "randconfig"] #, "defconfig", "allnoconfig",\
#        "allyesconfig", "allmodconfig", "alldefconfig"]


def main():
    ''' main function '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=20,
                        help="no of iteration")
    args = parser.parse_args()
    out = "name,nb_yes,nb_mod,bool,tristate,both,last_clause,in\n"
    for i in range(args.n):
        for configuration in CONF:
            os.system("make {} -C {}".format(configuration, CONFIG_DIR))
            checker = Checker(DIMACS, CSV)
            checker.set_dot_config_file("{}/.config".format(CONFIG_DIR))
            nb = checker.get_nb_tristate()
            res_bool = checker.check_bool()
            checker.clean()
            res_tristate = checker.check_tristate()
            checker.clean()
            res_both = checker.check_bool()
            if res_both["return"]:
                res_both = checker.check_tristate()
            name = "{}_{}".format(configuration, i)
            last_clause = "{}/{}/{}".format(res_bool["last_clause"],
                                            res_tristate["last_clause"],
                                            res_both["last_clause"])
            in_formula = "{}/{}/{}".format(res_bool["In"], res_tristate["In"],
                                           res_both["In"])
            out += "{},{},{},{},{},{},{},{}\n"\
                .format(name, nb["y"], nb["m"], res_bool["return"],
                        res_tristate["return"], res_both["return"],
                        last_clause, in_formula)
    with open("extractor_out.csv", "w") as stream:
        stream.write(out)


if __name__ == '__main__':
    main()
