#!/usr/bin/env python3
import argparse
import datetime
import re
from collections import defaultdict, Counter


log_types = ['FATAL', 'RECONF']


class WrongLogLine(Exception):
    pass


class WrongFileName(Exception):
    pass


args = None


def print_in_columns(data, width=15, separator=','):
    print(separator.join([str(d).ljust(width) for d in data]))


def to_unixtime(t):
    """ note that this does not work if all timestamps are not from the same time zone """
    return int((t - datetime.datetime(1970, 1, 1)).total_seconds())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='the log file', required=True, nargs='*')
    parser.add_argument('-v', help='be more verbose', default=False,
                        action='store_true')
    parser.add_argument('-c', help='Compute convergence delay', default=False,
                        action='store_true')
    parser.add_argument('-t', help='compute the number of updates generated',
                        default=False, action='store_true')
    global args
    args = parser.parse_args()


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
        AS_number = int(fname.split('_')[2][:-4]) + 1
    except (ValueError, ):
        print('Invalid file name:', fname)
        print('I expect a file name of the form log_h_X.log '
              'where X is an AS number')
        exit()
    data = []
    reconf_time = None
    with open(fname, 'r') as f:
        for line in f:
            try:
                t, d, reconf = parse_line(line, args.v)
                if reconf:
                    reconf_time = t
            except WrongLogLine:
                continue
            data.append([t, d])
    return AS_number, data, reconf_time


def compute_convergence_time(data):
    convergence_time = ''
    best_path = ''
    first_log = None
    for (t, d) in data:
        if not first_log:
            first_log = t
        if 'processing' in d and d['processing'] == 'NEW_BEST_PATH':
            convergence_time = t
            best_path = d['actual_best_path']
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
        return convergence_time, first_log
    return None, None


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
    for fname in args.f:
        AS_number, data, reconf_temp = parse_file(fname)
        if reconf_temp:
            reconf_time = reconf_temp
        if args.c:
            convergence_time, first_log = compute_convergence_time(data)
            AS_data[AS_number]['convergence_time'] = convergence_time
            AS_data[AS_number]['first_log'] = first_log
        if args.t:
            updates, min_secs, max_secs = compute_updates_number(data)
            AS_data[AS_number]['updates'] = updates
            AS_data[AS_number]['min_secs'] = min_secs
            AS_data[AS_number]['max_secs'] = max_secs

    if args.c:
        print_in_columns(['AS', 'convergence_time'])
        for AS_number, c_data in sorted(AS_data.items()):
            if c_data['convergence_time']:
                print_line = []
                if reconf_time:
                    print_line = [AS_number, (c_data['convergence_time'] -
                                  reconf_time)]
                else:
                    print_line = [AS_number, (c_data['convergence_time'] -
                                  c_data['first_log'])]
                    # there can be negative value for convergence, that
                    # happen when a node is not affected by the change
                    # (it converged before the RECONF)
            else:
                print_line = [AS_number, 1000000]  # a big number to show that
                                                   # it did not converge
            print_in_columns(print_line)
        print('\n\n')

        print_in_columns(['time', 'converged_ASes', 'non_converged_ASes', 'total_nodes'])
        convergence_time = []
        never_converged_ASes = 0
        non_reconfigured_ASes = 0
        last_reconf = 0
        for AS_number, c_data in sorted(AS_data.items()):
            if c_data['convergence_time']:
                if reconf_time:
                    # convergence_time is a relative time
                    conv_time = (c_data['convergence_time'] - reconf_time)
                else:
                    conv_time = (c_data['convergence_time'] - c_data['first_log'])
                if conv_time >= 0:
                    convergence_time.append((AS_number, conv_time))
                    if c_data['convergence_time'] > last_reconf:
                        last_reconf = c_data['convergence_time']
                else:
                    non_reconfigured_ASes += 1
            else:
                never_converged_ASes += 1
        tot_nodes = len(AS_data)
        max_time = max([x[1] for x in convergence_time])
        for i in range(max_time + 1):
            conv_ASes = 0
            for (AS, t) in convergence_time:
                if i >= t:
                    conv_ASes += 1
            print_in_columns([i, conv_ASes + non_reconfigured_ASes,
                              tot_nodes - conv_ASes - non_reconfigured_ASes,
                              tot_nodes])
        print('\n\n')


    if args.t:
        # here seconds are in unix time
        if reconf_time:
            reconf_secs = reconf_time
        else:
            reconf_secs = min([AS_data[x]['min_secs'] for x in AS_data])

        if last_reconf:
            end_secs = last_reconf
        else:
            end_secs = max([AS_data[x]['max_secs'] for x in AS_data])

        print_in_columns(['time'] + ['sum'] + sorted(AS_data.keys()), width=4)
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
            for k,v in c_data['updates'].items():
                if k >= reconf_time and k < last_reconf + 1:
                    tot_updates += v
        if (tot_updates != control_total):
            print("Error in counting updates")

main()
