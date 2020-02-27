import itertools as it
import pandas as pd
import numpy as np

def make_index(t_r_number=3, run_id_number=3, AS_number=5):
    AS_list = ['AS' + str(x) for x in range(AS_number)]
    t_r_list = AS_list[:t_r_number]
    run_id_list = list(range(run_id_number))
    return([t_r_list, run_id_list, AS_list])


def fill_run_table(names, t_r_list, run_id_list, AS_list, mode='ZERO', samples=0, delta='100ms'):
    """ creates a list of dictionaries to fill a multiindex dataframe with
        dummy data """
    data = []
    time_data = []
    max_d = 9
    zero_time = pd.Timedelta('0 days 00:00:00')
    timedelta = pd.Timedelta(delta)
    end_time = zero_time + timedelta*samples
    for idx, val in enumerate(it.product(t_r_list, run_id_list, AS_list)):
        tot_updates = idx
        updates = [0] * samples
        if mode == 'RANDOM':
            updates = np.random.randn(samples)
        if mode == 'LINEAR':
            updates = [idx] * samples
        if mode == 'INCREASING':
            updates = range(samples)
        if mode == 'INCREASING_L':
            updates = [x*idx for x in range(samples)]
        data_dict = {}
        tot_updates = sum(updates)
        for i in range(len(names)): 
            data_dict[names[i]] = str(val[i])
        data_dict['tot_updates'] =  tot_updates
        data_dict['distance_AS_from_tr'] =  np.random.randint(max_d) + 1
        data_dict['distance_tr_to_t'] =  np.random.randint(1,4)
        data_dict['distance_AS_after_t'] = max(data_dict['distance_AS_from_tr'] -\
                                           data_dict['distance_tr_to_t'], 0)
        slot_len = samples/max_d
        conv_sample = max((data_dict['distance_AS_from_tr']-1) * slot_len +\
                np.random.randint(-slot_len, slot_len-1), 0)
        data_dict['conv_time'] = zero_time + timedelta*conv_sample
        data_dict['last_up_time'] = max(data_dict['conv_time'] +\
                timedelta*np.random.rand()*slot_len, zero_time)
        data_dict['first_up_time'] = max(data_dict['conv_time'] -\
                timedelta*np.random.rand()*slot_len, zero_time)
        data.append(data_dict)
        time_data.append(updates)
    return data, np.matrix.transpose(np.array(time_data))
 
