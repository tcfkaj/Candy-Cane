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
# runs <- rle(cc.data$Labs == "HUM")
# size <- buffer_0 + buffer_1
# HUM_subs <- c(1:size)
# length(HUM_subs)
#
# for  (x in 2:length(runs$values)){
#         if(runs$values[x]){
#                 i <- sum(runs$lengths[1:(x-1)]) + 1
#                 take <- cc.data$Vol.Day[(i-buffer_0):(i+buffer_1-1)]
#                 print(length(take))
#                 HUM_subs <- rbind(HUM_subs, take)
#         }
# }
#
# HUM_subs <- HUM_subs[-1,]
# dim(HUM_subs)
# typeof(HUM_subs)
#
# write.table(HUM_subs,
#             file="../HUM_subs.csv",
#             sep=",",
#             col.names=F,
#             row.names=F)


# Check out dist of REG's
runs <- rle(cc.data$Labs)
problems <- which(runs$values=="REG" & runs$lengths>3200)
prob = minus1 = plus1 = ind =c()
for (i in problems){
	prob <- c(prob, runs$length[i])
	minus1 <- c(minus1, runs$values[i-1])
	plus1 <- c(plus1, runs$values[i+1])
	ind <- c(ind, sum(runs$lengths[1:(i-1)]))
}

probDF <- data.frame(ind=ind, m1=minus1, prob=prob, p1=plus1)
probDF[which(probDF$p1=="DEF"),]

starting_points <- c()
def_sp <- c()

for (i in which(probDF$p1=="DEF")){
	def_ind  <- probDF$ind[i] + probDF$prob[i]
	reg_ind <- def_ind - 3000
	def_sp <- c(def_sp, def_ind)
	starting_points <- c(starting_points, reg_ind)
	if (probDF$prob[i] > 15000){
		start_here  <- probDF$ind[i]
		starting_points <- c(starting_points, start_here+3000,
				     start_here+4500, start_here+6000,
				     start_here+7500, start_here+9000,
				     start_here+10500)
	}
	if (probDF$prob[i] < 15000 & probDF$prob[i] > 12000){
		start_here  <- probDF$ind[i]
		starting_points <- c(starting_points, start_here+3000,
				     start_here+4500, start_here+6000,
				     start_here+7500, start_here+9000)
	}
	if (probDF$prob[i] < 12000 & probDF$prob[i] > 9000){
		start_here  <- probDF$ind[i]
		starting_points <- c(starting_points, start_here+3000,
				     start_here+4500, start_here+6000)
	}
	if (probDF$prob[i] < 9000 & probDF$prob[i] > 6000){
		start_here  <- probDF$ind[i]
		starting_points <- c(starting_points, start_here+3000)
	}
}

length(starting_points)
length(def_sp)

# hist(runs$lengths[runs$values== "HUM"], breaks=fifty)
# hist(runs$lengths[runs$values== "DEF"], breaks=fifty)
# hist(runs$lengths[runs$values== "HUM"], breaks=quarter)
# hist(runs$lengths[runs$values== "DEF"], breaks=quarter)

# cc.data$Vol.Day[14100:14500]



# ggplot(data=cc.data[69000:72500,], aes(x=c(69000:72500)))+
#         geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
#         geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
#         geom_line(aes(y=Flow.Temp, color="Flowline Temp"))+
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
