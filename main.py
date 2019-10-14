import os
import sys

cmd = "make randconfig"

def usage():
    print("python3 main.py [.config]file n")
    print("n\t number of tests")
    
def read(filename, data):
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


def main():
    if len(sys.argv) >= 1:
        data = dict()
        n = int(sys.argv[1])
        for i in range(n):
            os.system(cmd)
            read(".config", data)

        with open('data.csv', 'w') as stream:
            stream.write('{:64s};{}\n'.format('feature', 'occurence'))
            for k in data:
                stream.write('{:64s};{:d}\n'.format(k, data[k]))
    else :
        usage()

if __name__ == '__main__':
    try:
        main()
    except ValueError:
        print("Invalid size {}".format(sys.argv[-1]))
        exit(0)
            
