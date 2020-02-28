import itertools as it
import pandas as pd
import numpy as np
import argparse
import datetime
from os import walk, path
from pandas_BGP import delta, index_names, column_names

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
    parser = argparse.ArgumentParser()
    #parser.add_argument('-f', help='the log file', required=False, nargs='*')
    parser.add_argument('-G', help='The graphml file (unused, TBD)', required=False)
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
    return args



def parse_line(line, verb=False):
    split_line = line.split()
    try:
        date_time = split_line[0] + " " + split_line[1]
        log_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f')
    except (ValueError, IndexError):
        if verb:
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


def check_convergence_time(t, d, convergence_time, best_path, AS_t_r_distance):
    if 'processing' in d and d['processing'] == 'NEW_BEST_PATH':
        convergence_time = t
        best_path = d['actual_best_path']
        path_len = len(set(d['actual_best_path'].split('|')))
        if not AS_t_r_distance:
            AS_t_r_distance = path_len
    if 'processing' in d and (d['processing'] == 'REMOVED_REPLACED_PATH'
                              or d['processing'] == 'NEW_PATH'):
        if d['actual_best_path'] == 'NONE':
            convergence_time = ''
            best_path = ''
        elif d['actual_best_path'] != best_path:
            best_path = d['actual_best_path']
            convergence_time = t
    return convergence_time, best_path, AS_t_r_distance

def path_analysis(best_path, T_ASes):
    best_path_unique = []
    hops_before_t = 0
    hops_after_t = 0
    for AS in reversed(best_path.split('|')): 
        # remove duplicates and maintain order
        if not AS:
            continue
        if AS not in best_path_unique:
            best_path_unique.append(AS)
            if int(AS) in T_ASes or hops_after_t:
                hops_after_t += 1
            if not hops_after_t:
                hops_before_t += 1
    path_len = len(best_path_unique) # path does not include node itself
    if not path_len == hops_before_t + hops_after_t:
        raise Exception("Problems in countin path lenght!")
    return path_len, hops_before_t, hops_after_t

def parse_file(fname, reconf_time=None, T_ASes=[], verb=False):
    tot_updates = 0
    last_message_before_reconf = None
    convergence_time = ''
    best_path = ''
    AS_t_r_distance = 0
    update_received = []
    with open(fname, 'r') as f:
        for line in f:
            try:
                t, d, reconf = parse_line(line, verb)
                if reconf:
                    reconf_time = t
                    last_message_before_reconf = last_one
                last_one = t
            except WrongLogLine:
                continue
            convergence_time, best_path, AS_t_r_distance = \
                    check_convergence_time(t, d, convergence_time, best_path, AS_t_r_distance)
            if d['type'] == 'UPDATE_RX':
                tot_updates += 1
                update_received.append(t)
    
    path_len, hops_before_t, hops_after_t = path_analysis(best_path, T_ASes)
    if convergence_time:
        conv_time = convergence_time - reconf_time
    else:
        conv_time = pd.Timedelta(0)
    # [:] writes the data in the same memory of the original structure, 
    # does not reallocate
    update_received[:] = map(lambda x: x-reconf_time, update_received)
    zero_time = pd.Timedelta(0)
    update_received[:] = filter(lambda x: x >= zero_time, update_received)
    AS_data = [
    ('distance_AS_from_tr', AS_t_r_distance),
    ('distance_AS_after_t', hops_after_t ),
    ('distance_AS_before_t', hops_before_t ),
    ('first_up_time', None), #FIXME 
    ('conv_time', conv_time),
    ('last_up_time', None), # FIXME
    ('tot_updates', tot_updates)]
    update_series = pd.Series([1]*len(update_received), index=update_received)
    dup = update_series.index.duplicated()
    reindex = [x for x in update_series.index]
    while dup.any():
        for idx, check in enumerate(dup):
            if check:
                reindex[idx] = reindex[idx] +\
                        pd.Timedelta('0.001ms')*np.random.randint(1,99)
        dup = pd.Index(reindex).duplicated()

    return  AS_data, reconf_time, reindex


def parse_folders(args, T_ASes):
    #extract info from names
    dirNames = []
    AS_index_all = []
    AS_data_all = []
    update_event = []
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
            run_id = int(run_data.split('_')[1][3:])
            if run_id > slice_end:
                continue
        except ValueError:
            print('ERROR: I expect each subfolder name to be like: "RES-12K-30SEC-BROKEN10883_run10"')
            print('       While it is: {}'.format(dir))
            exit()
        fileList = list()
        for (dir_path, dir_names, filenames) in walk(args.ff + "/" + dir):
            fileList.extend(filenames)
            break
        # Note file are numbered starting from zero
        broken_AS = "log_h_" + str(t_r-1) + ".log" 

        tr_data, reconf_time, update_received = \
                parse_file(args.ff + "/" + dir + "/" + broken_AS, reconf_time='', 
                        T_ASes=T_ASes)
        tr_data.append(('distance_tr_to_t', 0)) # FIXME
        AS_index = [t_r, run_id, t_r, strategy] 
        AS_index_all.append(AS_index)
        AS_data_all.append(dict(tr_data))
        update_event.append(update_received)
        for fname in fileList[:slice_end*100]:
            if fname == broken_AS:
                continue
            try:
                AS = int(fname.split('_')[2].split('.')[0])
            except IndexError:
                print('ERROR: I expect each log file name to be like: "log_h_23.log"')
                print('       While it is: {}'.format(fname))
                exit()
            data, _, update_received = \
                parse_file(args.ff + "/" + dir + "/" + fname, 
                           reconf_time=reconf_time, T_ASes=T_ASes)
            AS_index_all.append([t_r, run_id, AS, strategy])
            AS_data_all.append(dict(data + [('distance_tr_to_t', 0)])) # FIXME
            update_event.append(update_received)
    run_index = pd.MultiIndex.from_tuples(AS_index_all, names=index_names)
    update_index = pd.Index(it.chain.from_iterable(update_event))
    max_time = max(update_index)
    min_time = min(update_index)
    start = {min_time:0}
    end = {max_time:0}
    update_table = pd.DataFrame([])#, index=update_index)
    u_series = []
    for update_list in update_event:
        tmp = pd.Series([1]*len(update_list), index=update_list)
        tmp = tmp.append(pd.Series(start))
        tmp = tmp.append(pd.Series(end))
        tmp = tmp.resample(delta, label='right').sum()
        u_series.append(tmp)
    update_table = pd.concat(u_series, axis='columns', keys=run_index)
    return pd.DataFrame(AS_data_all, index=run_index, columns=column_names), update_table




         

