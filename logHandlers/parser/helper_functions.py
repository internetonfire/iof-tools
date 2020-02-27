import itertools as it
import pandas as pd
import numpy as np
import argparse
import datetime
from os import walk, path
from pandas_BGP import args, delta

log_types = ['FATAL', 'RECONF']

class WrongLogLine(Exception):
    pass


class WrongFileName(Exception):
    pass


def make_index(t_r_number=3, run_id_number=3, AS_number=5, strategy=['']):
    AS_list = ['AS' + str(x) for x in range(AS_number)]
    t_r_list = AS_list[:t_r_number]
    run_id_list = list(range(run_id_number))
    return([t_r_list, run_id_list, AS_list, strategy])


def fill_run_table(names, t_r_list, run_id_list, AS_list, strategy, mode='ZERO', samples=0, delta='100ms'):
    """ creates a list of dictionaries to fill a multiindex dataframe with
        dummy data """
    data = []
    time_data = []
    max_d = 9
    zero_time = pd.Timedelta('0 days 00:00:00')
    timedelta = pd.Timedelta(delta)
    end_time = zero_time + timedelta*samples
    for idx, val in enumerate(it.product(t_r_list, run_id_list, AS_list, strategy)):
        tot_updates = idx
        updates = [0] * samples
        if mode == 'RANDOM':
            updates = np.random.randn(samples)
        if mode == 'LINEAR':
            updates = [idx] * samples
        if mode == 'INCREASING':
            updates = range(samples)
        if mode == 'INCREASING_L':
            updates = [x*idx for x in range(samples)]
        data_dict = {}
        tot_updates = sum(updates)
        for i in range(len(names)): 
            data_dict[names[i]] = str(val[i])
        data_dict['tot_updates'] =  tot_updates
        data_dict['distance_AS_from_tr'] =  np.random.randint(max_d) + 1
        data_dict['distance_tr_to_t'] =  np.random.randint(1,4)
        data_dict['distance_AS_after_t'] = max(data_dict['distance_AS_from_tr'] -\
                                           data_dict['distance_tr_to_t'], 0)
        slot_len = samples/max_d
        conv_sample = max((data_dict['distance_AS_from_tr']-1) * slot_len +\
                np.random.randint(-slot_len, slot_len-1), 0)
        data_dict['conv_time'] = zero_time + timedelta*conv_sample
        data_dict['last_up_time'] = max(data_dict['conv_time'] +\
                timedelta*np.random.rand()*slot_len, zero_time)
        data_dict['first_up_time'] = max(data_dict['conv_time'] -\
                timedelta*np.random.rand()*slot_len, zero_time)
        data.append(data_dict)
        time_data.append(updates)
    return data, np.matrix.transpose(np.array(time_data))
 

# se puoi leggere l'AS riconfigurato dal nome della cartella, fai prima quel file e trova il tempo di riconfigurazione
# trova i T nodes come si faceva prima.
# 

def parse_args():
    global args
    parser = argparse.ArgumentParser()
    #parser.add_argument('-f', help='the log file', required=False, nargs='*')
    parser.add_argument('-ff', help='Folder with log Folders', required=False)
    parser.add_argument('-v', help='be more verbose', default=False,
                        action='store_true')
    #parser.add_argument('-c', help='Compute convergence delay', default=False,
    #                    action='store_true')
    #parser.add_argument('-t', help='compute the number of updates generated',
    #                    default=False, action='store_true')
    parser.add_argument('-T', help='time resolution (s/decimal/cent/milli)',
                        default='SEC',
                        choices=['SECS', 'DSEC', 'CSEC', 'MSEC'])
    #parser.add_argument('-d', required=False, default=0, action='store', 
    #        help="Use this option to see a negative delta")
    parser.add_argument('--tnodes', required=False, default=-1, type=int,
            help="Assume the first X nodes are T nodes")
    parser.add_argument('-l', required=False, default=-1, 
            help="Limit the number of runs to consider, helps speeding up development",
            type=int)
    args = parser.parse_args()

    if not (args.ff):
        parser.error('No folders provided, you have to choose at one type of folder to pass')

    if args.T == 'SEC':
        delta = '1s'
    elif args.T == 'DSEC':
        delta = '100ms'
    elif args.T == 'CSEC':
        delta = '10ms'
    elif args.T == 'MSEC':
        delta = '1ms'



