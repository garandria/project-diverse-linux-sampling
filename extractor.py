import os
import argparse
from file import DimacsFile, CSVFile, Checker


DIMACS = "../kconfigreader/out.dimacs"
CONFIG_DIR = "../linux-4.14.152"
CSV = "../linux-4.14.152/alloptions-x86.4.14.152.csv"
CONF = ["tinyconfig", "randconfig"] #, "defconfig", "allnoconfig",\
#        "allyesconfig", "allmodconfig", "alldefconfig"]


def main():
    ''' main function '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdir", type=str, default=CONFIG_DIR,
                        help="local directory of linux source code \
                        (to launch the Makefile)")
    parser.add_argument("--dimacs", type=str, default=DIMACS,
                        help="dimacs file name")
    parser.add_argument("--csv", type=str, default=CSV,
                        help="all options csv file")
    parser.add_argument("-n", type=int, default=20,
                        help="nb of iteration")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    stream = open("extractor_out.csv", "w")
    stream.write("name,nb_yes,nb_mod,bool,tristate,both,last_clause,in\n")
    for i in range(args.n):
        for configuration in CONF:
            os.system("KCONFIG_ALLCONFIG=x86_64.config make {} -C {}".format(configuration, args.cdir))
            checker = Checker(args.dimacs, args.csv, args.verbose)
            checker.set_dot_config_file("{}/.config".format(args.cdir))
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
            stream.write("{},{},{},{},{},{},{},{}\n"\
                .format(name, nb["y"], nb["m"], res_bool["return"],
                        res_tristate["return"], res_both["return"],
                        last_clause, in_formula))
    stream.close()

if __name__ == '__main__':
    main()
