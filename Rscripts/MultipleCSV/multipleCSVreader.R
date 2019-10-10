# set the environment
setwd("~/src/iof-tools/Rscripts/MultipleCSV")

library(dplyr)

folder1 <- '../../BGPpysim/out/mrai30secCSV'
folder2 <- '../../BGPpysim/out/mraiFabrikantCSV'
folder3 <- '../../BGPpysim/out/mraiInverseFabrikantCSV'
folder4 <- '../../BGPpysim/out/mraiSimpleHeuristicCSV'
folder5 <- '../../BGPpysim/out/nomraiCSV'

fileList1 <- list.files(folder1,full.names = TRUE)
fileList2 <- list.files(folder2,full.names = TRUE)
fileList3 <- list.files(folder3,full.names = TRUE)
fileList4 <- list.files(folder4,full.names = TRUE)
fileList5 <- list.files(folder5,full.names = TRUE)

#Functions
# Function to find the id of the line with type equals to RECONF
findReconfId <- function(csv_obj){
  typeColumn <- csv_obj$TYPE
  res <- match(c('RECONF'),typeColumn)
  return(res)
}

findReconfTime <- function(csv_obj){
  typeColumn <- csv1$TYPE
  res <- match(c('RECONF'),typeColumn)
  return(csv1[res,3])
}

# Function to get only the subset with the UPDATE_TX type
onlyTypeCondition <- function(csv_obj, type){
  return(csv_obj[csv_obj$TYPE == type , ])
}

numberOfElements <- function(csv_obj){
  return(nrow(csv_obj))
}

MaxAS <- function(csv_obj){
  return(max(csv_obj$AS))
}

maxAS <- function(csv_obj1, csv_obj2){
  max1 <- max(csv_obj1$AS)
  max2 <- max(csv_obj2$AS)
  return(max(max1, max2))
}

listUpdtes <- function(fileList) {
  listNumberOfUpdatesAfter <- c()
  
  for (file in fileList){
    csv1 <- read.csv(file, header = T)
    
    reconfId <- findReconfId(csv1)
    
    beforeReconf <- head(csv1, reconfId-1)
    afterReconf <- tail(csv1, nrow(csv1) - reconfId)
    
    beforeReconf_tx <- onlyTypeCondition(beforeReconf, 'UPDATE_TX')
    beforeReconf_rx <- onlyTypeCondition(beforeReconf, 'UPDATE_RX')
    afterReconf_tx <- onlyTypeCondition(afterReconf, 'UPDATE_TX')
    afterReconf_rx <- onlyTypeCondition(afterReconf, 'UPDATE_RX')
    
    listNumberOfUpdatesAfter <- c(listNumberOfUpdatesAfter, numberOfElements(afterReconf_tx))
  }  
  return(listNumberOfUpdatesAfter)
}

maxTime <- function(object){
  return(max(as.numeric(as.POSIXct(afterReconf_rx_time_as$TIME))))
}

objectFromCSVFile <- function(file){
  return(read.csv(file, header = T))
}

listTimes <- function(fileList) {
  listNumberOfUpdatesAfter <- c()
  
  for (file in fileList){
    csv1 <- read.csv(file, header = T)
    
    reconfId <- findReconfId(csv1)
    
    beforeReconf <- head(csv1, reconfId-1)
    afterReconf <- tail(csv1, nrow(csv1) - reconfId)
    
    beforeReconf_tx <- onlyTypeCondition(beforeReconf, 'UPDATE_TX')
    beforeReconf_rx <- onlyTypeCondition(beforeReconf, 'UPDATE_RX')
    afterReconf_tx <- onlyTypeCondition(afterReconf, 'UPDATE_TX')
    afterReconf_rx <- onlyTypeCondition(afterReconf, 'UPDATE_RX')
    
    listNumberOfUpdatesAfter <- c(listNumberOfUpdatesAfter, max(as.numeric(as.POSIXct(afterReconf_rx$TIME))) - as.numeric(as.POSIXct(findReconfTime(csv1))))
  }  
  return(listNumberOfUpdatesAfter)
}

data1 <- listUpdtes(fileList1)
sink("30SecFixed_nUpdates.txt")
print(summary(data1))
sink()
data2 <- listUpdtes(fileList2)
sink("Fabrikant_nUpdates.txt")
print(summary(data2))
sink()
data3 <- listUpdtes(fileList3)
sink("InverseFabrikant_nUpdates.txt")
print(summary(data3))
sink()
data4 <- listUpdtes(fileList4)
sink("Heuristic_nUpdates.txt")
print(summary(data4))
sink()
data5 <- listUpdtes(fileList5)
sink("NoMRAI_nUpdates.txt")
print(summary(data5))
sink()

boxplot(data.frame(fixed30sec = data1, Fabrikant = data2, ReverseFabrikant = data3, SimpleHeuristic = data4, NoMRAI = data5),
        main="Different boxplots for each MRAI style",
        sub="(50 simulations, graph based on Fig 1 Fabrikant paper)",
        xlab="MRAI style",
        ylab="# Updates after break to achieve convergence")

data1 <- c()
for (file in fileList1) {
  csv_obj <- read.csv(file, header = T)
  data1 <- c(data1, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("30SecFixed_time.txt")
print(summary(data1))
sink()
data2 <- c()
for (file in fileList2) {
  csv_obj <- read.csv(file, header = T)
  data2 <- c(data2, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("Fabrikant_time.txt")
print(summary(data2))
sink()
data3 <- c()
for (file in fileList3) {
  csv_obj <- read.csv(file, header = T)
  data3 <- c(data3, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("InversedFabrikant_time.txt")
print(summary(data3))
sink()
data4 <- c()
for (file in fileList4) {
  csv_obj <- read.csv(file, header = T)
  data4 <- c(data4, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("SimpleHeuristic_time.txt")
print(summary(data4))
sink()
data5 <- c()
for (file in fileList5) {
  csv_obj <- read.csv(file, header = T)
  data5 <- c(data5, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("NoMRAI_time.txt")
print(summary(data5))
sink()

boxplot(data.frame(fixed30sec = data1, Fabrikant = data2, ReverseFabrikant = data3, SimpleHeuristic = data4, NoMRAI = data5),
        main="Convergence time BoxPlot",
        sub="(50 simulations, graph based on Fig 1 Fabrikant paper)",
        xlab="MRAI style",
        ylab="Convergence time in seconds")
