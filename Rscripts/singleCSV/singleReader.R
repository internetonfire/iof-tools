library(ggplot2)

# set the environment
setwd("~/src/iof-tools/Rscripts/singleCSV")

#File
file <- '../../BGPpysim/out2/bgpSim_test_49_15h39m21s_01-10-2019.csv'

#Functions
# Function to find the id of the line with type equals to RECONF
findReconfId <- function(csv_obj){
  typeColumn <- csv_obj$TYPE
  res <- match(c('RECONF'),typeColumn)
  return(res)
}

# Function to get only the subset with the UPDATE_TX type
onlyTypeCondition <- function(csv_obj, type){
  return(csv_obj[csv_obj$TYPE == type , ])
}

numberOfElements <- function(csv_obj){
  return(nrow(csv_obj))
}

maxAS <- function(csv_obj1, csv_obj2){
  max1 <- max(csv_obj1$AS)
  max2 <- max(csv_obj2$AS)
  return(max(max1, max2))
}

csv1 <- read.csv(file, header = T)

reconfId <- findReconfId(csv1)

beforeReconf <- head(csv1, reconfId-1)
afterReconf <- tail(csv1, nrow(csv1) - reconfId)

beforeReconf_tx <- onlyTypeCondition(beforeReconf, 'UPDATE_TX')
beforeReconf_rx <- onlyTypeCondition(beforeReconf, 'UPDATE_RX')
afterReconf_tx <- onlyTypeCondition(afterReconf, 'UPDATE_TX')
afterReconf_rx <- onlyTypeCondition(afterReconf, 'UPDATE_RX')

sprintf("Number of updates sent before RECONF: %i", numberOfElements(beforeReconf_tx))
sprintf("Number of updates sent after RECONF: %i", numberOfElements(afterReconf_tx))

numberOfAS <- maxAS(beforeReconf_tx, beforeReconf_rx)

print(beforeReconf$TIME[1])
print(beforeReconf$TIME[nrow(beforeReconf)])
timeDelta <- difftime(beforeReconf$TIME[1], beforeReconf$TIME[nrow(beforeReconf)])
print(abs(timeDelta))

op <- options(digits.secs=10)
ggplot(beforeReconf, aes(x=beforeReconf$TIME, y=beforeReconf$AS)) +
  geom_point(shape=1) + theme_classic() +
  labs(x = "Samples ids", y = "Value", 
       title = "Samples distribution") + 
  theme(plot.title = element_text(hjust = 0.5, size = 20), 
        axis.title.x = element_text(face="bold", size = 17),
        axis.title.y = element_text(face="bold", size = 17),
        axis.text = element_text(size = 14))