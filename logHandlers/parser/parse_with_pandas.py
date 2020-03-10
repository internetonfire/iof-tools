#!/usr/bin/env python3
import pandas as pd
import numpy as np
import pandas_lib as plib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class Dummy():
    def savefig(self, x):
        pass
    def close(self):
        pass

def gen_MRAI_graphs(run_table, update_table, pdf):
    _, pl = plib.updates_by_distance(run_table)
    pdf.savefig(pl.get_figure())
    _, pl = plib.updates_by_distance_per_sec(run_table, column='avg_update_per_sec')
    pdf.savefig(pl.get_figure())
    _, pl = plib.updates_by_distance_per_sec(run_table, column='max_update_per_sec')
    pdf.savefig(pl.get_figure())
    _, pl = plib.nodes_by_dist(run_table)
    pdf.savefig(pl.get_figure())
    _, pl = plib.conv_time(run_table, plot=True)
    pdf.savefig(pl.get_figure())
    _, pl = plib.conv_time_by_distance(run_table)
    pdf.savefig(pl.get_figure())
    _, pl = plib.conv_time_by_distance(run_table, column='distance_AS_before_t')
    pdf.savefig(pl.get_figure())
    _, pl = plib.conv_time_by_distance(run_table, column='distance_AS_after_t')
    pdf.savefig(pl.get_figure())
    pdf.close()


if __name__ == '__main__':
    args = plib.parse_args()
    T_ASes = set()
    DPC = False
    MRAI = False
    if args.G:
        pass # TODO implement graph parsing here
    else:
        T_ASes = set(range(args.tnodes))

    if args.P:
        run_table = pd.read_pickle(args.P[0])
        update_table = pd.read_pickle(args.P[1])
    elif args.ff:
        kind, res = plib.parse_folders(args, T_ASes)
        if args.p:
            if kind == 'MRAI':
                MRAI = True
                res[0].to_pickle(args.p + "-runs.pickle")
                res[1].to_pickle(args.p + "-update.pickle")
            if kind == 'DPC':
                DPC = True
                res[0].to_pickle(args.p + "-DPC.pickle")
    if MRAI:
        if update_table.empty:
            stop = max(run_table['conv_time'])
            number = stop/pd.Timedelta(args.T)
            idx = pd.Index(pd.date_range(0, number, freq=pd.Timedelta(args.T)))
        else:
            idx = update_table.index
    if args.pdf:
        pdf = PdfPages(args.pdf)
    else:
        pdf = Dummy()

    if MRAI:
        gen_MRAI_graphs(run_table, update_table, pdf)
