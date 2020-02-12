#!/usr/bin/env python3
import argparse
import datetime
import re
from collections import defaultdict, Counter
from os import walk
import numpy as np
import pprint


log_types = ['FATAL', 'RECONF']


class WrongLogLine(Exception):
    pass


class WrongFileName(Exception):
    pass


args = None
resolution = 1

def print_in_columns(data, width=15, separator=','):
    print(separator.join([str(d).ljust(width) for d in data]))


def to_unixtime(t):
    """ note that this does not work if all timestamps are not from the same time zone """
    return int((t - datetime.datetime(1970, 1, 1)).total_seconds()*resolution)


def parse_args():
    global args
    global resolution
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='the log file', required=False, nargs='*')
    parser.add_argument('-ff', help='Folder with log Folders', required=False)
    parser.add_argument('-v', help='be more verbose', default=False,
                        action='store_true')
    parser.add_argument('-c', help='Compute convergence delay', default=False,
                        action='store_true')
    parser.add_argument('-t', help='compute the number of updates generated',
                        default=False, action='store_true')
    parser.add_argument('-T', help='time resolution (s/decimal/cent/milli)',
                        default='SEC',
                        choices=['SECS', 'DSEC', 'CSEC', 'MSEC'])
    parser.add_argument('-d', required=False, default=0, action='store', 
            help="Use this option to see a negative delta")
    parser.add_argument('--tnodes', required=False, default=-1, type=int,
            help="Assume the first X nodes are T nodes")
    parser.add_argument('-l', required=False, default=-1, 
            help="Limit the number of runs to consider, helps speeding up development",
            type=int)
    args = parser.parse_args()

    if not (args.f or args.ff):
        parser.error('No folders provided, you have to choose at one type of folder to pass')
    if args.f and args.ff:
        parser.error('Too much folders provided, you have to choose at ONE type of folder to pass')

    if args.T == 'DSEC':
        resolution = 10
    elif args.T == 'CSEC':
        resolution = 100
    elif args.T == 'MSEC':
        resolution = 1000