def parse_line(line, verb):
    split_line = line.split()
    try:
        date_time = split_line[0] + " " + split_line[1]
        log_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f')
    except (ValueError, IndexError):
        if args.v:
            print("Ignoring this log line:", line)
        raise WrongLogLine
    log_type = ''.join(split_line[2][1:-1])
    if log_type not in log_types:
        if verb:
            print("Ignoring this log line:", line)
        raise WrongLogLine
    try:
        log_body = line.split('{')[1].split('}')[0]
    except IndexError:
        if verb:
            print("Ignoring this log line:", line)
        raise WrongLogLine
    log_fields = log_body.split(',')
    log_dict = {}
    for k, v in [x.split(':') for x in log_fields]:
        log_dict[k.strip()] = v.strip()
    if log_dict['type'] == 'RECONF':
        return log_time, log_dict, True
    return log_time, log_dict, False


def check_convergence_time(t, d, convergence_time, best_path, AS_initial_distance):
    if 'processing' in d and d['processing'] == 'NEW_BEST_PATH':
        convergence_time = t
        best_path = d['actual_best_path']
        path_len = len(set(d['actual_best_path'].split('|')))
        if not AS_initial_distance:
            AS_initial_distance = path_len
    if 'processing' in d and (d['processing'] == 'REMOVED_REPLACED_PATH'
                              or d['processing'] == 'NEW_PATH'):
        if d['actual_best_path'] == 'NONE':
            convergence_time = ''
            best_path = ''
        elif d['actual_best_path'] != best_path:
            best_path = d['actual_best_path']
            convergence_time = t
    return convergence_time, best_path, AS_initial_distance


def parse_file(fname, reconf_time=None):
    data = []
    reconf_time = None
    last_message_before_reconf = None
    convergence_time = ''
    best_path = ''
    AS_initial_distance = 0
    with open(fname, 'r') as f:
        for line in f:
            try:
                t, d, reconf = parse_line(line, args.v)
                if reconf:
                    reconf_time = t
                    last_message_before_reconf = last_one
                last_one = t
            except WrongLogLine:
                continue
            data.append([t, d])
            convergence_time, best_path, AS_initial_distance = \
                    check_convergence_time(t, d, convergence_time, best_path, AS_initial_distance)
    return data, last_message_before_reconf, reconf_time


def parse_folders():
    #extract info from names
    dirNames = []
    fname = path.basename(path.normpath(args.ff))
    try:
        _, net_size, strategy = fname.split('-')
    except ValueError:
        print('ERROR: I expect a folder name of the kind: "RES-12K-30SEC"')
        print('       While it is: {}'.format(fname))
        exit()

    for (dir_path, dir_names, filenames) in walk(args.ff):
        # where run-id starts at 1
        dirNames.extend(dir_names)
        break
    if args.l:
        slice_end = args.l
    else:
        slice_end = len(dirNames)
    for dir in dirNames:
        try:
            _, _ , _, run_data = dir.split('-')
            t_r = int(run_data.split('_')[0][6:])
            run = int(run_data.split('_')[1][3:])
            if run > slice_end:
                continue
        except ValueError:
            print('ERROR: I expect each subfolder name to be like: "RES-12K-30SEC-BROKEN10883_run10"')
            print('       While it is: {}'.format(dir))
            exit()
        fileList = list()
        for (dir_path, dir_names, filenames) in walk(args.ff + "/" + dir):
            fileList.extend(filenames)
            break
        # Note ASes are numbered starting from zero
        broken_AS = "log_h_" + str(t_r-1) + ".log" 

        data, last_message_before_reconf, reconf_time = \
                parse_file(args.ff + "/" + dir + "/" + broken_AS)
        for fname in fileList:
            try:
                AS = int(fname.split('_')[2].split('.')[0])
            except IndexError:
                print('ERROR: I expect each log file name to be like: "log_h_23.log"')
                print('       While it is: {}'.format(fname))
                exit()
            data, last_message_before_tmp, reconf_temp = \
                parse_file(args.ff + "/" + dir + "/" + fname)


         

