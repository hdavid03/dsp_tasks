#!/bin/python3
from genericpath import exists
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


def convert_timestamps_to_ms(timestamps):
    ts_list = []
    for ts in timestamps:
        ts_list.append(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
    return ts_list

def calculate_sample_time(ts_list):
    step = 1
    ctr = 1
    finished = False
    while not finished :
        pre_dif = ts_list[step] - ts_list[0]
        dif = ts_list[step + step] - ts_list[step]
        ctr += 1
        if pre_dif != dif :
            step += 1
        else :
            stopped = False
            for i in range(ctr * step, len(ts_list), step):
                dif = ts_list[i] - ts_list[i - step]
                if dif != pre_dif:
                    stopped = True
                    break
        if stopped :
            step += 1
            continue
        else:
            finished = True
    return (ts_list[step] - ts_list[0]) / step;    


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
    ts_list = convert_timestamps_to_ms(arr[:, 0])
    fulltime = ts_list[6] - ts_list[0]
    print(fulltime)    
    sample_time = calculate_sample_time(ts_list)
    

if __name__ == '__main__' :
    main()