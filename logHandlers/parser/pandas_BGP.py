#!/usr/bin/env python3
import pandas as pd
import numpy as np
from helper_functions import *


samples = 25
delta = '100ms'
index_names=['t_r', 'run_id', 'AS']
column_names=['distance_AS_from_tr', 'distance_tr_to_t', 'distance_AS_after_t', 
              'first_up_time', 'conv_time', 'last_up_time', 'tot_updates']

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
    indexes = make_index()
    data_set, time_data = fill_run_table(index_names, indexes[0], indexes[1], indexes[2], 
            mode='INCREASING_L', samples=samples)
    #            
    run_table_index = pd.MultiIndex.from_product(indexes, names=index_names)
    run_table = pd.DataFrame(data_set, index=run_table_index, columns=column_names)
    #
    update_table_index = pd.timedelta_range(0, periods=samples, freq=delta)
    #
    update_table = pd.DataFrame(time_data, index=update_table_index, columns=run_table_index)
    check_data(update_table, run_table)
    #print(run_table)
    x = conv_time(run_table, update_table_index)
    print(x)
    #print(x.reindex(index=update_table_index, method='pad'))
    #print(conv_time(run_table[run_table['distance_AS_from_tr'] < 6], update_table_index))
    print(conv_time_per_distance(run_table, update_table_index))



    
    # just to recall how to slice on inner layers
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))])
    # then slice the time serie
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))]['00:00:00.770000':'00:00:00.870000'])
    
    
    # two tables on with run values (long list. each line with index: T_r, run_id), one dataframe qith X: time intervale from date_range(), Y: Run-id. For each row the updates received in the time interval. 
    # dopo faccio join su tr e run id, controlla che si possa fare join su una chiave con due campi
