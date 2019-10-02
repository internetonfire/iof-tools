set datafile separator ','
set ylabel "ASes"
set y2label "# of updates"
set xlabel "Relative Time"
set y2tics
set ytics nomirror
set key below bottom
set yrange [0:21]
plot 'logs.txt' i 1 u 1:2 w lp t 'Converged ASes',\
'' i 1 u 1:4 w l t 'number of ASes',\
'' i 2 u 1:2 w lp t 'Updates received' axes x1y2
