import itertools as it
import numpy as np

names=['t_r', 'run_id', 'AS']
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
 
