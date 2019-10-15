

def read(filename):
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
