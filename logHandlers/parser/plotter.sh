#!/bin/bash
python log_parser_sum_mean.py -ff ../../tmp/fab/RES-LOGS/RES-F16N-NOMRAI -c -t -T MSEC > FAB_NOMRAI_SUM_MEAN.txt
python log_parser_sum_mean.py -ff ../../tmp/fab/RES-LOGS/RES-F16N-30SEC -c -t > FAB_30SEC_SUM_MEAN.txt
python log_parser_sum_mean.py -ff ../../tmp/fab/RES-LOGS/RES-F16N-DPC -c -t > FAB_DPC_SUM_MEAN.txt
python log_parser_sum_mean.py -ff ../../tmp/fab/RES-LOGS/RES-F16N-FABRIKANT -c -t > FAB_FAB_SUM_MEAN.txt
python log_parser_sum_mean.py -ff ../../tmp/drive-download-20191229T142734Z-001/2019-12-23_4K-runs/RES-4K-30SEC/tot -c -t > 4K_30SEC_SUM_MEAN.txt
python log_parser_sum_mean.py -ff ../../tmp/drive-download-20191229T142734Z-001/2019-12-23_4K-runs/RES-4K-DPC/tot -c -t > 4K_DPC_SUM_MEAN.txt

cp FAB* ../../plotsGenerator/Gnuplot
cp 4K* ../../plotsGenerator/Gnuplot

cd ../../plotsGenerator/Gnuplot

gnuplot -e "outfile='f17n-NOMRAI.pdf'; inputfile='FAB_NOMRAI_SUM_MEAN.txt'; yrng=30; y2rng=200; xmax=224; xmin=-10; timeRange='[ms]'" plot_logs.gnuplot
gnuplot -e "outfile='f16n-30SEC.pdf'; inputfile='FAB_30SEC_SUM_MEAN.txt'; yrng=30; y2rng=500; xmax=177; xmin=-10" plot_logs.gnuplot
gnuplot -e "outfile='f16n-DPC.pdf'; inputfile='FAB_DPC_SUM_MEAN.txt'; yrng=30; y2rng=500; xmax=18; xmin=-10" plot_logs.gnuplot
gnuplot -e "outfile='f16n-FAB.pdf'; inputfile='FAB_FAB_SUM_MEAN.txt'; yrng=30; y2rng=500; xmax=28; xmin=-10" plot_logs.gnuplot
gnuplot -e "outfile='4K-30SEC.pdf'; inputfile='4K_30SEC_SUM_MEAN.txt'; yrng=5000; y2rng=500000; xmax=234; xmin=-10" plot_logs.gnuplot
gnuplot -e "outfile='4k-DPC.pdf'; inputfile='4K_DPC_SUM_MEAN.txt'; yrng=5000; y2rng=500000; xmax=89; xmin=-10" plot_logs.gnuplot
