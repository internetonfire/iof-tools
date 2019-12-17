# set the environment
setwd("~/src/iof-tools/Rscripts")

library(dplyr)

source("functions.R")

args <- commandArgs(trailingOnly = TRUE)

folder1 <- args[1]
outFile <- args[2]

fileList1 <- list.files(folder1,full.names = TRUE)

Messagesdata <- listUpdtes(fileList1)
pdf(paste("nMessages", outFile, sep="_"), width = 11.69, height = 8.27)
plot(ecdf(Messagesdata),
     main="CDF for number of messages to reach convergence",
     xlab="Number of messages",
     ylab="CDF")
dev.off()

Timedata <- c()
for (file in fileList1) {
  csv_obj <- read.csv(file, header = T)
  Timedata <- c(Timedata, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}

pdf(paste("convTime", outFile, sep="_"), width = 11.69, height = 8.27)
plot(ecdf(Timedata),
     main="CDF for time[s] to reach convergence",
     xlab="time [s]",
     ylab="CDF")
dev.off()