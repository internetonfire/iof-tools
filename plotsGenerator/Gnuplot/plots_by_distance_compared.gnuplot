print inputfile30s, inputfile15s, inputfileDPC
set terminal eps size 5, 10
set output outputfile
set datafile separator ','
set key top left
set xlabel "distance"
set ylabel "# of updates (cumulative)"
set ytics nomirror
set multiplot
set lmargin at screen 0.15
set rmargin at screen 0.85
set size 1, 0.33
set origin 0, 0
plot inputfile15s i 4 u 1:4 w p pt 7 t '',  inputfile30s i 4 u 1:6 w lp t "30s", inputfile15s i 4 u 1:6 w lp t "15s", inputfileDPC i 4 u 1:6 w lp  t "DPC"

set ylabel "avg convergence time"
set origin 0, 0.33
plot inputfile15s i 4 u 1:4 w p pt 7 t '',  inputfile30s i 4 u 1:2 w lp t "30s", inputfile15s i 4 u 1:2 w lp t "15s", inputfileDPC i 4 u 1:2 w lp  t "DPC"

set ylabel "# updates per AS"
set y2label "fraction of ASes"
set origin 0, 0.66
set key top right
set logscale y
set y2tics
set ytics nomirror
plot inputfile15s i 4 u 1:4 w p pt 7 t '' axes x1y2,  inputfile30s i 4 u 1:5 w lp t "updates 30s", inputfile15s i 4 u 1:5 w lp t "updates 15s", inputfileDPC i 4 u 1:5 w lp  t "updates DPC",  inputfile30s i 4 u 1:3 w lp t "ASes 30s" axes x1y2, inputfile15s i 4 u 1:3 w lp t "ASes 15s" axes x1y2, inputfileDPC i 4 u 1:3 w lp  t "ASes DPC" axes x1y2


