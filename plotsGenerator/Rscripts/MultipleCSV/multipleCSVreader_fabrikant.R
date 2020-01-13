# set the environment
setwd("~/src/iof-tools/plotsGenerator/Rscripts/MultipleCSV")

library(dplyr)

args <- commandArgs(trailingOnly = TRUE)

folder1 <- args[1]
folder2 <- args[2]
folder3 <- args[3]
folder4 <- args[4]

#folder1 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-NOMRAI_CSV/'
#folder2 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-30SEC_CSV/'
#folder3 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-FABRIKANT_CSV/'
#folder4 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-DPC_CSV/'

fileList1 <- list.files(folder1,full.names = TRUE)
fileList2 <- list.files(folder2,full.names = TRUE)
fileList3 <- list.files(folder3,full.names = TRUE)
fileList4 <- list.files(folder4,full.names = TRUE)

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
sink("input1_nUpdates.txt")
print(summary(data1))
sink()
data2 <- listUpdtes(fileList2)
sink("input2_nUpdates.txt")
print(summary(data2))
sink()
data3 <- listUpdtes(fileList3)
sink("input3_nUpdates.txt")
print(summary(data3))
sink()
data4 <- listUpdtes(fileList4)
sink("input4_nUpdates.txt")
print(summary(data4))
sink()

boxplot(data.frame(NoMRAI = data1, Fixed30Sec = data2, Fabrikant = data3, DPC = data4),
        main="Number of UPDATEs comparison",
        xlab="MRAI style",
        ylab="# Updates after break to achieve convergence",
        cex.lab = 1.35, cex.axis = 1.35, cex.main = 1.7)


data1 <- c()
for (file in fileList1) {
  csv_obj <- read.csv(file, header = T)
  data1 <- c(data1, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("input1_time.txt")
print(summary(data1))
sink()
data2 <- c()
for (file in fileList2) {
  csv_obj <- read.csv(file, header = T)
  data2 <- c(data2, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("input2_time.txt")
print(summary(data2))
sink()
data3 <- c()
for (file in fileList3) {
  csv_obj <- read.csv(file, header = T)
  data3 <- c(data3, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("input3_time.txt")
print(summary(data3))
sink()
data4 <- c()
for (file in fileList4) {
  csv_obj <- read.csv(file, header = T)
  data4 <- c(data4, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("input4_time.txt")
print(summary(data4))
sink()

boxplot(data.frame(NoMRAI = data1, Fixed30Sec = data2, Fabrikant = data3, DPC = data4),
        main="Convergence time",
        xlab="MRAI style",
        ylab="Convergence time in seconds",
        cex.lab = 1.35, cex.axis = 1.35, cex.main = 1.7)

