#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================
import pandas as pd
import numpy as np
import argparse
import datetime
from os import walk, path, listdir
import re
import matplotlib.pyplot as plt

log_types = ['FATAL', 'RECONF']
samples = 25
delta = '100ms'
index_names=['t_r', 'run_id', 'AS', 'strategy']
column_names=['distance_AS_from_tr', 'distance_tr_to_t', 'distance_AS_after_t', 
              'distance_AS_before_t', 'first_up_time', 'conv_time', 'last_up_time', 
              'avg_update_per_sec', 'max_update_per_sec', 'tot_updates']



class WrongLogLine(Exception):
    pass


class WrongFileName(Exception):
    pass


class WrongFolderStructure(Exception):
    pass


def check_data(update_table, run_table):
    max_time = max(update_table.index)
    for c in run_table:
        if "time" not in c:
            if (run_table[c] < 0).all():
                print('There are some negative values in the {} column'.format(c))
        else:
            if (run_table[c] < pd.Timedelta(0)).all():
                print('There are some negative values in the {} column'.format(c))
            if (run_table[c] > max_time).all():
                print('There are some convergence time beyond maximum time in the {} column'.format(c))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', help='Save graphs to pdf file', required=False, 
                        default='')
    parser.add_argument('-p', help='Save binary parsed file to "pickle" format', 
                        required=False)
    parser.add_argument('-P', help='Load binary pickle files (two files expected)' 
                        ' first for run_table, second for update_table',
                        required=False, nargs=2)
    parser.add_argument('-G', help='The graphml file (unused, TBD)', required=False)
    parser.add_argument('-ff', help='Folder with log Folders', required=False)
    parser.add_argument('-v', help='be more verbose', default=False,
                        action='store_true')
    parser.add_argument('-T', help='time resolution (s/decimal/cent/milli)',
                        default='100ms',
                        choices=['1s', '100ms', '10ms', '1ms'])
    parser.add_argument('--tnodes', required=False, default=-1, type=int,
            help="Assume the first X nodes are T nodes")
    parser.add_argument('-l', required=False,
            help="Limit the number of runs to consider, helps speeding up development",
            type=int, default=0)
    args = parser.parse_args()

    if not (args.ff or args.P):
        parser.error('No folders provided, you have to choose'
                'at one folder of one pickle file')

    global delta
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

def parse_file(fname, reconf_time=None, T_ASes=[], verb=False, delta='100ms'):
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
    update_series = pd.Series([1]*len(update_received), index=update_received)
    dup = update_series.index
    reindex = [x for x in update_series.index]
    while dup.duplicated().any():
        for idx, check in enumerate(dup):
            if check:
                reindex[idx] = reindex[idx] +\
                        pd.Timedelta('0.001ms')*np.random.randint(1,99)
        dup = pd.Index(reindex)

    update_series = pd.Series([1]*len(dup), index=dup).sort_index()
    avg_update_per_sec = 0
    max_update_per_sec = 0
    if len(dup) > 1:
        a = (dup.max() - dup.min()).total_seconds()
        avg_update_per_sec = len(dup)/a
        rolling = update_series.rolling(delta).count()
        avg_update_per_sec = rolling.mean()
        max_update_per_sec = rolling.max() 

    AS_data = [
    ('distance_AS_from_tr', AS_t_r_distance),
    ('distance_AS_after_t', hops_after_t ),
    ('distance_AS_before_t', hops_before_t ),
    ('first_up_time', None), #FIXME 
    ('conv_time', conv_time),
    ('last_up_time', None), # FIXME
    ('avg_update_per_sec', avg_update_per_sec),
    ('max_update_per_sec', max_update_per_sec),
    ('tot_updates', tot_updates)]
    return  AS_data, reconf_time, dup


def identify_folder_structure(args):
    
    MRAI = False
    DPC = False
    PARTIAL = False
    fname = path.basename(path.normpath(args.ff))
    try:
        preamble, net_size, strategy = fname.split('-')
        if preamble != 'RES':
            raise WrongFolderStructure
        MRAI = True

    except (ValueError, WrongFolderStructure):
        pass

    try: 
        if fname[:7] != 'RESULTS':
            raise WrongFolderStructure
        DPC = True
    except WrongFolderStructure:
        pass

    try: 
        preamble, net_size, _, perc = fname.split('-')
        PARTIAL = True
    except ValueError:
        pass

    return MRAI, DPC, PARTIAL

