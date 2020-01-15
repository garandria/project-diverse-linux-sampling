import os
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ntests", help="Number of tests", type=int)
    args = parser.parse_args()
    for i in range(args.ntests):
        os.system('make randconfig -C {}\
        && echo "=== TEST_{} BOOL ==\n" >> out.txt\
        && python extractor.py --boolean ../kconfigreader/out.dimacs\
        ../linux-4.14.152/alloptions-x86.4.14.152.csv ../linux-4.14.152/.config\
        >> out.txt\
        && echo "\n=== TEST_{} TRISTATE ==\n" >> out.txt\
        && python extractor.py --tristate ../kconfigreader/out.dimacs\
        ../linux-4.14.152/alloptions-x86.4.14.152.csv ../linux-4.14.152/.config\
        >> out.txt\
        && echo "\n=== TEST_{} BOOL & TRISTATE ==\n" >> out.txt\
        && python extractor.py --boolean --tristate ../kconfigreader/out.dimacs\
        ../linux-4.14.152/alloptions-x86.4.14.152.csv ../linux-4.14.152/.config\
        >> out.txt'.format("../linux-4.14.152", i, i, i))

if __name__ == '__main__':
    main()