def parse_line(line, verb):
    split_line = line.split()
    try:
        date_time = split_line[0] + " " + split_line[1]
        log_time = to_unixtime(datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f'))
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


def parse_file(fname):
    try:
        AS_number = int(fname.split('_')[-1][:-4]) + 1
    except (ValueError, ):
        print('Invalid file name:', fname)
        print('I expect a file name of the form log_h_X.log '
              'where X is an AS number')
        exit()
    data = []
    reconf_time = None
    last_message_before_reconf = None
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
    return AS_number, data, last_message_before_reconf, reconf_time


def compute_convergence_time(data):
    convergence_time = ''
    best_path = ''
    first_log = None
    AS_initial_distance = 0
    AS_final_distance = 0
    for (t, d) in data:
        if not first_log:
            first_log = t
        if 'processing' in d and d['processing'] == 'NEW_BEST_PATH':
            convergence_time = t
            best_path = d['actual_best_path']
            path_len = len(set(d['actual_best_path'].split('|')))
            if not AS_initial_distance:
                AS_initial_distance = path_len
            AS_final_distance = path_len
        if 'processing' in d and (d['processing'] == 'REMOVED_REPLACED_PATH'
                                  or d['processing'] == 'NEW_PATH'):
            if d['actual_best_path'] == 'NONE':
                convergence_time = ''
                best_path = ''
            elif d['actual_best_path'] != best_path:
                best_path = d['actual_best_path']
                convergence_time = t
        if args.v and 'processing' in d:
            print(t, d)
    if convergence_time:
        return convergence_time, first_log, AS_initial_distance, AS_final_distance
    return None, None, 0, 0


def compute_updates_number(data):
    updates = Counter()
    min_secs = data[0][0]
    max_secs = data[-1][0]
    for (t, d) in data:
        if d['type'] == 'UPDATE_TX':
            updates[t] += 1
    return updates, min_secs, max_secs


def main():
    parse_args()
    AS_data = defaultdict(dict)
    reconf_time = None
    last_reconf = None
    last_message_before_reconf = None
    reconf_ASes = list()
    max_key = 0
    key_counter = Counter()
    AS_data_all = defaultdict(dict)
    if args.f and not args.ff:
        for fname in args.f:
            AS_number, data, last_message_before_tmp, reconf_temp = parse_file(fname)
            if reconf_temp:
                reconf_time = reconf_temp
                last_message_before_reconf = last_message_before_tmp
                reconf_ASes.append(AS_number)
            if args.c:
                convergence_time, first_log, AS_initial_distance, AS_final_distance = \
                    compute_convergence_time(data)
                AS_data[AS_number]['convergence_time'] = [convergence_time]
                AS_data[AS_number]['first_log'] = first_log
                AS_data[AS_number]['initial_distance'] = AS_initial_distance
                AS_data[AS_number]['final_distance'] = AS_final_distance
            if args.t:
                updates, min_secs, max_secs = compute_updates_number(data)
                AS_data[AS_number]['updates'] = updates
                AS_data[AS_number]['min_secs'] = min_secs
                AS_data[AS_number]['max_secs'] = max_secs

        for AS_number in AS_data:
            if AS_data[AS_number]['convergence_time']:
                if AS_data[AS_number]['convergence_time'][0] is not None:
                    print(AS_number, AS_data[AS_number]['convergence_time'], reconf_time)
                    if reconf_time:
                        AS_data[AS_number]['convergence_time'][0] -= reconf_time
                    else:
                        AS_data[AS_number]['convergence_time'][0] -= AS_data[AS_number]['first_log']
                else:
                    if AS_number in reconf_ASes:
                        AS_data[AS_number]['convergence_time'] = [0]
                    else:
                        AS_data[AS_number]['convergence_time'] = [1000000]
            else:
                if AS_number in reconf_ASes:
                    AS_data[AS_number]['convergence_time'] = [0]
                else:
                    AS_data[AS_number]['convergence_time'] = [1000000]
            if 'updates' in AS_data[AS_number]:
                new_counter = Counter()
                for key in AS_data[AS_number]['updates']:
                    new_key = key - reconf_time
                    max_key = max(max_key, new_key)
                    key_counter[str(AS_number) + str(new_key)] += 1
                    value = AS_data[AS_number]['updates'][key]
                    new_counter[new_key] = value
                AS_data[AS_number]['updates'] = new_counter
    else:
        dirNames = list()
        for (dir_path, dir_names, filenames) in walk(args.ff):
            dirNames.extend(dir_names)
            break
        if args.l:
            slice_end = args.l
        else:
            slice_end = len(dirNames)
        for dir in dirNames[:slice_end]:
            fileList = list()
            for (dir_path, dir_names, filenames) in walk(args.ff + "/" + dir):
                fileList.extend(filenames)
                break
            if dir not in AS_data_all:
                AS_data_all[dir] = defaultdict(dict)
            for fname in fileList:
                AS_number, data, last_message_before_tmp, reconf_temp = \
                    parse_file(args.ff + "/" + dir + "/" + fname)
                if reconf_temp:
                    reconf_time = reconf_temp
                    last_message_before_reconf = last_message_before_tmp
                    reconf_ASes.append(AS_number)
                if args.c:
                    convergence_time, first_log, AS_initial_distance, AS_final_distance = \
                            compute_convergence_time(data)
                    AS_data_all[dir][AS_number]['convergence_time'] = convergence_time
                    AS_data_all[dir][AS_number]['first_log'] = first_log
                    AS_data_all[dir][AS_number]['AS_initial_distance'] = AS_initial_distance
                    AS_data_all[dir][AS_number]['AS_final_distance'] = AS_final_distance
                if args.t:
                    updates, min_secs, max_secs = compute_updates_number(data)
                    AS_data_all[dir][AS_number]['updates'] = updates
                    AS_data_all[dir][AS_number]['min_secs'] = min_secs
                    AS_data_all[dir][AS_number]['max_secs'] = max_secs
            for AS_number in AS_data_all[dir]:
                if AS_data_all[dir][AS_number]['convergence_time']:
                    if reconf_time:
                        AS_data_all[dir][AS_number]['convergence_time'] -= reconf_time
                    else:
                        AS_data_all[dir][AS_number]['convergence_time'] -= AS_data_all[dir][AS_number]['first_log']
                else:
                    if AS_number in reconf_ASes:
                        AS_data_all[dir][AS_number]['convergence_time'] = 0
                    else:
                        AS_data_all[dir][AS_number]['convergence_time'] = 1000000

                if 'convergence_time' not in AS_data[AS_number]:
                    AS_data[AS_number]['convergence_time'] = \
                            [AS_data_all[dir][AS_number]['convergence_time']]
                    AS_data[AS_number]['AS_initial_distance'] = \
                            [AS_data_all[dir][AS_number]['AS_initial_distance']]
                    AS_data[AS_number]['AS_final_distance'] = \
                            [AS_data_all[dir][AS_number]['AS_final_distance']]
                else:
                    AS_data[AS_number]['convergence_time'].append(
                            AS_data_all[dir][AS_number]['convergence_time'])
                    AS_data[AS_number]['AS_initial_distance'].append(
                            AS_data_all[dir][AS_number]['AS_initial_distance'])
                    AS_data[AS_number]['AS_final_distance'].append(
                            AS_data_all[dir][AS_number]['AS_final_distance'])

                if 'updates' in AS_data_all[dir][AS_number]:
                    new_counter = Counter()
                    for key in AS_data_all[dir][AS_number]['updates']:
                        new_key = key - reconf_time
                        # if new_key < 0:
                        #    print("ERROR")
                        max_key = max(max_key, new_key)
                        key_counter[str(AS_number) + str(new_key)] += 1
                        value = AS_data_all[dir][AS_number]['updates'][key]
                        new_counter[new_key] = value
                    AS_data_all[dir][AS_number]['updates'] = new_counter

                if 'updates' not in AS_data[AS_number]:
                    AS_data[AS_number]['updates'] = AS_data_all[dir][AS_number]['updates']
                else:
                    AS_data[AS_number]['updates'] += AS_data_all[dir][AS_number]['updates']


        for AS_number in AS_data:
            for key in AS_data[AS_number]['updates']:
                AS_data[AS_number]['updates'][key] /= float(len(AS_data_all.keys()))

    delta = reconf_time - last_message_before_reconf

    conv_time_by_dist = defaultdict(list)
    updates_by_dist = defaultdict(int)
    tot_runs = 0
    if args.c:
        print_in_columns(['AS', 'convergence_time', 
                          'AS_initial_distance', 'AS_final_distance'])
        T_AS_by_distance = defaultdict(int)
        for AS_number, c_data in sorted(AS_data.items()):
            if not tot_runs:
                tot_runs = len(c_data['convergence_time'])
            for d in c_data['AS_final_distance']:
                if AS_number <= args.tnodes:
                    T_AS_by_distance[d] += 1
                if d:
                    conv_time_by_dist[d].append(max(c_data['convergence_time']))
            print_line = [AS_number, max(c_data['convergence_time']), 
                max(c_data['AS_initial_distance']), max(c_data['AS_final_distance'])]
            print_in_columns(print_line)
        print('\n\n')

        

        print_in_columns(['time', 'converged_ASes', 'non_converged_ASes', 'total_nodes'])
        if int(args.d) > 0:
            i = int(args.d)
            while i > 0:
                print_in_columns(['-' + str(i), str(len(AS_data)), '0', str(len(AS_data))])
                i -= 1
        convergence_time = []
        never_converged_ASes = 0
        non_reconfigured_ASes = 0
        last_reconf = 0
        for AS_number, c_data in sorted(AS_data.items()):
            if 'convergence_time' in c_data:
                for conv_time in c_data['convergence_time']:

                    if conv_time >= 0:
                        convergence_time.append((AS_number, conv_time))
                        if conv_time > last_reconf:
                            last_reconf = min(last_reconf, conv_time)
                    else:
                        non_reconfigured_ASes += 1
            else:
                if AS_number not in reconf_ASes:
                    never_converged_ASes += 1
                else:
                    convergence_time.append((AS_number, 0))
        tot_nodes = len(AS_data)
        max_time = max([x[1] for x in convergence_time]) if max_key == 0 else max_key
        for i in range(max_time + 1):
            conv_ASes = 0
            for (AS, t) in convergence_time:
                if i >= t:
                    conv_ASes += 1
            if len(AS_data_all.keys()) != 0:
                conv_ASes /= float(len(AS_data_all.keys()))
            print_in_columns([i, conv_ASes + non_reconfigured_ASes,
                              tot_nodes - conv_ASes - non_reconfigured_ASes,
                              tot_nodes])
        print('\n\n')

    reconf_time = 0

    if args.t:
        # here seconds are in unix time
        if reconf_time is not None:
            reconf_secs = reconf_time
        else:
            reconf_secs = min([AS_data[x]['min_secs'] for x in AS_data])

        if last_reconf is not None:
            end_secs = max_key if max_key != 0 else last_reconf
        else:
            end_secs = max([AS_data[x]['max_secs'] for x in AS_data])

        integral_on_time = dict()
        if args.ff and not args.f:
            integral_list = list()
            for dir in AS_data_all:
                integral_on_time_dir = dict()
                for i in range(reconf_time, end_secs + 1):
                    if i not in integral_on_time:
                        integral_on_time_dir[i] = 0
                    for as_number in AS_data_all[dir]:
                        integral_on_time_dir[i] += AS_data_all[dir][as_number]['updates'][i]
                for i in range(reconf_time + 1, end_secs + 1):
                    integral_on_time_dir[i] += integral_on_time_dir[i - 1]
                integral_list.append(integral_on_time_dir)
            for i in range(reconf_time, end_secs + 1):
                for integral in integral_list:
                    if i not in integral_on_time:
                        integral_on_time[i] = 0
                    integral_on_time[i] += integral[i]
                integral_on_time[i] = integral_on_time[i]/float(len(integral_list))

        print_in_columns(['time'] + ['sum'] + sorted(AS_data.keys()), width=4)
        if int(args.d) > 0:
            i = int(args.d)
            while i > 0:
                print_in_columns(['-' + str(i)] + ['0'] + ['0' for x in AS_data.keys()], width=4)
                i -= 1
        # just a check that we are not leving any number behind
        control_total = 0
        for i in range(reconf_time, end_secs+1):
            print_list = []
            tot_udp = 0
            for (AS_number, c_data) in sorted(AS_data.items()):
                upd = c_data['updates'].get(i, 0)
                tot_udp += upd
                print_list.append(str(upd))
            print_list.insert(0, tot_udp)
            print_list.insert(0, str(i-reconf_secs))
            print_in_columns(print_list, width=4)
            control_total += tot_udp
        tot_updates = 0
        for (AS_number, c_data) in sorted(AS_data.items()):
            AS_updates = 0
            for k,v in c_data['updates'].items():
                if k >= reconf_time and k < end_secs + 1:
                    tot_updates += v
                    AS_updates += v
            for d in c_data['AS_final_distance']:
                if d:
                    updates_by_dist[d] += AS_updates
        if (tot_updates != control_total):
            print("Error in counting updates")
        print('\n\n')

        print_in_columns(['tim','sum'])
        #for i in range(reconf_time-int(args.d), end_secs+1):
        #   print_in_columns([str(i), str(tot_updates)])
        if int(args.d) > 0:
            i = int(args.d)
            while i > 0:
                print_in_columns(['-' + str(i)] + ['0'], width=4)
                i -= 1
        total_upd = 0
        if args.f and not args.ff:
            for i in range(reconf_time, end_secs+1):
                for (AS_number, c_data) in sorted(AS_data.items()):
                    upd = c_data['updates'][i]
                    total_upd += upd
                print_in_columns([str(i), str(total_upd)], width=4)
        else:
            for i in range(reconf_time, end_secs+1):
                """counter = 0
                delta = 0
                for (AS_number, c_data) in sorted(AS_data.items()):
                    upd = 0
                    print(AS_number, c_data['updates'])
                    if i in c_data['updates']:
                        counter += 1
                        upd = c_data['updates'][i]
                        delta += upd
                    if upd > 0:
                        total_upd += upd/counter"""
                print_in_columns([str(i), str(integral_on_time[i])], width=4)

    updates_CDF = 0
    if args.c and args.t:
        print('\n\n')               
        ASes = len(AS_data.items())
        dist_list = sorted(conv_time_by_dist.keys())
        for d in dist_list:
            if d not in T_AS_by_distance:
                T_AS_by_distance[d] = 0
            
        print_in_columns(['distance', 'avg_conv_time', 'frac_of_ASes', 
                          'T_ASes', 'avg_num_of_updates', 'updates CDF'])
        for k in dist_list:
            number_of_ASes = round(len(conv_time_by_dist[k])/tot_runs, 2) 
            if not number_of_ASes:
                print_in_columns([k, 0, 0, 0, 0])
                break
            avg_conv_time = round(sum(conv_time_by_dist[k])/len(conv_time_by_dist[k]), 3)
            T_ASes = round(T_AS_by_distance[k]/tot_runs, 2)
            if not T_ASes:
                T_ASes = ""
            else:
                T_ASes = 0
            avg_updates = round(updates_by_dist[k]/(tot_runs * number_of_ASes), 5)
            updates_CDF += round(updates_by_dist[k]/(tot_runs), 2)
            print_in_columns([k, avg_conv_time, round(number_of_ASes/ASes, 3), T_ASes, 
                round(avg_updates,2), updates_CDF])
        print('\n\n')               
main()
