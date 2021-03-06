#! /usr/bin/env python3

import unittest 
import pandas as pd
import numpy as np
import datetime
import pandas_lib as plib
import data_analysis as da
from os import path
from shutil import unpack_archive 
from collections import defaultdict
import itertools as it

def test_equal(frame, value):
    return frame.min() == frame.max() == value

def is_monotone(array):
    # diff returns array of differences with next value
    return np.all(np.diff(array) >= 0)

def make_index(t_r_number=3, run_id_number=3, AS_number=5, strategy=['']):
    AS_list = ['AS' + str(x) for x in range(AS_number)]
    t_r_list = AS_list[:t_r_number]
    run_id_list = list(range(run_id_number))
    return([t_r_list, run_id_list, AS_list, strategy])


def fill_run_table(names, t_r_list, run_id_list, AS_list, strategy, mode='ZERO', 
                   samples=0, delta='100ms'):
    """ creates a list of dictionaries to fill a multiindex dataframe with
        dummy data """
    data = []
    time_data = []
    max_d = 9
    zero_time = pd.Timedelta('0 days 00:00:00')
    timedelta = pd.Timedelta(delta)
    end_time = zero_time + timedelta*samples
    for idx, val in enumerate(it.product(t_r_list, run_id_list, AS_list, strategy)):
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
 

