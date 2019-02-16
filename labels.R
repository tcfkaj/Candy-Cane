suppressMessages(library(tidyverse, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(forecast, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(imputeTS, quietly=TRUE, warn.conflicts=FALSE))

cc.data <- read.csv("../CANDY-CANE.csv")
colnames(cc.data) <- c("Type.Fac", "Name.Fac",
		  "Timestamp","Cas.A.Pr",
		  "Cas.B.Pr","Flow.Pr","Flow.Temp",
		  "Vol.Day","Tub.Pr")
names(cc.data)


##########################################################
############ Subset useful numeric variables ############
##########################################################

cc.data <- cc.data[11000:nrow(cc.data),]
cc.data <- cc.data %>%
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

#######################################
######## Practice test labels  ########
#######################################

# some_data <- c(0,0,0,3,4,5,8,9,7,8,5,3,3,2,2,0,1,3,5,6,6,6,4,3,2,2,3,3,4,5)
#
# print("Labeling data...")
# labs <- c()
# i = 1; j = length(some_data)
# iter=1
# threshold = 4
# while (i < j){
#         sub_data <- some_data[i:j]
#         print("Iteration, i=:")
#         print(i)
#         print(sub_data)
#         if (sub_data[1] < threshold){
# next_thr <- min(min(which(sub_data >= threshold),
#                     length(sub_data))
#                 if (0 %in% sub_data[1: (next_thr -1)]){
#                         labs <- c(labs, rep("HUM", next_thr -1))
#                 }
#                 else {
#                         labs <- c(labs, rep("DEF", next_thr -1))
#                 }
#         }
#         else {
# next_thr <- min(min(which(sub_data < threshold)),
#                 length(sub_data))
#                 labs <- c(labs, rep("REG", next_thr - 1))
#         }
#         i <- i + next_thr -1
#         iter <- iter+1
# }
#
# labs <- c(labs, labs[length(labs)])
#
# iter
# test_df <- data.frame(Val=some_data, Labs=labs)
# test_df

#######################################
########### The real labels ###########
#######################################

ptm <- proc.time()
print("Labeling data...")

some_data <- cc.data$Vol.Day
labs <- c()
i = 1; j = length(some_data)
iter=1
threshold = 4000

while (i < j){
	sub_data <- some_data[i:j]
	if (sub_data[1] < threshold){
		next_thr <- min(min(which(sub_data >= threshold)),
				length(sub_data))
		if (0 %in% sub_data[1: (next_thr -1)]){
			labs <- c(labs, rep("HUM", next_thr -1))
		}
		else {
			labs <- c(labs, rep("DEF", next_thr -1))
		}
	}
	else {
		next_thr <- min(min(which(sub_data < threshold)),
				length(sub_data))
		labs <- c(labs, rep("REG", next_thr - 1))
	}
	i <- i + next_thr -1
	iter <- iter+1
}

## There has to be a better way to do this, but
## having a hard time iterating to the last obs
labs <- c(labs, labs[length(labs)])
print("Iter: ")
iter
cc.data <- cc.data %>%
	mutate(Labs=labs)
head(cc.data)

proc.time() - ptm

#################################################################
################## Dynamic reg-based threshold ##################
#################################################################

ptm <- proc.time()
print("Labeling data...")

splitsAB <- 72000
splitsBC <- 185000

A <- suppressWarnings(lm(Vol.Day~time, data=cc.data[1:splitsAB,]))
B <- suppressWarnings(lm(Vol.Day~time,
			 data=cc.data[(splitsAB+1):splitsBC,]))
C <- suppressWarnings(lm(Vol.Day~time,
			 data=cc.data[(splitsBC+1):nrow(cc.data),]))

sectionA <- predict(A, interval="prediction", level=0.96)[,2]
sectionB <- predict(B, interval="prediction", level=0.96)[,2]
sectionC <- predict(C, interval="prediction", level=0.96)[,2]
threshold <- c(sectionA, sectionB, sectionC)

some_data <- cc.data$Vol.Day
labs <- c()
i = 1; j = length(some_data)
iter=1

while (i < j){
	sub_data <- some_data[i:j]
	if (sub_data[1] < threshold[i]){
		next_thr <- min(min(which(sub_data >= threshold[i])),
				length(sub_data))
		if (0 %in% sub_data[1: (next_thr -1)]){
			labs <- c(labs, rep("HUM", next_thr -1))
		}
		else {
			labs <- c(labs, rep("DEF", next_thr -1))
		}
	}
	else {
		next_thr <- min(min(which(sub_data < threshold[i])),
				length(sub_data))
		labs <- c(labs, rep("REG", next_thr - 1))
	}
	i <- i + next_thr -1
	iter <- iter+1
}

labs <- c(labs, labs[length(labs)])
print("Iter: ")
iter
cc.data <- cc.data %>%
	mutate(Labs=labs)
head(cc.data)

proc.time() - ptm





#########################################
############# Label next 24 #############
#########################################

##########################################################
############# This takes wayyyyyyyy too long #############
##########################################################

# print("Labeling next 24...")
# print("Rows before: ")
# nrow(cc.data)
#
# Next.24 <- c()
#
# for (i in 1:(nrow(cc.data) -1440)){
#         if ("DEF" %in% cc.data$Labs[i:i+1440]) {
#                 Next.24 <- c(Next.24, "DANGER")
#         }
#         else{
#                 Next.24 <- c(Next.24, "CLEAR")
#         }
# }
#
# Next.24 <- c(Next.24, rep(NA, 1440))
#
# cc.data <- cc.data %>%
#         mutate(Next.24=Next.24) %>%
#         na.omit()
# print("Rows after: ")
# nrow(cc.data)
#


########################################################
################### Best way (maybe) ###################
########################################################


ptm <- proc.time()

timeframe = 1440
labs.data = cc.data$Labs
length(labs.data)


next.24 <- labs.data[1:(length(labs.data)-timeframe)]
table(next.24)

## Step 1
next.24[which(next.24 != "DEF")] = "NOT"
table(next.24)

## Steps 2,3,4
runs <- rle(next.24 == "NOT")
# data.frame(runs$values, runs$lengths)

for  (x in 2:length(runs$values)){
	i <- sum(runs$lengths[1:(x-1)]) + 1
	j <- sum(runs$lengths[1:(x-1)]) + runs$lengths[x]

	if (runs$values[x] & runs$lengths[x] < timeframe){
		next.24[i:j]  <- "DEF"
	}
	if (runs$values[x] & runs$length[x] >= timeframe){
		next.24[(j-timeframe):j] <- "DEF"
	}
	#         print(table(next.24))
}


table(next.24)
proc.time() - ptm

cc.data2 <- cc.data[1:(nrow(cc.data)-1440),] %>%
	mutate(Next.24 = next.24)

head(cc.data2)


#################################
############# Graph #############
#################################


print("Graphing...")
ggplot(data=cc.data2, aes(x=time, y=Vol.Day, color=Next.24)) +
	geom_point() +
	geom_vline(xintercept=splitsAB) +
	geom_vline(xintercept=splitsBC) +
	geom_line(aes(y=threshold[1:nrow(cc.data2)],
		      color="threshold")) +
	ggtitle("Colored by whether there is a deferment or not in next 24")


ggplot(data=cc.data, aes(x=time, y=Vol.Day, color=Labs)) +
	geom_point() +
	geom_vline(xintercept=splitsAB) +
	geom_vline(xintercept=splitsBC) +
	geom_line(aes(y=threshold[1:nrow(cc.data)],
		      color="threshold")) +
	ggtitle("Colored based on present label")




#########################################################
############### Split HUM into sub-series ###############
#########################################################




print("Writing to csv...")
write.csv(cc.data2, file="../Next24.csv")
