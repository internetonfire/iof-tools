if (!exists("outfile")) outfile='out.pdf'
if (!exists("inputfile")) inputfile='logs.txt'
if (!exists("type")) type=1

set datafile separator ','
set ylabel "ASes"
set y2label "# of updates"
set xlabel "Relative Time"
set y2tics
set ytics nomirror
set key below bottom
set yrange [0:21]
set terminal pdf
set output outfile
if (type > 0) {
    plot inputfile i 1 u 1:2 w lp t 'Converged ASes',\
    '' i 1 u 1:4 w l t 'number of ASes',\
    '' i 2 u 1:2 w lp t 'Updates received' axes x1y2
} else {
    plot inputfile i 1 u 1:2 w lp t 'Converged ASes',\
    '' i 1 u 1:4 w l t 'number of ASes'
}