def parse_folders(args, T_ASes, gen_updates=False):
    MRAI, DPC, PARTIAL = identify_folder_structure(args)
    if MRAI:
        return parse_folders_MRAI(args, T_ASes, gen_updates)
    elif DPC:
        return parse_folders_one_level(args, T_ASes, gen_updates, action='DPC')
    elif PARTIAL:
        return parse_folders_MRAI(args, T_ASes, gen_updates, action='PARTIAL')
    else:
        fname = path.basename(path.normpath(args.ff))
        print('ERROR: I expect a folder name of the kind: "RES-12K-30SEC" for MRAI simulations')
        print('       or a folder name of the kind "RES-1K-30SEC-0.1" for' 
              'MRAI simulations with partial deployment')
        print('       or a folder named "RESULTS" for DPC simulations')
        print('       While it is: {}'.format(fname))
        exit()


def parse_folders_MRAI(args, T_ASes, gen_updates=False, action='MRAI'):
    #extract info from names
    dirNames = []
    AS_index_all = []
    AS_data_all = []
    update_event = []
    fname = path.basename(path.normpath(args.ff))
    if action == 'MRAI':
        _, net_size, strategy = fname.split('-')
    elif action == 'PARTIAL':
        _, net_size, _, strategy = fname.split('-')

    for (dir_path, dir_names, filenames) in walk(args.ff):
        # where run-id starts at 1
        dirNames.extend(dir_names)
        break
    if args.l:
        slice_end = args.l
    else:
        slice_end = len(dirNames)
    dir_n = len(dirNames)
    count = 1
    print_step = list(range(10,100,10))
    for dir in dirNames:
        if args.v:
            if int(100*count/dir_n) in print_step:
                print("Parsed {}% of the folders".format(int(100*count/dir_n)))
                del print_step[0]
        count+=1
            
        
        idx, data, update = parse_folder(dir, args.ff, slice_end, T_ASes, 
                                         strategy, gen_updates, delta=args.T)
        AS_index_all.extend(idx)
        AS_data_all.extend(data)
        update_event.extend(update)
    run_index = pd.MultiIndex.from_tuples(AS_index_all, names=index_names)
    update_table = pd.DataFrame()
    if gen_updates:
        if args.v:
            print('Done with reading files, now resampling')
        max_time = max(update_index)
        min_time = min(update_index)
        u_series = []
        count = 0
        up_len = len(update_event)
        print_step = list(range(10,100,10))
        for update_list in update_event:
            if args.v:
                if int(100*count/up_len) in print_step:
                    print("Resampled {}% of the series".format(int(100*count/up_len)))
                    del print_step[0]
            count += 1
            tmp = pd.Series([1]*len(update_list), index=update_list)
            if min_time not in update_list:
                tmp.loc[min_time] = 0
            if max_time not in update_list:
                tmp.loc[max_time] = 0
            tmp = tmp.resample(delta, label='right').sum()
            u_series.append(tmp.values)
        all_index = tmp.index # they are all the same, pick the last one
        if args.v:
            print('Done resampling, now creating DataFrame')
        

         
        # What follows it slow but I cant find a better way:
        #  - either we first resample (as I do now) and then I can create a DataFrame,
        #    then resampling is slow or,
        #  - I concat each dataframe (which is slow because it reorders the index) 
        #    and after that I resample the dataframe all together 
        # Both seems slow solutions
        update_table = pd.DataFrame(np.stack(u_series).transpose(), index=all_index, 
                                 columns=run_index)
        if args.v:
            print("Done creating DataFrame")
    return action, [pd.DataFrame(AS_data_all, index=run_index, 
                                 columns=column_names), 
                    update_table]


def parse_folders_one_level(args, T_ASes, gen_updates=False, action='DPC'):
    #extract info from names
    dirNames = []
    AS_index_all = []
    AS_data_all = []
    update_event = []

    file_dict = {}
    folders = listdir(args.ff)
    if args.l:
        slice_end = args.l
    else:
        slice_end = len(folders)
    ASes = set()
    for folder in folders:
        # one folder per run
        fname = path.basename(path.normpath(folder))
        try:
            run_id = int(fname[3:])
            if run_id > slice_end:
                continue
            file_dict[run_id] = []
            if action == 'DPC':
                suffix = '/tgz'
            else:
                suffix = ''

            for (dir_path, dir_names, filenames) in walk(args.ff + '/' + folder + suffix):
                # where run-id starts at 1
                if filenames:
                    for f in filenames:
                        if f.endswith('.log'):
                            file_dict[run_id].append(dir_path + '/' + f) 
                            AS = int(f.split('.')[0].split('_')[2])
                            ASes.add(AS)
        except ValueError:
            print('ERROR: I expect each subfolder name to be like: runXX'
                  + suffix + '/nodeYY-logs')
            print('       While it is: {}'.format(fname))
            exit()
    dpc_values = pd.DataFrame(columns=ASes, index=pd.MultiIndex(levels = [[]]*3, 
                                                  labels = [[]]*3,
                                                  names=['perc', 'run', 'metric']))

    if action == 'DPC':
        return parse_sub_folders_DPC(dpc_values, file_dict, args, len(ASes))

