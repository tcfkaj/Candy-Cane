suppressMessages(library(forecast, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(tree, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(tidyverse, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(zoo, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(randomForest, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(data.table, quietly=TRUE, warn.conflicts=FALSE))

cc.data <- read.csv("../Rolled-and-Labeled.csv", header=T)

cc.data %>%
	sapply(function(x){sum(is.na(x))})
# which(is.na(cc.data$Vol.Day))

# dim(cc.data)
cc.data <- cc.data %>%
	na.omit()
# dim(cc.data)

# glimpse(cc.data)


cc.data$Labs <- shift(cc.data$Labs, n=1440, type="lead", fill=NA)
head(cc.data)
cc.data <- cc.data %>%
	na.omit()

## Find long runs of REG's
runs <- rle(as.character(cc.data$Labs))
problems <- which(runs$values=="REG" & runs$lengths>3200)
prob = minus1 = plus1 = ind =c()
for (i in problems){
	prob <- c(prob, runs$length[i])
	minus1 <- c(minus1, runs$values[i-1])
	plus1 <- c(plus1, runs$values[i+1])
	ind <- c(ind, sum(runs$lengths[1:(i-1)]))
}

probDF <- data.frame(ind=ind, m1=minus1, prob=prob, p1=plus1)
# probDF[which(probDF$p1=="DEF"),]

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


problems <- which(runs$values=="REG" & runs$lengths<3200)
prob =  plus1 = ind =c()
minus1 <- c("start")
for (i in problems){
	prob <- c(prob, runs$length[i])
	minus1 <- c(minus1, runs$values[i-1])
	plus1 <- c(plus1, runs$values[i+1])
	ind <- c(ind, sum(runs$lengths[1:(i-1)]))
}

probDF <- data.frame(ind=ind, m1=minus1, prob=prob, p1=plus1)
probDF[which(probDF$p1=="DEF"),]

for (i in which(probDF$p1=="DEF")){
	if (probDF$prob > 1500){
		def_ind  <- probDF$ind[i] + probDF$prob[i]
		def_sp <- c(def_sp, def_ind)
	}
}

starting_points <- c(starting_points, def_sp)
starting_points <- starting_points+1
length(starting_points)

levels(cc.data$Labs)
simple.data <- cc.data[starting_points,] %>%
	select(Labs, Cas.A.PrMA, Cas.A.PrSD, Cas.A.PrMAX, Cas.A.PrMIN,
	       Flow.PrMA, Flow.PrSD, Flow.PrMAX, Flow.PrMIN,
	       Tub.PrMA, Tub.PrSD, Tub.PrMAX, Tub.PrMIN)
simple.data$Labs <- factor(as.character(simple.data$Labs))
# levels(simple.data$Labs)
# simple.data$Labs

# save(simple.data, file="../Simple-Data-80obs.csv")


print("Random Forest for Labels shifted 1440...")
simple.RF <- randomForest(Labs~., data=simple.data, mtry=4, ntree=1000)
simple.RF
plot(simple.RF)
varImpPlot(simple.RF)
importance(simple.RF)


print("LOOCV Logistic Regression for Labels shifted 1440...")
probs = preds= c()
for (i in 1:nrow(simple.data)){
	glm.simple <- glm(Labs~., data=simple.data[-i,], family=binomial)
	probs <- c(probs,predict(glm.simple, newdata=simple.data[i,]))
}
preds <- ifelse(probs>0.5,"NOT", "DEF")
confmat <- table(simple.data$Labs, preds)
confmat
print("Error: ")
sum(confmat[1,2],confmat[2,1])/sum(confmat)

