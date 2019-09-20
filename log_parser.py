#!/usr/bin/env python3
import argparse
import datetime
import re
from collections import defaultdict


log_types = ['FATAL', 'RECONF']


class WrongLogLine(Exception):
    pass


class WrongFileName(Exception):
    pass


args = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='the log file', required=True, nargs='*')
    parser.add_argument('-v', help='be more verbose', default=False,
                        action='store_true')
    parser.add_argument('-c', help='Compute convergence delay', default=False,
                        action='store_true')
    global args
    args = parser.parse_args()


def parse_line(line, verb):
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
    if log_type == 'RECONF':
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
        if 'processing' in d and d['processing'] == 'REMOVED_REPLACED_PATH':
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


def print_in_columns(data, width=15, separator=','):
    print(separator.join([str(d).ljust(width) for d in data]))


def main():
    parse_args()
    AS_data = defaultdict(dict)
    reconf_time = None
    for fname in args.f:
        AS_number, data, reconf_time = parse_file(fname)
        if args.c:
            convergence_time, first_log = compute_convergence_time(data)
            AS_data[AS_number]['convergence_time'] = convergence_time
            AS_data[AS_number]['first_log'] = first_log

    if args.c:
        print_in_columns(['AS', 'convergence_time'])
        for AS_number, c_data in sorted(AS_data.items()):
            if c_data['convergence_time']:
                print_line = []
                if reconf_time:
                    print_line = [AS_number, c_data['convergence_time'] -
                                  reconf_time]
                else:
                    print_line = [AS_number, c_data['convergence_time'] -
                                  c_data['first_log']]
            else:
                print_line = [AS_number, -1]
            print_in_columns(print_line)


main()
