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

#####################################
########## Initial Boxplot ##########
#####################################

cc.data %>%
	select(-c(time)) %>%
	boxplot(main="Inital Boxplot")
box.data <- recordPlot()
dev.off()

#####################################################
############# Plot the initial Variables ############
#####################################################


plot.data <- ggplot(data=cc.data, aes(x=time))+
	geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
	geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
	geom_line(aes(y=Flow.Temp, color="Flowline Temp"))+
	geom_line(aes(y=Vol.Day, color="Volume"))+
	geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
	labs(color="Legend") +
	scale_colour_manual("",breaks = c("Casing A Pr",
					  "Flowline Pr",
					  "Flowline Temp",
					  "Volume",
					  "Tubing Pr"),
			    values = c("yellow", "red",
				       "orange", "black",
				       "blue")) +
ggtitle("Candy Cane Well") +
theme(plot.title = element_text(lineheight=0.7, face="bold"))

##########################################################
################# Differencing and Plot #################
##########################################################


cc.data <- cc.data %>%
	mutate_all(function(x){c(diff(x), NA)}) %>%
	mutate(time=c(1:length(Vol.Day))) %>%
	na.omit()


plot.data.DIFF <- ggplot(data=cc.data, aes(x=time))+
	geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
	geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
	geom_line(aes(y=Flow.Temp, color="Flowline Temp"))+
	geom_line(aes(y=Vol.Day, color="Volume"))+
	geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
	labs(color="Legend") +
	scale_colour_manual("",breaks = c("Casing A Pr",
					  "Flowline Pr",
					  "Flowline Temp",
					  "Volume",
					  "Tubing Pr"),
			    values = c("yellow", "red",
				       "orange", "black",
				       "blue")) +
ggtitle("Candy Cane Well- After differencing") +
theme(plot.title = element_text(lineheight=0.7, face="bold"))

print("After differencing:")
head(cc.data)
glimpse(cc.data)

cc.data %>%
	sapply(function(x){sum(is.na(x))})


cc.data %>%
	select(-c(time)) %>%
	boxplot(main="After differencing")
box.data.DIFF <- recordPlot()
dev.off()

########################################################
################# Normalize and Plot ###################
########################################################


cc.data <- cc.data %>%
	mutate_all(function(x){
			   ((x-min(x))/(max(x)-min(x))) %>%
			    as.vector()}) %>%
	mutate(time=c(1:length(Vol.Day)))


plot.data.DIFFNORM <- ggplot(data=cc.data, aes(x=time))+
	geom_line(aes(y=Cas.A.Pr, color="Casing A Pr"))+
	geom_line(aes(y=Flow.Pr, color="Flowline Pr"))+
	geom_line(aes(y=Flow.Temp, color="Flowline Temp"))+
	geom_line(aes(y=Vol.Day, color="Volume"))+
	geom_line(aes(y=Tub.Pr, color="Tubing Pr"))+
	labs(color="Legend") +
	scale_colour_manual("",breaks = c("Casing A Pr",
					  "Flowline Pr",
					  "Flowline Temp",
					  "Volume",
					  "Tubing Pr"),
			    values = c("yellow", "red",
				       "orange", "black",
				       "blue")) +
ggtitle("Candy Cane Well- After differencing and normalizing") +
theme(plot.title = element_text(lineheight=0.7, face="bold"))


print("Differencing and normalizing:")
head(cc.data)
glimpse(cc.data)

cc.data %>%
	sapply(function(x){sum(is.na(x))})

cc.data %>%
	select(-c(time)) %>%
	boxplot(main="After differencing and normalizing")
box.data.DIFFNORM <- recordPlot()
dev.off()

####################################
########## Print graphics ##########
####################################

print("Rendering graphics...")
plot(plot.data)
# box.data
plot(plot.data.DIFF)
# box.data.DIFF
plot(plot.data.DIFFNORM)
# box.data.DIFFNORM


#############################################
############# Save R objects  ###############
#############################################

print("Saving objects...")
save(cc.data, box.data, box.data.DIFF,
     box.data.DIFFNORM, plot.data,
     plot.data.DIFF, plot.data.DIFFNORM,
     file="data_prep.rda")


####################################
########### Write to csv ###########
####################################

print("Writing to csv...")
write.csv(cc.data, file="after_data_prep.csv")

