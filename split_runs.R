
suppressMessages(library(tidyverse, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(forecast, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(imputeTS, quietly=TRUE, warn.conflicts=FALSE))

cc.data <- read.csv("../CANDY-CANE.csv")
colnames(cc.data) <- c("Type.Fac", "Name.Fac",
		  "Timestamp","Cas.A.Pr",
		  "Cas.B.Pr","Flow.Pr","Flow.Temp",
		  "Vol.Day","Tub.Pr")
names(cc.data)


#########################################################
############### Split HUM into sub-series ###############
#########################################################

runs <- rle(cc.data$Labs=="HUM")
size <- 30+60
HUM_subs <- c(1:size)
size

for (i in which(runs$values & runs$lengths > 29)){
	start_here <- sum(runs$lengths[1: (i-1)]) - 60
	indices <- c((start_here+1): (start_here + size))
	HUM_subs <- rbind(HUM_subs,cc.data$Vol.Day[indices])
}

dim(HUM_subs)
HUM_subs <- HUM_subs[1,]