class DataTest(unittest.TestCase):

    def setUp(self):
        self.t_r = 2
        self.runs = 2
        self.ASes = 3
        self.indexes = make_index(self.t_r, self.runs, self.ASes)

            
        self.run_table_index = pd.MultiIndex.from_product(self.indexes, 
                                                          names=plib.index_names)
        self.update_table_index = pd.timedelta_range(0, periods=plib.samples, 
                                                     freq=plib.delta)

        self.test_data = 'tests/test-data/'
        self.test_datafile_MRAI = self.test_data + 'RES-1K.tgz'
        self.test_datafolder_MRAI = self.test_data + 'RES-1K/'
        self.test_data_strategy_MRAI = self.test_datafolder_MRAI + 'RES-1K-1SEC'
        self.test_datafile_PARTIAL = self.test_data + 'RES-1K-0.1.tgz'
        self.test_datafolder_PARTIAL = self.test_data + 'RES-1K-30SEC-0.1/'
        if not path.isdir(self.test_datafolder_MRAI):
            unpack_archive(self.test_datafile_MRAI, self.test_data)
        if not path.isdir(self.test_datafolder_PARTIAL):
            unpack_archive(self.test_datafile_PARTIAL, self.test_data)



    def test_zero(self):
        self.data_set, self.time_data = fill_run_table(plib.index_names, 
                                                       self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       self.indexes[3], 
                                                       mode='ZERO', 
                                                       samples=plib.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)
        self.assertFalse(update_table.values.any()) 


    def test_linear(self):
        self.data_set, self.time_data = fill_run_table(plib.index_names, 
                                                       self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       self.indexes[3], 
                                                       mode='LINEAR', 
                                                       samples=plib.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)



        self.assertFalse(update_table.loc[:,((self.indexes[0][0], 
                                              self.indexes[1][0],
                                              self.indexes[2][0],
                                              self.indexes[3][0]))].any())
        self.assertTrue(test_equal(update_table.loc[:,(('AS0', 0, 'AS1', ''))], 1))

    def test_avg(self):
        self.data_set, self.time_data = fill_run_table(plib.index_names, 
                                                       self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       self.indexes[3], 
                                                       mode='LINEAR', 
                                                       samples=plib.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)


        data = dict.fromkeys(self.indexes[0], 0)
        per_AS = dict.fromkeys(self.indexes[0], dict())
        mean = 0
        for t_r in per_AS:
            per_AS[t_r] = dict.fromkeys(self.indexes[2], 0)

        for column in list(update_table):
            mean += update_table[column].sum()
            t_r = column[0]
            data[t_r] += update_table[column].sum()
            AS = column[2]
            per_AS[t_r][AS] += update_table[column].sum()
        avg = da.avg_update_by_t_r(update_table)
        avg_per_AS = da.avg_update_by_t_r_by_AS(update_table)
        for t_r,v in data.items():
            self.assertTrue(np.isclose(v/(self.runs*self.ASes*plib.samples), 
                            avg[t_r]))
            for AS, vv in per_AS[t_r].items():
                self.assertTrue(np.isclose(vv/(self.runs*plib.samples), 
                                avg_per_AS[t_r][AS]))
        self.assertTrue(np.isclose(mean/(self.t_r*self.runs*self.ASes*plib.samples), 
                        da.avg_update(update_table)))


    def test_per_sec(self):
        data_set, time_data = fill_run_table(plib.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=plib.samples)
        update_table = pd.DataFrame(time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)


        per_t_r = dict.fromkeys(self.indexes[0], None)
        per_t_r_per_AS = dict.fromkeys(self.indexes[0], dict())
        for t_r in per_t_r:
            per_t_r_per_AS[t_r] = dict.fromkeys(self.indexes[2], None)
        for column in list(update_table):
            t_r = column[0]
            try:
                per_t_r[t_r] += update_table[column]
            except TypeError:
                per_t_r[t_r] = update_table[column].copy()

            AS = column[2]
            try:
                per_t_r_per_AS[t_r][AS] += update_table[column]
            except TypeError:
                per_t_r_per_AS[t_r][AS] = update_table[column].copy()
        updates_per_sec = da.update_by_t_r_per_sec(update_table)
        updates_per_AS_per_sec = da.update_by_t_r_by_AS_per_sec(update_table)
        for t_r in per_t_r:
            self.assertTrue(per_t_r[t_r].equals(updates_per_sec[t_r]))
            for AS in per_t_r_per_AS[t_r]:
                self.assertTrue(per_t_r_per_AS[t_r][AS].equals(
                                    updates_per_AS_per_sec[(t_r, AS)]))


    def test_convergence(self):

        data_set, time_data = fill_run_table(plib.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=plib.samples)
        run_table = pd.DataFrame(data_set, index=self.run_table_index)
        conv_time, _ = da.conv_time(run_table)
        conv_time_per_dist, _ = da.conv_time_by_distance(run_table, plot=False)
        self.assertEqual(max(conv_time), 1)
        self.assertTrue(is_monotone(conv_time))
        self.assertEqual(conv_time_per_dist.max().sum(), len(conv_time_per_dist.columns))
        for c in conv_time_per_dist:
            self.assertTrue(is_monotone(conv_time_per_dist[c].notna()))


    def test_convergence_fail(self):
        self.skipTest('Skipping test that shows that resample does not work')

        data_set, time_data = fill_run_table(plib.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=plib.samples)
        run_table = pd.DataFrame(data_set, index=self.run_table_index)
        conv_dict = {}
        for t in self.update_table_index:
            conv_dict[t] = 0
        for t in sorted(run_table['conv_time'].values):
            for tt in conv_dict.keys():
                if pd.Timedelta(t) <= tt:
                    conv_dict[tt] += 1
        conv_time = plib.conv_time(run_table, self.update_table_index)
        keys = conv_time.keys()[:-1]
        for idx, k in enumerate(keys):
            if k in conv_dict:
                self.assertEqual(conv_time[k], conv_dict[k])

    def test_real_data_MRAI(self):
        class FakeArgs():
            def __init__(self, ff):
                self.ff = ff
                self.l = 2
                self.v = False
                self.T = '100ms'
        
        indexes = make_index()
        t_r_list = [285, 514, 529] # see comment at beginning of parse_folder()
        run_id_list = [1,2]
        AS_list = [x for x in range(1, 1001)]
        strategy = ['1SEC']
        run_table_index = pd.MultiIndex.from_product([t_r_list, run_id_list, 
                                                      AS_list, strategy])

        _, [run_table, update_event] = plib.parse_folders_MRAI(
                                                  FakeArgs(self.test_data_strategy_MRAI), 
                                                  [0,1,2,3,4,5])
        run_set = set(run_table_index)
        run_set_II = set(run_table.index)
        self.assertEqual(run_set, run_set_II)


        node_stats_list = []
        node_stats_list.append({'AS':301, 'run':1, 'conv_time':'2020-02-11 20:28:00.069', 
            'best_path':'70|40|2|153|285', 'reconf_time':'2020-02-11 20:27:56.135', 
            't_r':285, 'tot_updates':5})
        node_stats_list.append({'AS':401, 'run':2, 'conv_time':'2020-02-11 20:33:34.890', 
            'best_path':'153|285|285|285|285|285|285|285', 
            'reconf_time':'2020-02-11 20:33:34.867', 't_r':285, 'tot_updates':1})
        node_stats_list.append({'AS':501, 'run':2, 'conv_time':'2020-02-11 21:30:13.545', 
            'best_path':'76|17|514|514|514|514|514|514|514', 
            'reconf_time':'2020-02-11 21:30:09.611', 't_r':514, 'tot_updates':5})


        for node_stats in node_stats_list:
            AS_data = run_table.loc[node_stats['t_r'], 
                                    node_stats['run'],
                                    node_stats['AS'], '1SEC']
            self.assertEqual(AS_data['distance_AS_from_tr'], 
                    len(set(node_stats['best_path'].split('|'))))
            rel_reconf_time = pd.Timedelta(
                    datetime.datetime.strptime(node_stats['conv_time'], 
                                               '%Y-%m-%d %H:%M:%S.%f')-
                    datetime.datetime.strptime(node_stats['reconf_time'], 
                                               '%Y-%m-%d %H:%M:%S.%f'))
            self.assertTrue(AS_data['conv_time'] >= rel_reconf_time - pd.Timedelta('50ms') )
            self.assertTrue(AS_data['conv_time'] <= rel_reconf_time + pd.Timedelta('50ms') )
            self.assertTrue(AS_data['tot_updates'], node_stats['tot_updates'])



    def test_real_data_PARTIAL(self):
        """ testing the folder structure is parsed correctly """
        class FakeArgs():
            def __init__(self, ff):
                self.ff = ff
                self.l = 2
                self.v = False
                self.T = '100ms'
        
        indexes = make_index()
        t_r_list = [514, 761] # see comment at beginning of parse_folder()
        run_id_list = [1,2]
        AS_list = [x for x in range(1, 1001)]
        strategy = ['0.1']
        run_table_index = pd.MultiIndex.from_product([t_r_list, run_id_list, 
                                                      AS_list, strategy])

        _, [run_table, update_event] = plib.parse_folders_MRAI(
                                                  FakeArgs(self.test_datafolder_PARTIAL), 
                                                  [0,1,2,3,4,5], action='PARTIAL')
        self.assertEqual(len(run_table.index.levels[0]), 2)
        self.assertEqual(len(run_table.index.levels[1]), 2)
        self.assertEqual(len(run_table.index.levels[2]), 1000)
        self.assertEqual(len(run_table.index.levels[3]), 1)
        self.assertEqual(run_table.index.levels[3][0], '0.1')



    def test_real_data_DPC(self):
        # TBD
        self.assertTrue(0)
