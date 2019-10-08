#!/usr/bin/env zsh

python log_parser.py -ff BGPpysim/out30sec/  -c -t > 30Sec.txt
gnuplot -e "outfile='30Sec_fixed_50_simulations_avg.pdf'; inputfile='30Sec.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outFabrikant/  -c -t > fabr.txt
gnuplot -e "outfile='fabrikant_50_simulations_avg.pdf'; inputfile='fabr.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outInversefabrikant/  -c -t > IFabr.txt
gnuplot -e "outfile='InversedFabrikant_50_simulations_avg.pdf'; inputfile='IFabr.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outSimpleheuristic/  -c -t -T DSEC> heur.txt
gnuplot -e "outfile='SimpleHeuristic_50_simulations_avg.pdf'; inputfile='heur.txt'; timeRange='[DSEC]'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outNoMRAI/  -c -t -T CSEC> NoMRAI.txt
gnuplot -e "outfile='NoMRAI_50_simulations_avg.pdf'; inputfile='NoMRAI.txt'; timeRange='[CSEC]'" plot_logs.gnuplot

python log_parser.py -ff BGPpysim/out30sec/  -c -t -n > 30Sec_n.txt
gnuplot -e "outfile='30Sec_fixed_50_simulations_avg_withNegative.pdf'; inputfile='30Sec_n.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outFabrikant/  -c -t -n > fabr_n.txt
gnuplot -e "outfile='fabrikant_50_simulations_avg_withNegative.pdf'; inputfile='fabr_n.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outInversefabrikant/  -c -t -n > IFabr_n.txt
gnuplot -e "outfile='InversedFabrikant_50_simulations_avg_withNegative.pdf'; inputfile='IFabr_n.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outSimpleheuristic/  -c -t -n -T DSEC> heur_n.txt
gnuplot -e "outfile='SimpleHeuristic_50_simulations_avg_withNegative.pdf'; inputfile='heur_n.txt'; timeRange='[DSEC]'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outNoMRAI/  -c -t -n -T CSEC> NoMRAI_n.txt
gnuplot -e "outfile='NoMRAI_50_simulations_avg_withNegative.pdf'; inputfile='NoMRAI_n.txt'; timeRange='[CSEC]'" plot_logs.gnuplot