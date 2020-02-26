#! /usr/bin/env python3

import unittest 
import pandas as pd
import numpy as np
import pandas_BGP as bgp
from helper_functions import *

def test_equal(frame, value):
    return frame.min() == frame.max() == value

class DataTest(unittest.TestCase):

    def setUp(self):
        self.t_r = 10
        self.runs = 100
        self.ASes = 10
        self.indexes = make_index(self.t_r, self.runs, self.ASes)

            
        self.run_table_index = pd.MultiIndex.from_product(self.indexes, names=bgp.names)
        #self.run_table = pd.DataFrame(self.data_set, index=self.run_table_index, 
        #                              columns = ['tot_updates'])
        self.update_table_index = pd.timedelta_range(0, periods=bgp.samples, freq=bgp.delta)


    def test_zero(self):
        self.data_set, self.time_data = fill_run_table(bgp.names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       mode='ZERO', 
                                                       time_len=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)
        self.assertFalse(update_table.values.any()) 

    def test_random(self):
        self.data_set, self.time_data = fill_run_table(names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       mode='RANDOM', 
                                                       time_len=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)
        self.assertTrue(np.isclose(bgp.avg_update(update_table), 0, atol=0.01))

    def test_linear(self):
        self.data_set, self.time_data = fill_run_table(names, self.indexes[0], 
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
        self.data_set, self.time_data = fill_run_table(names, self.indexes[0], 
                                                       self.indexes[1], 
                                                       self.indexes[2], 
                                                       mode='INCREASING_L', 
                                                       time_len=bgp.samples)
        update_table = pd.DataFrame(self.time_data, index=self.update_table_index, 
                                         columns=self.run_table_index)


        data = dict.fromkeys(self.indexes[0], 0)
        per_AS = dict.fromkeys(self.indexes[0], dict())
        mean = 0
        for t_r in per_AS:
            per_AS[t_r] = dict.fromkeys(self.indexes[0], 0)

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



                

