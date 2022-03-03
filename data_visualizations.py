from genericpath import exists
from posixpath import split
from time import strptime
from html5lib import serialize
from datetime import datetime
import pandas as ps
import matplotlib.pyplot as mplot
import numpy as np
import getopt
import sys

def usage():
    print(
        '-h --help for help\r\n-i --infile filename\r\n'
    )
    pass

def opt_walk(opts):
    verbose = False
    infile = None
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            return None
        elif o in ("-i", "--infile"):
            infile = a
        else:
            print("unhandled option")
            usage()
            return None
    return { 'verbose':verbose, 'infile':infile }


def convert_timestamps(timestamps):
    ts_list = []
    for i in timestamps:
        datetime_obj = strptime(i, '%Y-%m-%d %H:%M:%S%f')
        ts_list.append(datetime_obj.timestamp())
    return ts_list


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:v", ["help", "infile=", "verbose"])
    except getopt.GetoptError as err:
        print(err + '\r\n')
        usage()
        sys.exit(1)
    
    res = opt_walk(opts)
    verbose = res['verbose']
    infile = res['infile']
    
    if (infile == None) or (not exists(infile)) :
        print('there is no existing input file\r\nhint: -i, --infile filename')
        sys.exit(1)    
    
    data_set = ps.read_csv(infile, sep=',', squeeze=True, names=['time_stamp', 'acceleration'])
    arr = data_set.to_numpy()
    cols = data_set.columns
    keys = data_set.keys()
    for i in range(601):
        if i == 600:
            print(arr[i, 0])
    
    k = arr[3,0]
    print(k)
    d = datetime.strptime(k, '%Y-%m-%d %H:%M:%S.%f')
    m = d.timestamp() * 1000
    print(datetime.fromtimestamp(m / 1000))


if __name__ == '__main__' :
    main()