def parse_sub_folders_DPC(dpc_values, file_dict, args, AS_num): 
    fracs = list(range(0,101,10))
    for k,l in file_dict.items():
        if args.v:
            print("Parsing run {}".format(k))
        file_n = len(l)
        count = 1
        print_step = list(range(10,100,10))
        M_list = []
        L_list = []
        AS_list = []
        for f in l:
            if int(100*count/file_n) in print_step:
                print("Parsed {}% of the files".format(int(100*count/file_n)))
                del print_step[0]
            count+=1
            AS, M, L = parse_file_DPC(f, verb=args.v)
            AS_list.append(AS)
            M_list.append(M)
            L_list.append(L)
        DPC_frac = 100*len(AS_list)/AS_num
        idx = min(fracs, key=lambda x:abs(x-DPC_frac))
        dpc_values.loc[(idx, k, 'M'), AS_list] = M_list 
    return 'DPC', [dpc_values]
   

def parse_file_DPC(fname, verb=False):
    file_name = path.basename(path.normpath(fname))
    AS = int(file_name.split('.')[0].split('_')[2])
    pattern = '\|?\(K:'+str(AS)+'.*?\)\|?'
    regex = re.compile(pattern)
    metric_M = 0
    metric_L = 0
    for line in reversed(list(open(fname))):
        cent_values = regex.search(line)
        if cent_values:
            couples = cent_values.group().strip('|()').split(',')
            _, K = couples[0].split(':')
            _, L = couples[1].split(':')
            _, M = couples[2].split(':')
            metric_M = float(M)
            metric_L = float(L)
            break
    return AS, metric_M, metric_L


def parse_folder(dir, f_path, slice_end, T_ASes, strategy, verb=False,
        gen_updates=False, delta='100ms'):
    AS_index_all = []
    AS_data_all = []
    update_event = []
    # AS number goes from 1 up, 
    # Node IDs in the graph go from 0 up, logfiles are named after ID
    # DataFrame are organized to use only AS numbers

    try:
        _, _ , _, run_data = dir.split('-')
        t_r = int(run_data.split('_')[0][6:])
        run_id = int(run_data.split('_')[1][3:])
        if run_id > slice_end:
            return [], [], []
    except ValueError:
        try: 
            _, _ , _, perc, run_data = dir.split('-')
            t_r = int(run_data.split('_')[0][6:])
            run_id = int(run_data.split('_')[1][3:])
            if run_id > slice_end:
                return [], [], []
        except ValueError:
            print('ERROR: I expect each subfolder name to be like:' 
                  '"RES-12K-30SEC-BROKEN10883_run10" for MRAI runs')
            print('       Or, "RES-12K-30SEC-0.1-BROKEN10883_run10" '
                  'for Partial deployment MRAI runs')
            print('       While it is: {}'.format(dir))
            exit()
    fileList = list()
    for (dir_path, dir_names, filenames) in walk(f_path + "/" + dir):
        fileList.extend(filenames)
        break
    broken_AS_file = "log_h_" + str(t_r-1) + ".log" 
    tr_data, reconf_time, update_received = \
            parse_file(f_path + "/" + dir + "/" + broken_AS_file, reconf_time='', 
                    T_ASes=T_ASes, verb=verb, delta=delta)
    tr_data.append(('distance_tr_to_t', 0)) # FIXME
    AS_index = [t_r, run_id, t_r, strategy] 
    AS_index_all.append(AS_index)
    AS_data_all.append(dict(tr_data))
    update_event.append(update_received)
    for fname in sorted(fileList):
        if fname == broken_AS_file:
            continue
        try:
            AS = int(fname.split('_')[2].split('.')[0]) + 1
        except IndexError:
            print('ERROR: I expect each log file name to be like: "log_h_23.log"')
            print('       While it is: {}'.format(fname))
            exit()
        data, _, update_received = \
            parse_file(f_path + "/" + dir + "/" + fname, 
                       reconf_time=reconf_time, T_ASes=T_ASes, verb=verb, 
                       delta=delta)
        AS_index_all.append([t_r, run_id, AS, strategy])
        AS_data_all.append(dict(data + [('distance_tr_to_t', 0)])) # FIXME
        if gen_updates:
            update_event.append(update_received)
    return AS_index_all, AS_data_all, update_event
