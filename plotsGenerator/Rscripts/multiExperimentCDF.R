# set the environment
setwd("~/src/iof-tools/plotsGenerator/Rscripts")

library(dplyr)
library(ggplot2)
library(Hmisc)

source("functions.R")

args <- commandArgs(trailingOnly = TRUE)

folder1 <- args[1]
folder2 <- args[2]
outFile <- args[3]

fileList1 <- list.files(folder1,full.names = TRUE)
fileList2 <- list.files(folder2,full.names = TRUE)

Messagesdata <- listUpdtes(fileList1)
Messagesdata2 <- listUpdtes(fileList2)

pdf(paste("nMessages", outFile, sep="_"), width = 11.69, height = 8.27)
#df <- data.frame(x = c(Messagesdata, Messagesdata2),ggg = factor(rep(1:2, c(10,10))))

#df <- df[order(df$x), ]
#df$ecdf <- ave(df$x, df$ggg, FUN=function(x) seq_along(x)/length(x))

#ggplot(df, aes(x, ecdf, colour = ggg)) + geom_line() + scale_colour_hue(name="MRAI style", labels=c('ExponentialFabr','ConstantFabr'))
ecdf1 <- ecdf(Messagesdata)
ecdf2 <- ecdf(Messagesdata2)
plot(ecdf1,
     main="CDF for number of messages to reach convergence",
     xlab="Number of messages",
     ylab="CDF",
     xlim = c(0,300),
     verticals=TRUE, do.points=FALSE)
plot(ecdf2, verticals=TRUE, do.points=FALSE, add=TRUE, col='orange')
legend("topleft", legend=c("Random MRAI", "Classical Fabrikant"),
       col=c("black", "orange"),lty=1:1, cex=0.8,)
dev.off()

Timedata <- c()
for (file in fileList1) {
  csv_obj <- read.csv(file, header = T)
  Timedata <- c(Timedata, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}

Timedata2 <- c()
for (file in fileList2) {
  csv_obj <- read.csv(file, header = T)
  Timedata2 <- c(Timedata2, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}

ecdf1 <- ecdf(Timedata)
ecdf2 <- ecdf(Timedata2)

pdf(paste("convTime", outFile, sep="_"), width = 11.69, height = 8.27)
plot(ecdf1,
     main="CDF for time[s] to reach convergence",
     xlab="time [s]",
     ylab="CDF",
     xlim = c(0,170),
     verticals=TRUE, do.points=FALSE)
plot(ecdf2, verticals=TRUE, do.points=FALSE, add=TRUE, col='orange')
legend("topleft", legend=c("Random MRAI", "Classical Fabrikant"),
       col=c("black", "orange"),lty=1:1, cex=0.8,)
dev.off()