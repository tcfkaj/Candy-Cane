library(imputeTS, quietly=TRUE, warn.conflicts=FALSE)
library(tidyverse, quietly=TRUE, warn.conflicts=FALSE)
library(forecast, quietly=TRUE, warn.conflicts=FALSE)

cc <- read.csv("CANDY-CANE.csv", header=T)
colnames(cc) <- c("Type.Fac", "Name.Fac",
		  "Timestamp","Cas.A.Pr",
		  "Cas.B.Pr","Flow.Pr","Flow.Temp",
		  "Vol.Day","Tub.Pr")



##########################################################
############ Subset useful numeric variables ############
##########################################################

cc.data <- cc %>%
	select(Cas.A.Pr,Flow.Pr,
	       Flow.Temp,Vol.Day,Tub.Pr)
cc.data$time <- c(1:length(cc.data$Vol.Day))
colnames(cc.data)
head(cc.data)

######################################################################
############ Check the variable types and turn to numeric ############
######################################################################

glimpse(cc.data)
cc.data <- cc.data %>%
	mutate_all(function(x) as.numeric(as.character(x)))
glimpse(cc.data)

######################
### Now count NA's ###
######################

cc.data %>%
	sapply(function(x){sum(is.na(x))})
which(is.na(cc.data$Vol.Day))

### What's happening around these NA's?
# cc.data$Vol.Day[244190:244270]
# cc.data$Cas.A.Pr[244190:244270]
# cc.data$Flow.Pr[244190:244270]
# cc.data$Flow.Temp[244190:244270]
# cc.data$Tub.Pr[244190:244270]

################################
######### Fill in NA's #########
################################

print("Initial look:")

cc.data <- cc.data %>%
	mutate_all(na.locf) %>%
	as.data.frame()
cc.data %>%
	sapply(function(x){sum(is.na(x))})
glimpse(cc.data)

#########################################################
########### Categorize each point by whether  ###########
########### deferment occurs in next 24 hours ###########
#########################################################

threshold = 3500
def.next24 <- c()
for (i in 1:(length(cc.data$Vol.Day)-2880)){
	test <- min(cc.data$Vol.Day[i+1441:i+2880])
	if (test < threshold & test > 0){
		def.next24 <- c(def.next24, "DEFR")
	}
	if (test < threshold & test !> 0){
		def.next24 <- c(def.next24, "HUMN")
	}
	else{
		def.next24 <- c(def.next24, "NRML")
	}
}

## Some variables

## Diff by
for (i in 20000:(length(cc.data$Vol.Day)-1440)){


}


