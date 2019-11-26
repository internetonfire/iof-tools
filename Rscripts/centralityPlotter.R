# set the environment
setwd("~/src/iof-tools/Rscripts")

library(dplyr)
library(ggplot2)
library(Hmisc)

source("functions.R")

args <- commandArgs(trailingOnly = TRUE)

file <- "centrality.csv"
outFile <- "outCentrality"

csv1 <- read.csv(file, header = T, sep=" ")

plot(ecdf(csv1$centrality),
     main="CDF for node centrality",
     xlab="centrality",
     ylab="CDF")