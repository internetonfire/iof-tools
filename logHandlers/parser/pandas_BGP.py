#!/usr/bin/env python3
import pandas as pd
import numpy as np
import itertools as it


def make_index(t_r_number=3, run_id_number=3, AS_number=5):
    AS_list = ['AS' + str(x) for x in range(AS_number)]
    t_r_list = AS_list[:t_r_number]
    run_id_list = list(range(run_id_number))
    return([t_r_list, run_id_list, AS_list])

def fill_data(names, t_r_list, run_id_list, AS_list, mode='ZERO'):
    data = []
    for val in it.product(t_r_list, run_id_list, AS_list):
        updates = 0
        if mode == 'RANDOM':
            updates = np.random.random()
        data_dict = {}
        for i in range(len(names)): 
            data_dict[names[i]] = str(val[i])
        data_dict['updates'] =  str(updates)
        data.append(data_dict)
    return data
    
names=['t_r', 'run_id', 'AS']
indexes = make_index()
data_set = fill_data(names, indexes[0], indexes[1], indexes[2])
            
run_table_index = pd.MultiIndex.from_product(indexes, names=names)
run_table = pd.DataFrame(data_set, index=run_table_index, columns = ['updates'])
print(run_table)




# two tables on with run values (long list. each line with index: T_r, run_id), one dataframe qith X: time intervale from date_range(), Y: Run-id. For each row the updates received in the time interval. 
# dopo faccio join su tr e run id, controlla che si possa fare join su una chiave con due campi
