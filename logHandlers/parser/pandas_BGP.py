#!/usr/bin/env python3
import pandas as pd
import numpy as np
import itertools as it


samples = 100
delta = '10ms'

def make_index(t_r_number=3, run_id_number=3, AS_number=5):
    AS_list = ['AS' + str(x) for x in range(AS_number)]
    t_r_list = AS_list[:t_r_number]
    run_id_list = list(range(run_id_number))
    return([t_r_list, run_id_list, AS_list])

def fill_run_table(names, t_r_list, run_id_list, AS_list, mode='ZERO', time_len=0):
    """ creates a list of dictionaries to fill a multiindex dataframe with
        dummy data """
    data = []
    time_data = []
    for idx, val in enumerate(it.product(t_r_list, run_id_list, AS_list)):
        tot_updates = idx
        updates = [0] * time_len
        if mode == 'RANDOM':
            tot_updates = np.random.random()
            updates = np.random.randn(time_len) + idx
        if mode == 'LINEAR':
            tot_updates = idx
            updates = [idx] * time_len
        data_dict = {}
        for i in range(len(names)): 
            data_dict[names[i]] = str(val[i])
        data_dict['tot_updates'] =  str(tot_updates)
        data.append(data_dict)
        time_data.append(updates)
    return data, np.matrix.transpose(np.array(time_data))
    
def fill_updates_table(names):
    pass


names=['t_r', 'run_id', 'AS']
indexes = make_index()
data_set, time_data = fill_run_table(names, indexes[0], indexes[1], indexes[2], 
        mode='LINEAR', time_len=samples)
            
run_table_index = pd.MultiIndex.from_product(indexes, names=names)
run_table = pd.DataFrame(data_set, index=run_table_index, columns = ['tot_updates'])

update_table_index = pd.timedelta_range(0, periods=samples, freq=delta)

update_table = pd.DataFrame(time_data, index=update_table_index, columns=run_table_index)
print(update_table)




# two tables on with run values (long list. each line with index: T_r, run_id), one dataframe qith X: time intervale from date_range(), Y: Run-id. For each row the updates received in the time interval. 
# dopo faccio join su tr e run id, controlla che si possa fare join su una chiave con due campi
