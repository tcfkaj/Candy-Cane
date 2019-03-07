suppressMessages(library(kernlab, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(MASS, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(forecast, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(tree, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(tidyverse, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(zoo, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(randomForest, quietly=TRUE, warn.conflicts=FALSE))
suppressMessages(library(data.table, quietly=TRUE, warn.conflicts=FALSE))

cc.data <- read.csv("../NAIVE.csv", header=T)

cc.data %>%
	sapply(function(x){sum(is.na(x))})
# which(is.na(cc.data$Vol.Day))
# dim(cc.data)
# glimpse(cc.data)

# dim(cc.data)
cc.data <- cc.data %>%
	na.omit()



## Find long runs of REG's
runs <- rle(cc.data$Next.24=="NOT")
# problems <- which(runs$values=="NOT")
# prob = plus1 = ind =c()
# minus1=c("start")
# for (i in problems){
#         prob <- c(prob, runs$length[i])
#         minus1 <- c(minus1, runs$values[i-1])
#         plus1 <- c(plus1, runs$values[i+1])
#         ind <- c(ind, (sum(runs$lengths[1:(i-1)])+1))
# }
#
# probDF <- data.frame(ind=ind, m1=minus1, prob=prob, p1=plus1)
# bins <- seq(1,40000, by=2500)

# df <- data.frame(lens = runs$lengths[which(runs$values)])
# ggplot(data=df, aes(x=lens)) +
#         geom_histogram(breaks=seq(1,40000,by=5000)) +
#         labs(title="Histogram of time between deferments", x="Time between deferments")
# ggsave(file="../HIST-BETWEEN.png", height=4, width=6)

# library(e1071)
#
# cc.data$Labs==NULL
#
# train <- c(1:250000)
# NBM <- naiveBayes(Next.24~., data=cc.data[train,])
# preds <- predict(NBM,cc.data[-train,], type="class")
# table(preds, cc.data$Next.24[-train])


## Naive approach

print("Looking back 24:")
cc.data$Pred <- shift(cc.data$Next.24, n=1440, type="lead")
cc.data <- cc.data %>%
	na.omit()

table(cc.data$Next.24, cc.data$Pred)



print("Looking back 1 minute:")
cc.data$Pred <- shift(cc.data$Labs, n=1, type="lead")
cc.data <- cc.data %>%
	na.omit() %>%
	mutate(Pred = ifelse(Pred=="REG", "NOT", "DEF"))

table(cc.data$Next.24, cc.data$Pred)





# ggplot(probDF, aes(x=prob)) +
#         geom_histogram(aes(y = ..density..), binwidth=10000) +
#         geom_density(aes(color="red"))
#
# probDF[which(probDF$p1=="DEF"),]

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
#
# starting_points <- c(starting_points, def_sp)
# starting_points <- starting_points+1
# starting_points
#
# levels(cc.data$Labs)
# simple.data <- cc.data[starting_points,] %>%
#         select(Labs, Cas.A.PrMA, Cas.A.PrSD, Cas.A.PrMAX, Cas.A.PrMIN,
#                Flow.PrMA, Flow.PrSD, Flow.PrMAX, Flow.PrMIN,
#                Tub.PrMA, Tub.PrSD)
# simple.data$Labs <- factor(as.character(simple.data$Labs))

# levels(cc.data$Labs)
# simple.data <- cc.data[starting_points,] %>%
#         select(Labs, Cas.A.PrMA, Cas.A.PrSD, Cas.A.PrMAX, Cas.A.PrMIN,
#                Flow.PrMA, Flow.PrSD, Flow.PrMAX, Flow.PrMIN,
#                Tub.PrMA, Tub.PrSD, Vol.DayMA, Vol.DayMIN, Vol.DaySD)
# simple.data$Labs <- factor(as.character(simple.data$Labs))



# levels(simple.data$Labs)
# simple.data$Labs

# save(simple.data, file="../Simple-Data-80obs.csv")


# print("Random Forest for Labels shifted 1440...")
# simple.RF <- randomForest(Labs~., data=simple.data, mtry=3, ntree=1000)
# simple.RF
# plot(simple.RF)
# varImpPlot(simple.RF)
# importance(simple.RF)


# print("LOOCV Logistic Regression for Labels shifted 1440...")
# probs = preds= c()
# for (i in 1:nrow(simple.data)){
#         glm.simple <- glm(Labs~., data=simple.data[-i,], family=binomial)
#         probs <- c(probs,predict(glm.simple, newdata=simple.data[i,]))
# }
# preds <- ifelse(probs>0.5,"REG", "DEF")
# confmat <- table(simple.data$Labs, preds)
# confmat
# print("Error: ")
# sum(confmat[1,2],confmat[2,1])/sum(confmat)

# simple.data <- simple.data %>%
#         mutate(Labs = ifelse(Labs=="REG", -1, 1))

# write.table(simple.data, "../svm-simple.csv", sep=",")
# source("~/Projects/ridge/ridge/klm.R")
#
# y <- simple.data %>%
#         select(Labs)
# y
# X <- simple.data %>%
#         select(-c(Labs))
# colnames(X)


# G <- kernelMatrix(X, kernel=rbfdot(sigma=1e-8))
# lambda = 1
#
# klm.simple <- cv.klm(G, y, lambda, cv="LOOCV")
# preds <- ifelse(klm.simple$preds<0, -1, 1)
#
# table(y, preds)
#
# gammas <- c(1e-9, 1e-10, 1e-20, 1e-8, 1e-7, 1e-6, 0.00001, 0.0001, 0.001, 0.01, 0.1, 5, 20, 100, 1000)


# ptm <- proc.time()
# best <- find_best_gamma(X,y, gammas, cv="LOOCV", scale=FALSE)
#
# best$train
# best$test
# best$best_mse
#
# print("Train perfs...")
# best$train_rse
#
# print("Test perfs...")
# best$test_rse
#
# print("Other stuff")
# best$best_rse
# best$test_sd
# best$best_gamma
# proc.time() - ptm
