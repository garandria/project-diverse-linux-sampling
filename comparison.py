'''
'''

TUXML_FILENAME='alloptions.csv'
DIMACS_FILENAME='out.dimacs'

def csv_reader(filename, column, sep=';', comment='#'):
    '''
    '''
    res = set()
    col = column - 1
    assert(col > 0, 'Negative column number')
    with open(filename, 'r') as stream:
        line = readline()
        while not line:
            if not (line[0] == comment):
                feature = line.split(sep)[col]
                res.add(feature)
            line = readline()
    return res



