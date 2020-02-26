#! /usr/bin/env python3

import unittest 
import pandas as pd
import numpy as np
import pandas_BGP as bgp
import helper_functions as hf

def test_equal(frame, value):
    return frame.min() == frame.max() == value

bgp.samples=3
class DataTest(unittest.TestCase):

    def setUp(self):
        self.t_r = 2
        self.runs = 2
        self.ASes = 3
        self.indexes = hf.make_index(self.t_r, self.runs, self.ASes)

            
        self.run_table_index = pd.MultiIndex.from_product(self.indexes, names=bgp.index_names)
        #self.run_table = pd.DataFrame(self.data_set, index=self.run_table_index, 
        #                              columns = ['tot_updates'])
        self.update_table_index = pd.timedelta_range(0, periods=bgp.samples, freq=bgp.delta)


    def test_zero(self):
        self.data_set, self.time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       mode='ZERO', 
                                                       time_len=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)
        self.assertFalse(update_table.values.any()) 


    def test_linear(self):
        self.data_set, self.time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       mode='LINEAR', 
                                                       time_len=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)



        self.assertFalse(update_table.loc[:,((self.indexes[0][0], 
                                              self.indexes[1][0],
                                              self.indexes[2][0]))].any())
        self.assertTrue(test_equal(update_table.loc[:,(('AS0', 0, 'AS1'))], 1))

    def test_avg(self):
        self.data_set, self.time_data = hf.fill_run_table(bgp.index_names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       mode='LINEAR', 
                                                       time_len=bgp.samples)
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
                                                    mode='INCREASING_L', 
                                                    time_len=bgp.samples)
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




                


                

