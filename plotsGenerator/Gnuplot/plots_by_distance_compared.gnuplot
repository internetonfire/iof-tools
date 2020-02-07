print inputfile30s, inputfile15s, inputfileDPC
set terminal eps 
set output outputfile
set datafile separator ','
set key top left
set xlabel "distance"
set ylabel "# of updates (cumulative)"
set ytics nomirror
set multiplot
set lmargin at screen 0.15
set size 1, 0.5
set origin 0, 0
plot inputfile15s i 4 u 1:4 w p pt 7 t '',  inputfile30s i 4 u 1:6 w lp t "30s", inputfile15s i 4 u 1:6 w lp t "15s", inputfileDPC i 4 u 1:6 w lp  t "DPC"

set ylabel "avg convergence time"
set origin 0, 0.5
plot inputfile15s i 4 u 1:4 w p pt 7 t '',  inputfile30s i 4 u 1:2 w lp t "30s", inputfile15s i 4 u 1:2 w lp t "15s", inputfileDPC i 4 u 1:2 w lp  t "DPC"
