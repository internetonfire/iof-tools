# set the environment
setwd("~/src/iof-tools/plotsGenerator/Rscripts/MultipleCSV")

library(dplyr)

folder1 <- '../../tmp/drive-download-20191229T142734Z-001/2019-12-23_4K-runs/RES-4K-30SEC/30SEC_CSV/'
folder2 <- '../../tmp/drive-download-20191229T142734Z-001/2019-12-23_4K-runs/RES-4K-DPC/DPC_CSV/'
#folder1 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-NOMRAI_CSV/'
#folder2 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-30SEC_CSV/'
#folder3 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-FABRIKANT_CSV/'
#folder4 <- '../../tmp/drive-download-20191229T142734Z-001_01/2019-12-24_fabrikant_16_nodes/RES-F16N/RES-F16N-DPC_CSV/'
#folder5 <- '../../BGPpysim/outNoMRAICSV'
#folder6 <- '../../BGPpysim/outConstFabrCSV'
#folder7 <- '../../BGPpysim/outConstInvFabrCSV'

fileList1 <- list.files(folder1,full.names = TRUE)
fileList2 <- list.files(folder2,full.names = TRUE)
#fileList3 <- list.files(folder3,full.names = TRUE)
#fileList4 <- list.files(folder4,full.names = TRUE)
#fileList5 <- list.files(folder5,full.names = TRUE)
#fileList6 <- list.files(folder6,full.names = TRUE)
#fileList7 <- list.files(folder7,full.names = TRUE)

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
sink("30Sec_nUpdates.txt")
print(summary(data1))
sink()
data2 <- listUpdtes(fileList2)
sink("DPC_nUpdates.txt")
print(summary(data2))
sink()
#data3 <- listUpdtes(fileList3)
#sink("InverseFabrikant_nUpdates.txt")
#print(summary(data3))
#sink()
#data4 <- listUpdtes(fileList4)
#sink("Heuristic_nUpdates.txt")
#print(summary(data4))
#sink()
#data5 <- listUpdtes(fileList5)
#sink("NoMRAI_nUpdates.txt")
#print(summary(data5))
#sink()
#data6 <- listUpdtes(fileList6)
#sink("constFabr_nUpdates.txt")
#print(summary(data6))
#sink()
#data7 <- listUpdtes(fileList7)
#sink("InvConstFabr_nUpdates.txt")
#print(summary(data7))
#sink()

#boxplot(data.frame(NoMRAI = data1, Fixed30Sec = data2, Fabrikant = data3, DPC = data4),
boxplot(data.frame(Fixed30Sec = data1, DPC = data2),
        main="Number of UPDATEs comparison",
        xlab="MRAI style",
        ylab="# Updates after break to achieve convergence",
        cex.lab = 1.35, cex.axis = 1.35, cex.main = 1.7)


data1 <- c()
for (file in fileList1) {
  csv_obj <- read.csv(file, header = T)
  data1 <- c(data1, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("fixed_30_sec.txt")
print(summary(data1))
sink()
data2 <- c()
for (file in fileList2) {
  csv_obj <- read.csv(file, header = T)
  data2 <- c(data2, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
}
sink("DPC.txt")
print(summary(data2))
sink()
#data3 <- c()
#for (file in fileList3) {
#  csv_obj <- read.csv(file, header = T)
#  data3 <- c(data3, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
#}
#sink("Fabrikant.txt")
#print(summary(data3))
#sink()
#data4 <- c()
#for (file in fileList4) {
#  csv_obj <- read.csv(file, header = T)
#  data4 <- c(data4, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
#}
#sink("DPC.txt")
#print(summary(data4))
#sink()
#data5 <- c()
#for (file in fileList5) {
#  csv_obj <- read.csv(file, header = T)
#  data5 <- c(data5, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
#}
#sink("NoMRAI_time.txt")
#print(summary(data5))
#sink()
#data6 <- c()
#for (file in fileList6) {
#  csv_obj <- read.csv(file, header = T)
#  data6 <- c(data6, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
#}
#sink("constFabr_mrai.txt")
#print(summary(data6))
#sink()
#data7 <- c()
#for (file in fileList7) {
#  csv_obj <- read.csv(file, header = T)
#  data7 <- c(data7, max(as.numeric(as.POSIXct(csv_obj$TIME))) - as.numeric(as.POSIXct(csv_obj[findReconfId(csv_obj), ]$TIME)))
#}
#sink("constInvFabr_time.txt")
#print(summary(data7))
#sink()

#boxplot(data.frame(NoMRAI = data1, Fixed30Sec = data2, Fabrikant = data3, DPC = data4),
boxplot(data.frame(Fixed30Sec = data1, DPC = data2),
        main="Convergence time",
        xlab="MRAI style",
        ylab="Convergence time in seconds",
        cex.lab = 1.35, cex.axis = 1.35, cex.main = 1.7)

