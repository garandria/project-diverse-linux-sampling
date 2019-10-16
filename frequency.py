'''This program generates .config files a certain amount of time
(number given by the user) then generate a csv file that contains the
options of the .config file and its frequency.

'''

__author__ = "Georges Aaron RANDRIANAINA"
__email__ = "georges-aaron.randrianaina@ens-rennes.fr"

import os
import argparse


def read(filename):
    '''Reads a .config file and returns
    :param: .config filename
    :type: string
    :return: table containing {option : frequency}
    :rtype: dict
    '''
    data = dict()
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line != '':
            if not ('#' in line or line[0] == '\n'):
                res = line.split('=')[0]
                try:
                    data[res] += 1
                except KeyError:
                    data[res] = 1
            line = stream.readline()
    return data


def main():
    '''Main program
    Parse the input argument then launch the .config generation n
    times (n given by the use) and saves the options of each file
    using `read`.

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('dir',
                        help='path to directory containing the makefile')
    parser.add_argument('-n', dest='ntests', default=50, type=int,
                        help='Number of .config files to generate')
    args = parser.parse_args()

    if args.dir[-1] != ['/']:
        args.dir += '/'
        
    data = dict()
    for i in range(args.ntests):
        os.system('make randconfig -C {}'.format(args.dir))
        data = read('{}.config'.format(args.dir))

    content = ''
    content += '{:64s};{}\n'.format('feature', 'occurence')
    for k in data:
        content += '{:64s};{:d}\n'.format(k, data[k])
    with open('data_{}.csv'.format(args.ntests), 'w') as stream:
        stream.write(content)


if __name__ == '__main__':
    main()
