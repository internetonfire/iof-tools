#! /usr/bin/env python3

import unittest 
import pandas as pd
import numpy as np
import pandas_BGP as bgp
import helper_functions as hf
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
        self.indexes = hf.make_index(self.t_r, self.runs, self.ASes)

            
        self.run_table_index = pd.MultiIndex.from_product(self.indexes, names=bgp.index_names)
        self.update_table_index = pd.timedelta_range(0, periods=bgp.samples, freq=bgp.delta)


    def test_zero(self):
        self.data_set, self.time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       self.indexes[3], 
                                                       mode='ZERO', 
                                                       samples=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)
        self.assertFalse(update_table.values.any()) 


    def test_linear(self):
        self.data_set, self.time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       self.indexes[3], 
                                                       mode='LINEAR', 
                                                       samples=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)



        self.assertFalse(update_table.loc[:,((self.indexes[0][0], 
                                              self.indexes[1][0],
                                              self.indexes[2][0],
                                              self.indexes[3][0]))].any())
        self.assertTrue(test_equal(update_table.loc[:,(('AS0', 0, 'AS1', ''))], 1))

    def test_avg(self):
        self.data_set, self.time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       self.indexes[3], 
                                                       mode='LINEAR', 
                                                       samples=bgp.samples)
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
        avg = bgp.avg_update_per_t_r(update_table)
        avg_per_AS = bgp.avg_update_per_t_r_per_AS(update_table)
        for t_r,v in data.items():
            self.assertTrue(np.isclose(v/(self.runs*self.ASes*bgp.samples), avg[t_r]))
            for AS, vv in per_AS[t_r].items():
                self.assertTrue(np.isclose(vv/(self.runs*bgp.samples), avg_per_AS[t_r][AS]))
        self.assertTrue(np.isclose(mean/(self.t_r*self.runs*self.ASes*bgp.samples), 
                        bgp.avg_update(update_table)))


    def test_per_sec(self):
        data_set, time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=bgp.samples)
        update_table = pd.DataFrame(time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)


        per_sec = bgp.update_per_sec(update_table)
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
        updates_per_sec = bgp.update_per_t_r_per_sec(update_table)
        updates_per_AS_per_sec = bgp.update_per_t_r_per_AS_per_sec(update_table)
        for t_r in per_t_r:
            self.assertTrue(per_t_r[t_r].equals(updates_per_sec[t_r]))
            for AS in per_t_r_per_AS[t_r]:
                self.assertTrue(per_t_r_per_AS[t_r][AS].equals(
                                    updates_per_AS_per_sec[(t_r, AS)]))


    def test_convergence(self):

        data_set, time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=bgp.samples)
        run_table = pd.DataFrame(data_set, index=self.run_table_index)
        conv_time = bgp.conv_time(run_table, self.update_table_index)
        conv_time_per_dist = bgp.conv_time_per_distance(run_table, self.update_table_index)
        self.assertEqual(max(conv_time), self.t_r*self.runs*self.ASes)
        self.assertTrue(is_monotone(conv_time))
        self.assertEqual(conv_time_per_dist[-1:].values.sum(), self.t_r*self.runs*self.ASes)
        for c in conv_time_per_dist:
            self.assertTrue(is_monotone(conv_time_per_dist[c]))
        for t in conv_time_per_dist.index:
            self.assertEqual(conv_time_per_dist.loc[t].sum(), conv_time[t])


    def test_convergence_fail(self):

        data_set, time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                    self.indexes[1], 
                                                    self.indexes[2], 
                                                    self.indexes[3], 
                                                    mode='INCREASING_L', 
                                                    samples=bgp.samples)
        run_table = pd.DataFrame(data_set, index=self.run_table_index)
        conv_dict = {}
        for t in self.update_table_index:
            conv_dict[t] = 0
        for t in sorted(run_table['conv_time'].values):
            for tt in conv_dict.keys():
                if pd.Timedelta(t) <= tt:
                    conv_dict[tt] += 1
        conv_time = bgp.conv_time(run_table, self.update_table_index)
        keys = conv_time.keys()[:-1]
        for idx, k in enumerate(keys):
            if k in conv_dict:
                self.assertEqual(conv_time[k], conv_dict[k])
