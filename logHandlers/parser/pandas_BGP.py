#!/usr/bin/env python3
import pandas as pd
import numpy as np
import helper_functions as hf
import matplotlib.pyplot as plt


samples = 25
delta = '100ms'
index_names=['t_r', 'run_id', 'AS', 'strategy']
column_names=['distance_AS_from_tr', 'distance_tr_to_t', 'distance_AS_after_t', 
              'distance_AS_before_t', 'first_up_time', 'conv_time', 'last_up_time', 
              'tot_updates']

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

    
def conv_time(run_table, update_table_index):
    conv_times = run_table['conv_time']
    start = {pd.Timedelta('00:00:00.000000'):0}
    #FIXME label is ignored, thus must be a bug in pandas
    conv_series = pd.Series([1]*len(conv_times), index=conv_times).append(
                            pd.Series(start)).resample(delta, label='right').sum().cumsum()
    return conv_series.reindex(index=update_table_index, method='pad')

def conv_time_per_distance(run_table, update_table_index, column='distance_AS_from_tr'):
    distances = run_table[column].unique()
    conv_list = {}
    for d in distances:
        x  = conv_time(run_table[run_table['distance_AS_from_tr'] == d], 
                                           update_table_index).values
        conv_list[d] = x
    convergence_table = pd.DataFrame(conv_list, index=update_table_index, columns=distances)
    return convergence_table.reindex(sorted(convergence_table.columns), axis='columns')

def _compute_average(update_table, query=(slice(None), slice(None), slice(None)),
        time_start='00:00:00.000000', time_end='99:99:99.999999'):
    return update_table.loc[:, query].mean()

def avg_update_per_t_r(update_table):
    return _compute_average(update_table).mean(level=0)

def avg_update_per_t_r_per_AS(update_table):
    return _compute_average(update_table).groupby(['t_r','AS']).mean()

def avg_update(update_table):
    return _compute_average(update_table).mean()

def update_per_sec(update_table):
    return update_table.sum(axis=1)

def update_per_t_r_per_sec(update_table):
    return update_table.groupby(level=[0], axis='columns').sum()

def update_per_t_r_per_AS_per_sec(update_table):
    return update_table.groupby(level=[0,2], axis='columns').sum()



if __name__ == '__main__':
    indexes = hf.make_index()
    data_set, time_data = hf.fill_run_table(index_names, indexes[0], indexes[1], indexes[2],
            indexes[3], mode='INCREASING_L', samples=samples)
    run_table_index = pd.MultiIndex.from_product(indexes, names=index_names)
    run_table = pd.DataFrame(data_set, index=run_table_index, columns=column_names)
    update_table_index = pd.timedelta_range(0, periods=samples, freq=delta)
    update_table = pd.DataFrame(time_data, index=update_table_index, columns=run_table_index)
    args = hf.parse_args()
    check_data(update_table, run_table)
    T_ASes = set()
    if args.G:
        pass # TODO implement graph parsing here
    else:
        T_ASes = set(range(args.tnodes))

    if args.P:
        run_table = pd.read_pickle(args.P[0])
        update_table = pd.read_pickle(args.P[1])
    elif args.ff:
        run_table, update_table = hf.parse_folders(args, T_ASes)
    if args.p:
        run_table.to_pickle(args.p + "-runs.pickle")
        update_table.to_pickle(args.p + "-update.pickle")
    #print(update_table.sum())
    ct = conv_time_per_distance(run_table, update_table.index)
    pl = ct.plot(title="Convergence time by distance from T_r")
    pl.set_xlabel('time')
    pl.set_ylabel('# of ASes')
    ct = conv_time_per_distance(run_table, update_table.index, column='distance_AS_after_t')
    pl = ct.plot(title="Convergence time by hops after T nodes")
    pl.set_xlabel('time')
    pl.set_ylabel('# of ASes')
    ct = conv_time_per_distance(run_table, update_table.index, column='distance_AS_before_t')
    pl = ct.plot(title="Convergence time by hops before T nodes")
    pl.set_xlabel('time')
    #plt.show()
    #print(run_table)
    #print(update_table)
    



    
    # just to recall how to slice on inner layers
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))])
    # then slice the time serie
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))]['00:00:00.770000':'00:00:00.870000'])
