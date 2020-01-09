# Title     : TODO
# Objective : TODO
# Created by: mattia
# Created on: 03/12/19

setwd("~/src/iof-tools/plotsGenerator/Rscripts/singleCSV")
csv1 <- read.csv("mrai", header = T)

summary(csv1)

csv2 <- read.csv("mrai2", header = T)

summary(csv2)