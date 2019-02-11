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
######## Generate test labels  ########
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
#                 next_thr <- min(min(which(sub_data >= threshold)),length(sub_data))
#                 if (0 %in% sub_data[1: (next_thr -1)]){
#                         labs <- c(labs, rep("HUM", next_thr -1))
#                 }
#                 else {
#                         labs <- c(labs, rep("DEF", next_thr -1))
#                 }
#         }
#         else {
#                 next_thr <- min(min(which(sub_data < threshold)),length(sub_data))
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
	print("Iteration, i=:")
	print(i)
	if (sub_data[1] < threshold){
		next_thr <- min(min(which(sub_data >= threshold)),length(sub_data))
		if (0 %in% sub_data[1: (next_thr -1)]){
			labs <- c(labs, rep("HUM", next_thr -1))
		}
		else {
			labs <- c(labs, rep("DEF", next_thr -1))
		}
	}
	else {
		next_thr <- min(min(which(sub_data < threshold)),length(sub_data))
		labs <- c(labs, rep("REG", next_thr - 1))
	}
	i <- i + next_thr -1
	iter <- iter+1
}

## There has to be a better way to do this, but
## having a hard time iterating to the last obs
labs <- c(labs, labs[length(labs)])

iter
cc.data <- cc.data %>%
	mutate(Labs=labs)
head(cc.data)

proc.time() - ptm

#################################
############# Graph #############
#################################
 print("Graphing...")
ggplot(data=cc.data, aes(x=time, y=Vol.Day, color=Labs)) +
	geom_point()


print("Writing to csv...")
write.csv(cc.data, file="../labeled_data.csv")
