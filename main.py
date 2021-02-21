"""MAIN PROGRAM TO LAUNCH CHECKERS"""

import sanity, config_check
import argparse

def main():
    parser = argparse.ArgumentParser(prog='Formula checker')
    parser.add_argument("--alloptions", type=str, help="alloptions-csv file",
                        required=True)
    parser.add_argument("--dimacs", type=str, help="dimacs file name",
                        required=True)
    parser.add_argument("--sanity", action="store_true",
                        help="enable sanity check")

    parser.add_argument("--ccheck", type=str, metavar=".CONFIG",
                        help=".config check. "\
                        "Must be followed by a configuration file")

    args = parser.parse_args()

    if args.sanity:
        print("SANITY CHECK")
        print("------------")
        sanity\
            .sanity_check_optionsvalues(args.dimacs, args.alloptions, True)
    elif args.ccheck:
        print(".CONFIG CHECK")
        print("-------------")
        config_check\
            .config_check(args.ccheck, args.dimacs, args.alloptions, True)
    else:
        print("No checker selcted. You must chose one.")

if __name__ == "__main__":
    main()
