#!/usr/bin/env zsh

python log_parser.py -ff BGPpysim/out30sec/  -c -t > 30Sec.txt
gnuplot -e "outfile='30Sec_fixed_50_simulations_avg.pdf'; inputfile='30Sec.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outFabrikant/  -c -t > fabr.txt
gnuplot -e "outfile='fabrikant_50_simulations_avg.pdf'; inputfile='fabr.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outInversefabrikant/  -c -t > IFabr.txt
gnuplot -e "outfile='InversedFabrikant_50_simulations_avg.pdf'; inputfile='IFabr.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outSimpleheuristic/  -c -t > heur.txt
gnuplot -e "outfile='SimpleHeuristic_50_simulations_avg.pdf'; inputfile='heur.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outNoMRAI/  -c -t > NoMRAI.txt
gnuplot -e "outfile='NoMRAI_50_simulations_avg.pdf'; inputfile='NoMRAI.txt'" plot_logs.gnuplot

python log_parser.py -ff BGPpysim/out30sec/  -c -t -n > 30Sec.txt
gnuplot -e "outfile='30Sec_fixed_50_simulations_avg_withNegative.pdf'; inputfile='30Sec.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outFabrikant/  -c -t -n > fabr.txt
gnuplot -e "outfile='fabrikant_50_simulations_avg_withNegative.pdf'; inputfile='fabr.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outInversefabrikant/  -c -t -n > IFabr.txt
gnuplot -e "outfile='InversedFabrikant_50_simulations_avg_withNegative.pdf'; inputfile='IFabr.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outSimpleheuristic/  -c -t -n > heur.txt
gnuplot -e "outfile='SimpleHeuristic_50_simulations_avg_withNegative.pdf'; inputfile='heur.txt'" plot_logs.gnuplot
python log_parser.py -ff BGPpysim/outNoMRAI/  -c -t -n > NoMRAI.txt
gnuplot -e "outfile='NoMRAI_50_simulations_avg_withNegative.pdf'; inputfile='NoMRAI.txt'" plot_logs.gnuplot