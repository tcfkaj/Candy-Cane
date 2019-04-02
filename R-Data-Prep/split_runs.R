suppressMessages(library(forecast, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(tidyverse, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(imputeTS, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(zoo, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(xts, quietly=TRUE, warn.conflicts=FALSE))

cc.data <- read.csv("../cc_data-chopped-start-here.csv", header=T)
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

threshold = Thresholds$pred.band4sd

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
buffer_0 = 720
buffer_1 = 0
size <- buffer_0 + buffer_1

runs <- rle(cc.data$Labs == "NOT")
indices <- cumsum(runs$lengths)
prosp <- which(runs$lengths>4000 & runs$values)
defs <- indices[prosperity+1]
nots <- indices[prosperity]+2000

prosp <- which(runs$lengths>6000 & runs$values)
nots <- c(nots,(indices[prosp]+4000))
prosp <- which(runs$lengths>8000 & runs$values)
nots <- c(nots,(indices[prosp]+6000))
prosp <- which(runs$lengths>10000 & runs$values)
nots <- c(nots,(indices[prosp]+8000))
prosp <- which(runs$lengths>12000 & runs$values)
nots <- c(nots,(indices[prosp]+10000))

vars <- c("Cas.A.Pr", "Flow.Pr", "Flow.Temp", "Vol.Day", "Tub.Pr")

for (i in vars){

}
data <- c(1:size)
length(tslen)
HUMANS <- which(runs$values)
ends = starts = c()
for (i in HUMANS){
	starts <- c(starts, (sum(runs$lengths[1:(i-1)])+1))
	ends <- c(ends, sum(runs$lengths[1:i]))

}

df <- data.frame(start=starts, end=ends)

for  (x in 1:length(runs$values)){
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




# ggplot(data=cc.data[106000:109000,], aes(x=c(106000:109000)))+
#         geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
#         geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
#         geom_line(aes(y=Vol.Day, color="Volume"))+
#         geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
#         labs(color="Legend") +
#         scale_colour_manual("",breaks = c("Casing A Pr",
#                                           "Flowline Pr",
#                                           "Flowline Temp",
#                                           "Volume",
#                                           "Tubing Pr"),
#                             values = c("darkgreen", "red",
#                                        "orange", "black",
#                                        "blue")) +
# ggtitle("Timestep= 105000 to 110000") + xlab("Timestep") + ylab("Levels") +
# theme(plot.title = element_text(lineheight=0.7, face="bold"))
# ggsave("jackedup1.png",width=10, height=6)
#
#
# ggplot(data=cc.data[106700:107500,], aes(x=c(106700:107500)))+
#         geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
#         geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
#         geom_line(aes(y=Vol.Day, color="Volume"))+
#         geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
#         labs(color="Legend") +
#         scale_colour_manual("",breaks = c("Casing A Pr",
#                                           "Flowline Pr",
#                                           "Flowline Temp",
#                                           "Volume",
#                                           "Tubing Pr"),
#                             values = c("darkgreen", "red",
#                                        "orange", "black",
#                                        "blue")) +
# ggtitle("Timestep= 106700 to 107500") + xlab("Timestep") + ylab("Levels") +
# theme(plot.title = element_text(lineheight=0.7, face="bold"))
# ggsave("jackedup1.png", width=10, height=6)
#
#
# ggplot(data=cc.data, aes(x=c(1:nrow(cc.data))))+
#         geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
#         geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
#         geom_line(aes(y=Vol.Day, color="Volume"))+
#         geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
#         labs(color="Legend") +
#         scale_colour_manual("",breaks = c("Casing A Pr",
#                                           "Flowline Pr",
#                                           "Flowline Temp",
#                                           "Volume",
#                                           "Tubing Pr"),
#                             values = c("darkgreen", "red",
#                                        "orange", "black",
#                                        "blue")) +
# ggtitle("Time= Whole Data Set") +  xlab("Timestep") + ylab("Levels") +
# theme(plot.title = element_text(lineheight=0.7, face="bold"))

# write.table(HUM_subs,
#             file="../HUM_subs.csv",
#             sep=",",
#             col.names=F,
#             row.names=F)

# Check out dist of REG's
# runs <- rle(cc.data$Labs)
# problems <- which(runs$values=="REG" & runs$lengths>3200)
# prob = minus1 = plus1 = ind =c()
# for (i in problems){
#         prob <- c(prob, runs$length[i])
#         minus1 <- c(minus1, runs$values[i-1])
#         plus1 <- c(plus1, runs$values[i+1])
#         ind <- c(ind, sum(runs$lengths[1:(i-1)]))
# }
#
# probDF <- data.frame(ind=ind, m1=minus1, prob=prob, p1=plus1)
# probDF[which(probDF$p1=="DEF"),]
#
# starting_points <- c()
# def_sp <- c()
#
# for (i in which(probDF$p1=="DEF")){
#         def_ind  <- probDF$ind[i] + probDF$prob[i]
#         reg_ind <- def_ind - 3000
#         def_sp <- c(def_sp, def_ind)
#         starting_points <- c(starting_points, reg_ind)
#         if (probDF$prob[i] > 15000){
#                 start_here  <- probDF$ind[i]
#                 starting_points <- c(starting_points, start_here+3000,
#                                      start_here+4500, start_here+6000,
#                                      start_here+7500, start_here+9000,
#                                      start_here+10500)
#         }
#         if (probDF$prob[i] < 15000 & probDF$prob[i] > 12000){
#                 start_here  <- probDF$ind[i]
#                 starting_points <- c(starting_points, start_here+3000,
#                                      start_here+4500, start_here+6000,
#                                      start_here+7500, start_here+9000)
#         }
#         if (probDF$prob[i] < 12000 & probDF$prob[i] > 9000){
#                 start_here  <- probDF$ind[i]
#                 starting_points <- c(starting_points, start_here+3000,
#                                      start_here+4500, start_here+6000)
#         }
#         if (probDF$prob[i] < 9000 & probDF$prob[i] > 6000){
#                 start_here  <- probDF$ind[i]
#                 starting_points <- c(starting_points, start_here+3000)
#         }
# }
#
# length(starting_points)
# length(def_sp)

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
