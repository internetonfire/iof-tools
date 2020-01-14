if (!exists("outfile")) outfile='out.pdf'
if (!exists("inputfile")) inputfile='logs.txt'
if (!exists("type")) type=1
if (!exists("timeRange")) timeRange="[s]"
if (!exists("yrng")) yrng=20
if (!exists("y2rng")) y2rng=20
if (!exists("xmin")) xmin=0
if (!exists("xmax")) xmax=70

set datafile separator ','
set ylabel "Number of AS"
set y2label "# of updates"
set xlabel "Time from route change ".timeRange
set y2tics
set ytics nomirror
set key right top
set yrange [0:yrng]
set y2range [0.01:y2rng]
set xrange [xmin:xmax]
set terminal pdf
set output outfile
set logscale y2 10
if (type > 0) {
    plot inputfile i 1 u 1:2 w lp t 'Converged ASes',\
    '' i 1 u 1:4 w l lt 2 dashtype 2 notitle,\
    '' i 2 u 1:2 w lp t 'Updates received' axes x1y2,\
    '' i 3 u 1:2 w l t 'total updates' axes x1y2
} else {
    plot inputfile i 1 u 1:2 w lp t 'Converged ASes',\
    '' i 1 u 1:4 w l lt 2 dashtype 2 notitle
}
