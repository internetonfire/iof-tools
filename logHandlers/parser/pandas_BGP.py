#!/usr/bin/env python3
import pandas as pd
import numpy as np
from helper_functions import *


samples = 10
delta = '10ms'
index_names=['t_r', 'run_id', 'AS']
   
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
            mode='INCREASING_L', time_len=samples)
    #            
    run_table_index = pd.MultiIndex.from_product(indexes, names=index_names)
    run_table = pd.DataFrame(data_set, index=run_table_index, columns = ['tot_updates'])
    #
    update_table_index = pd.timedelta_range(0, periods=samples, freq=delta)
    #
    update_table = pd.DataFrame(time_data, index=update_table_index, columns=run_table_index)
    print(run_table)



    
    # just to recall how to slice on inner layers
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))])
    # then slice the time serie
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))]['00:00:00.770000':'00:00:00.870000'])
    
    
    # two tables on with run values (long list. each line with index: T_r, run_id), one dataframe qith X: time intervale from date_range(), Y: Run-id. For each row the updates received in the time interval. 
    # dopo faccio join su tr e run id, controlla che si possa fare join su una chiave con due campi
