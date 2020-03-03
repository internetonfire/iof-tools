#!/usr/bin/env python3
import pandas as pd
import numpy as np
import pandas_lib as plib
import matplotlib.pyplot as plt


if __name__ == '__main__':
    args = plib.parse_args()
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
    if update_table.empty:
        stop = max(run_table['conv_time'])
        number = stop/pd.Timedelta(args.T)
        idx = pd.Index(pd.date_range(0, number, freq=pd.Timedelta(args.T)))
    else:
        idx = update_table.index
    pl = plib.nodes_by_dist(run_table)
    print(update_table.index)
    ct, pl = plib.conv_time(run_table, plot=True)
    ct, pl = plib.conv_time_per_distance(run_table)
    ct, pl = plib.conv_time_per_distance(run_table, column='distance_AS_before_t')
    ct, pl = plib.conv_time_per_distance(run_table, column='distance_AS_after_t')
    plt.show()
    #print(run_table)
    #print(update_table)
