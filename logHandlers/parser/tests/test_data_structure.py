#! /usr/bin/env python3

import unittest 
import pandas as pd
import numpy as np
import datetime
import pandas_lib as plib
from os import path
from shutil import unpack_archive 
from collections import defaultdict

def test_equal(frame, value):
    return frame.min() == frame.max() == value

def is_monotone(array):
    # diff returns array of differences with next value
    return np.all(np.diff(array) >= 0)

class DataTest(unittest.TestCase):

    def setUp(self):
        self.t_r = 2
        self.runs = 2
        self.ASes = 3
        self.indexes = plib.make_index(self.t_r, self.runs, self.ASes)

            
        self.run_table_index = pd.MultiIndex.from_product(self.indexes, 
                                                          names=plib.index_names)
        self.update_table_index = pd.timedelta_range(0, periods=plib.samples, 
                                                     freq=plib.delta)

        self.test_data = 'tests/test-data/'
        self.test_datafile = self.test_data + 'RES-1K.tgz'
        self.test_datafolder = self.test_data + 'RES-1K/'
        self.test_data_strategy = self.test_datafolder + 'RES-1K-1SEC'
        if not path.isdir(self.test_datafolder):
            unpack_archive(self.test_datafile, self.test_data)



    def test_zero(self):
        self.data_set, self.time_data = plib.fill_run_table(plib.index_names, 
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
        self.data_set, self.time_data = plib.fill_run_table(plib.index_names, 
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
        self.data_set, self.time_data = plib.fill_run_table(plib.index_names, 
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
        avg = plib.avg_update_by_t_r(update_table)
        avg_per_AS = plib.avg_update_by_t_r_by_AS(update_table)
        for t_r,v in data.items():
            self.assertTrue(np.isclose(v/(self.runs*self.ASes*plib.samples), 
                            avg[t_r]))
            for AS, vv in per_AS[t_r].items():
                self.assertTrue(np.isclose(vv/(self.runs*plib.samples), 
                                avg_per_AS[t_r][AS]))
        self.assertTrue(np.isclose(mean/(self.t_r*self.runs*self.ASes*plib.samples), 
                        plib.avg_update(update_table)))


    def test_per_sec(self):
        data_set, time_data = plib.fill_run_table(plib.index_names, self.indexes[0], 
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
        updates_per_sec = plib.update_by_t_r_per_sec(update_table)
        updates_per_AS_per_sec = plib.update_by_t_r_by_AS_per_sec(update_table)
        for t_r in per_t_r:
            self.assertTrue(per_t_r[t_r].equals(updates_per_sec[t_r]))
            for AS in per_t_r_per_AS[t_r]:
                self.assertTrue(per_t_r_per_AS[t_r][AS].equals(
                                    updates_per_AS_per_sec[(t_r, AS)]))


    def test_convergence(self):

        data_set, time_data = plib.fill_run_table(plib.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=plib.samples)
        run_table = pd.DataFrame(data_set, index=self.run_table_index)
        conv_time, _ = plib.conv_time(run_table)
        conv_time_per_dist, _ = plib.conv_time_by_distance(run_table, plot=False)
        self.assertEqual(max(conv_time), 1)
        self.assertTrue(is_monotone(conv_time))
        self.assertEqual(conv_time_per_dist.max().sum(), len(conv_time_per_dist.columns))
        for c in conv_time_per_dist:
            self.assertTrue(is_monotone(conv_time_per_dist[c].notna()))


    def test_convergence_fail(self):
        self.skipTest('Skipping test that shows that resample does not work')

        data_set, time_data = plib.fill_run_table(plib.index_names, self.indexes[0], 
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

    def test_real_data(self):
        class FakeArgs():
            def __init__(self, ff):
                self.ff = ff
                self.l = 2
                self.v = False
        
        indexes = plib.make_index()
        t_r_list = [285, 514, 529] # see comment at beginning of parse_folder()
        run_id_list = [1,2]
        AS_list = [x for x in range(1, 1001)]
        strategy = ['1SEC']
        run_table_index = pd.MultiIndex.from_product([t_r_list, run_id_list, 
                                                      AS_list, strategy])

        run_table, update_event = plib.parse_folders(
                                                  FakeArgs(self.test_data_strategy), 
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



        




