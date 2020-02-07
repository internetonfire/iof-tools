print inputfile
set terminal eps 
set output inputfile.".eps"
set datafile separator ','
set key top left
set xlabel "distance"
set ylabel "convergence time (avg of max)"
set y2label "# of updates (cumulative)"
set y2tics
set ytics nomirror
plot inputfile i 4 u 1:2 w lp t "avg convergence time", '' i 4 u 1:4 w p pt 7 t '',  '' i 4 u 1:6 w lp axes x1y2 t "# of updates"

set ytics nomirror
set ylabel "# updates per AS"
set y2label ""
set y2tics 
plot inputfile i 4 u 1:5 w lp t "avg number of updates per AS", '' i 4 u 1:4  w p pt 7 t '', '' i 4 u 1:3 w lp axes x1y2 t "fraction of ASes"
