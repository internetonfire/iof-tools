#!/usr/bin/env python3
import pandas as pd
import numpy as np
import pandas_lib as plib
import matplotlib.pyplot as plt


if __name__ == '__main__':
    indexes = plib.make_index()
    data_set, time_data = plib.fill_run_table(plib.index_names, indexes[0], 
            indexes[1], indexes[2],
            indexes[3], mode='INCREASING_L', samples=plib.samples)
    run_table_index = pd.MultiIndex.from_product(indexes, names=plib.index_names)
    run_table = pd.DataFrame(data_set, index=run_table_index, 
                             columns=plib.column_names)
    update_table_index = pd.timedelta_range(0, periods=plib.samples, freq=plib.delta)
    update_table = pd.DataFrame(time_data, index=update_table_index, 
                                columns=run_table_index)
    args = plib.parse_args()
    plib.check_data(update_table, run_table)
    T_ASes = set()
    if args.G:
        pass # TODO implement graph parsing here
    else:
        T_ASes = set(range(args.tnodes))

    if args.P:
        run_table = pd.read_pickle(args.P[0])
        update_table = pd.read_pickle(args.P[1])
    elif args.ff:
        run_table, update_table = plib.parse_folders(args, T_ASes)
    if args.p:
        run_table.to_pickle(args.p + "-runs.pickle")
        update_table.to_pickle(args.p + "-update.pickle")
    ct = plib.conv_time_per_distance(run_table, update_table.index)
    pl = ct.plot(title="Convergence time by distance from T_r")
    pl.set_xlabel('time')
    pl.set_ylabel('# of ASes')
    ct = plib.conv_time_per_distance(run_table, update_table.index, 
                                     column='distance_AS_after_t')
    pl = ct.plot(title="Convergence time by hops after T nodes")
    pl.set_xlabel('time')
    pl.set_ylabel('# of ASes')
    ct = plib.conv_time_per_distance(run_table, update_table.index, 
                                     column='distance_AS_before_t')
    pl = ct.plot(title="Convergence time by hops before T nodes")
    pl.set_xlabel('time')
    #plt.show()
    #print(run_table)
    #print(update_table)
    



    
    # just to recall how to slice on inner layers
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))])
    # then slice the time serie
    # print(update_table.loc[:, (('AS1', slice(None), 'AS1'))]['00:00:00.770000':'00:00:00.870000'])
