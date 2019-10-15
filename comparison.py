'''
'''

TUXML_FILENAME='alloptions.csv'
DIMACS_FILENAME='../Feature-Model-History-of-Linux/2017/2017-09-11T13_10_57-07_00/2017/2017-09-11T13_10_57-07_00/out.dimacs'

def csv_reader(filename, column=1, sep=';', comment='#'):
    '''
    '''
    res = set()
    col = column - 1
    with open(filename, 'r') as stream:
        stream.readline()       # first line (title)
        line = stream.readline()        
        while line:
            if not (line[0] == comment):
                feature = line.split(sep)[col]
                res.add(feature)
            line = stream.readline()
    return res


def dimacs_reader(filename, clean=False):
    '''
    '''
    res = set()
    with open(filename, 'r') as stream:
        line = stream.readline()
        while line[0] == 'c':
            # c 666 FEATURE_NAME
            feature = line.split(' ')[2].split('\n')[0]
            if clean:
                feature = feature.split('=')[0]
            res.add(feature)
            line = stream.readline()
    return res
