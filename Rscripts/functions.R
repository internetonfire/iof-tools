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