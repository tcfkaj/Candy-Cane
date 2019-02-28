suppressMessages(library(forecast, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(tidyverse, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(imputeTS, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(zoo, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(xts, quietly=TRUE, warn.conflicts=FALSE))

cc.data <- read.csv("../cc_data_band_timed_234sd_7K_2.csv", header=T)
Thresholds <- cc.data[, c("km.cls", "pred.exp", "pred.band", "pred.band3sd", "pred.band4sd")]
TS <- cc.data$Timestamp
cc.data <- cc.data[, c("Cas.A.Pr", "Flow.Pr", "Flow.Temp", "Vol.Day", "Tub.Pr")]

names(cc.data)
names(Thresholds)
names(TS)

glimpse(cc.data)
glimpse(Thresholds)
glimpse(TS)


######################
### Now count NA's ###
######################

cc.data %>%
	sapply(function(x){sum(is.na(x))})
which(is.na(cc.data$Vol.Day))

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

# ptm <- proc.time()
# print("Labeling data...")
#
# some_data <- cc.data$Vol.Day
# labs <- c()
# i = 1; j = length(some_data)
# iter=1
# threshold = 4000
#
# while (i < j){
#         sub_data <- some_data[i:j]
#         if (sub_data[1] < threshold){
#                 next_thr <- min(min(which(sub_data >= threshold)),
#                                 length(sub_data))
#                 if (0 %in% sub_data[1: (next_thr -1)]){
#                         labs <- c(labs, rep("HUM", next_thr -1))
#                 }
#                 else {
#                         labs <- c(labs, rep("DEF", next_thr -1))
#                 }
#         }
#         else {
#                 next_thr <- min(min(which(sub_data < threshold)),
#                                 length(sub_data))
#                 labs <- c(labs, rep("REG", next_thr - 1))
#         }
#         i <- i + next_thr -1
#         iter <- iter+1
# }

## There has to be a better way to do this, but
## having a hard time iterating to the last obs
# labs <- c(labs, labs[length(labs)])
# print("Iter: ")
# iter
# cc.data <- cc.data %>%
#         mutate(Labs=labs)
# head(cc.data)
#
# proc.time() - ptm

#################################################################
################## Dynamic reg-based threshold ##################
#################################################################

ptm <- proc.time()
print("Labeling data...")

# splitsAB <- 72000
# splitsBC <- 185000
#
# A <- suppressWarnings(lm(Vol.Day~time, data=cc.data[1:splitsAB,]))
# B <- suppressWarnings(lm(Vol.Day~time,
#                          data=cc.data[(splitsAB+1):splitsBC,]))
# C <- suppressWarnings(lm(Vol.Day~time,
#                          data=cc.data[(splitsBC+1):nrow(cc.data),]))
#
# sectionA <- predict(A, interval="prediction", level=0.96)[,2]
# sectionB <- predict(B, interval="prediction", level=0.96)[,2]
# sectionC <- predict(C, interval="prediction", level=0.96)[,2]
# threshold <- c(sectionA, sectionB, sectionC)


threshold = Thresholds$pred.band

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


#############################################
############ Break up deferments ############
#############################################

## Define buffers around first deferment point
buffer_0 = 60
buffer_1 = 60


# HUM
runs <- rle(cc.data$Labs == "HUM")
size <- buffer_0 + buffer_1
HUM_subs <- c(1:size)
length(HUM_subs)

for  (x in 2:length(runs$values)){
	if(runs$values[x]){
		i <- sum(runs$lengths[1:(x-1)]) + 1
		take <- cc.data$Vol.Day[(i-buffer_0):(i+buffer_1-1)]
		print(length(take))
		HUM_subs <- rbind(HUM_subs, take)
	}
}

HUM_subs <- HUM_subs[-1,]
dim(HUM_subs)
typeof(HUM_subs)

write.table(HUM_subs,
	    file="../HUM_subs.csv",
	    sep=",",
	    col.names=F,
	    row.names=F)







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
slight_lag = 3

next.24 <- labs.data[slight_lag:(length(labs.data)-timeframe)]
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

cc.data <- cc.data[1:(nrow(cc.data)-1439-slight_lag),] %>%
	mutate(Next.24 = next.24)

head(cc.data)


#################################
############# Graph #############
#################################


print("Graphing...")
ggplot(data=cc.data, aes(x=time, y=Vol.Day, color=Next.24)) +
	geom_point() +
	geom_vline(xintercept=splitsAB) +
	geom_vline(xintercept=splitsBC) +
	geom_line(aes(y=threshold[1:nrow(cc.data)],
		      color="threshold")) +
ggtitle("Colored by whether there is a deferment or not in next 24")


ggplot(data=cc.data, aes(x=time, y=Vol.Day, color=Labs)) +
	geom_point() +
	geom_vline(xintercept=splitsAB) +
	geom_vline(xintercept=splitsBC) +
	geom_line(aes(y=threshold[1:nrow(cc.data)],
		      color="threshold")) +
ggtitle("Colored based on present label")


#################################################
############# Detrend with line fit #############
#################################################

## Vol.Day
model <- lm(Vol.Day^2~time, data=cc.data)
fit <- sqrt(fitted(model))

# ggplot(data=cc.data, aes(x=time, y=Vol.Day, color="Vol.Day")) +
#         geom_point() +
#         geom_line(aes(y=fit, color="Fit")) +
#         ggtitle("Vol.Day^2")

cc.data$Vol.Day <- cc.data$Vol.Day - fit
# ggplot(data=cc.data, aes(x=time, y=Vol.Day, color="Vol.Day")) +
#         geom_point() +
#         ggtitle("Vol.Day Detrended")

## Cas.A.Pr
model <- lm(log(Cas.A.Pr)~time, data=cc.data)
fit <- exp(fitted(model))

# ggplot(data=cc.data, aes(x=time, y=Cas.A.Pr, color="Cas.A.Pr")) +
#         geom_point() +
#         geom_line(aes(y=fit, color="Fit")) +
#         ggtitle("log(Cas.A.Pr)")

cc.data$Cas.A.Pr <- cc.data$Cas.A.Pr - fit
# ggplot(data=cc.data, aes(x=time, y=Cas.A.Pr, color="Cas.A.Pr")) +
#         geom_point() +
#         ggtitle("Cas.A.Pr Detrended")

## Flow.Pr
model <- lm(Flow.Pr^2~time, data=cc.data)
fit <- sqrt(fitted(model))

cc.data$Flow.Pr <- cc.data$Flow.Pr - fit
# ggplot(data=cc.data, aes(x=time, y=Flow.Pr, color="Flow.Pr")) +
#         geom_point() +
#         ggtitle("Flow.Pr Detrended")

## Flow.Temp
model <- lm(Flow.Temp~time, data=cc.data)
fit <- fitted(model)

# ggplot(data=cc.data, aes(x=time, y=Flow.Temp, color="Flow.Temp")) +
#         geom_point() +
#         geom_line(aes(y=fit, color="Fit")) +
#         ggtitle("Flow.Temp")


cc.data$Flow.Temp <- cc.data$Flow.Temp - fit
# ggplot(data=cc.data, aes(x=time, y=Flow.Temp, color="Flow.Temp")) +
#         geom_point() +
#         ggtitle("Flow.Temp Detrended")

## Tub.Pr
model <- lm(Tub.Pr~time, data=cc.data)
fit <- fitted(model)

# ggplot(data=cc.data, aes(x=time, y=Tub.Pr, color="Tub.Pr")) +
#         geom_point() +
#         geom_line(aes(y=fit, color="Fit")) +
#         ggtitle("Tub.Pr")

cc.data$Tub.Pr <- cc.data$Tub.Pr - fit
# ggplot(data=cc.data, aes(x=time, y=Tub.Pr, color="Tub.Pr")) +
#         geom_point() +
#         geom_line(aes(y=fit, color="Fit")) +
#         ggtitle("Tub.Pr Detrended")


r = 30
place.time <- cc.data$time[1:(nrow(cc.data)-r+1)]
place.Next <- cc.data$Next.24[r:nrow(cc.data)]
glimpse(cc.data[,!(names(cc.data) %in% c("time", "Labs", "Next.24"))])

cc.data <- cc.data[,!(names(cc.data) %in% c("time", "Labs", "Next.24"))] %>%
	mutate_all(function(x) rollmeanr(x,r, na.pad=TRUE)) %>%
	na.omit() %>%
	mutate(time=place.time, Next.24=place.Next)
head(cc.data)

# ggplot(data=cc.data, aes(x=time))+
#         geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
#         geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
#         geom_line(aes(y=Flow.Temp, color="Flowline Temp"))+
#         geom_line(aes(y=Vol.Day, color="Volume"))+
#         geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
#         labs(color="Legend") +
#         scale_colour_manual("",breaks = c("Casing A Pr",
#                                           "Flowline Pr",
#                                           "Flowline Temp",
#                                           "Volume",
#                                           "Tubing Pr"),
#                             values = c("yellow", "red",
#                                        "orange", "black",
#                                        "blue")) +
# ggtitle("Candy Cane Well- After detrend and MA-30 Filter") +
# theme(plot.title = element_text(lineheight=0.7, face="bold"))


place.time <- cc.data$time
place.Next <- cc.data$Next.24
cc.data <- cc.data[,!(names(cc.data) %in% c("time", "Next.24"))] %>%
	mutate_all(function(x){(x - min(x))/(max(x)-min(x))}) %>%
	mutate(time=place.time, Next.24=place.Next)

head(cc.data)

# ggplot(data=cc.data, aes(x=time))+
#         geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
#         geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
#         geom_line(aes(y=Flow.Temp, color="Flowline Temp"))+
#         geom_line(aes(y=Vol.Day, color="Volume"))+
#         geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
#         labs(color="Legend") +
#         scale_colour_manual("",breaks = c("Casing A Pr",
#                                           "Flowline Pr",
#                                           "Flowline Temp",
#                                           "Volume",
#                                           "Tubing Pr"),
#                             values = c("yellow", "red",
#                                        "orange", "black",
#                                        "blue")) +
# ggtitle("Candy Cane Well- After detrend, filter and normalize.") +
# theme(plot.title = element_text(lineheight=0.7, face="bold"))


# print("Writing to csv...")
# write.csv(cc.data, file="../RNN-ready-DT-MA30-NORM.csv")
