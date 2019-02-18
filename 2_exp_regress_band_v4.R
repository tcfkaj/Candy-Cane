cc.data <- read.csv("cc_data_km_cls.csv", row.names = 1)
# See 1_kmeans_clustering_v1.R for the dataset.

# Regression for each clusters.

# Class 1: blue
cc.cls.1 <- cc.data[which(cc.data$km.cls==1), ]

# chop out the begining of production.
begin_limit <- mean(cc.cls.1$Vol.Day) - 2*sd(cc.cls.1$Vol.Day)
res <- c()
for (i in 1:10000){
  if (cc.cls.1$Vol.Day[i] >= begin_limit){
    res <- c(res, i)
  }
}
# head(res, 100)
start <- 1546  # gap
# end chop
cls.row <- as.numeric(row.names(cc.cls.1))
for (i in 1:nrow(cc.cls.1)){
  if (cls.row[i] >= 2e5){
    end <- i - 1
    break
  }
}
cls.1 <- cc.cls.1[start:end, ]
# plot(cc.cls.1$time, cc.cls.1$Vol.Day)
# points(cls.1$time, cls.1$Vol.Day, col="red")

# New chop for cls 1===============================
# for (i in 1:nrow(cc.cls.1)){
#   if (cc.cls.1$Vol.Day[i] >= 9000){
#     start.new <- i
#     break
#   }
# }
# 
# for (i in 1:nrow(cc.cls.1)){
#   if (cls.row[i] >= 67410){
#     end.new <- i - 1
#     break
#   }
# }
# cls.1 <- cc.cls.1[start.new:end.new, ]

# Linear
# lr.1 <- lm((Vol.Day) ~ time, data = cls.1[, -c(7)])
# plot(cc.cls.1$time, cc.cls.1$Vol.Day)
# lines(cls.1$time, lr.1$fitted.values, col="blue")

# Class 2: purple
cc.cls.2 <- cc.data[which(cc.data$km.cls==2), ]

# end chop
cls.row2 <- as.numeric(row.names(cc.cls.2))
for (i in 1:nrow(cc.cls.2)){
  if (cc.cls.2$time[i] >= 250000){
    end2 <- i - 1
    break
  }
}
cc.cls.2[(end2-2):(end2+2), ]  # check gap
cls.2 <- cc.cls.2[1:end2, ]
# plot(cc.cls.2$time, cc.cls.2$Vol.Day)
# points(cls.2$time, cls.2$Vol.Day, col="red")

# Linear
# lr.2 <- lm((Vol.Day) ~ time, data = cc.cls.2[, -c(7)])
# plot(cc.cls.2$time, cc.cls.2$Vol.Day)
# lines(cc.cls.2$time, lr.2$fitted.values, col="blue")

# Class 3: red
cc.cls.3 <- cc.data[which(cc.data$km.cls==3), ]

# start chop
cls.row3 <- as.numeric(row.names(cc.cls.3))
start3 <- 64  # by checking gap
cls.3 <- cc.cls.3[start3:nrow(cc.cls.3), ]
# plot(cc.cls.3$time, cc.cls.3$Vol.Day)
# points(cls.3$time, cls.3$Vol.Day, col="red")

# Linear
# lr.3 <- lm((Vol.Day) ~ time, data = cc.cls.3[, -c(7)])
# plot(cc.cls.3$Vol.Day)
# lines(cc.cls.3$time, lr.3$fitted.values, col="blue")

# plot(cc.data$time, cc.data$Vol.Day)
# lines(cls.1$time, lr.1$fitted.values, col="blue")
# lines(cc.cls.2$time, lr.2$fitted.values, col="blue")
# lines(cc.cls.3$time, lr.3$fitted.values, col="blue")


# Exponential regression
lr.1.exp <- lm(log(Vol.Day) ~ time, data = cls.1[, -c(7)])  # fit cls.123 (after chop)
vol.exp.1 <- exp(predict(lr.1.exp, cls.1))
plot(cc.cls.1$time, cc.cls.1$Vol.Day)
lines(cls.1$time, vol.exp.1, col = "blue")

lr.2.exp <- lm(log(Vol.Day) ~ time, data = cls.2[, -c(7)])
vol.exp.2 <- exp(predict(lr.2.exp, cls.2))
plot(cc.cls.2$time, cc.cls.2$Vol.Day)
lines(cls.2$time, vol.exp.2, col = "purple")

lr.3.exp <- lm(log(Vol.Day) ~ time, data = cls.3[, -c(7)])
vol.exp.3 <- exp(predict(lr.3.exp, cls.3))
plot(cc.cls.3$time, cc.cls.3$Vol.Day)
lines(cls.3$time, vol.exp.3, col = "red")

# Find cross point of two regressions

pred.check.1 <- exp(predict(lr.1.exp, cc.data[1e05:2e05, ]))
pred.check.2 <- exp(predict(lr.2.exp, cc.data[1e05:2e05, ]))

plot(cc.data$time[1e05:2e05], cc.data$Vol.Day[1e05:2e05])
lines(cc.data$time[1e05:2e05], pred.check.1, col = "red")
lines(cc.data$time[1e05:2e05], pred.check.2, col = "blue")

for (i in 1:1e05){
  if (abs(pred.check.1[i] - pred.check.2[i]) <= 0.01){
    crosspt <- cc.data[1e05:2e05, ][i, 6]
    print(crosspt)
    break
  }
}

# Band
band.limit.1 <- 2*sd(cls.1$Vol.Day)
band.limit.2 <- 2*sd(cls.2$Vol.Day)
band.limit.3 <- 2*sd(cls.3$Vol.Day)

# Group boundaries:
# Class 1, 2, 3
range.cls.1 <- 1:crosspt
range.cls.2 <- (crosspt+1):cls.2[nrow(cls.2), 6]
range.cls.3 <- (cls.2[nrow(cls.2), 6]+1):nrow(cc.data)

cc.data.band <- cc.data

pred.exp.1 <- exp(predict(lr.1.exp, cc.data[range.cls.1, ]))
pred.exp.2 <- exp(predict(lr.2.exp, cc.data[range.cls.2, ]))
pred.exp.3 <- exp(predict(lr.3.exp, cc.data[range.cls.3, ]))

pred.col <- data.frame(c(pred.exp.1, pred.exp.2, pred.exp.3))
pred.band.col <- data.frame(c(pred.exp.1-band.limit.1, pred.exp.2-band.limit.2, 
                   pred.exp.3-band.limit.3))

cc.data.band$pred.exp <- pred.col[, 1]
cc.data.band$pred.band <- pred.band.col[, 1]

# Plot for K Means clustering
library(ClusterR)
library(RColorBrewer)
library(ggplot2)
mypalette<-brewer.pal(9, name="Set1")
num.cluster <- 4

plot.def <- ggplot(data=cc.data, aes(x=time))+
  geom_point(aes(y=Vol.Day, color = factor(cc.data$km.cls)))+
  ggtitle(sprintf("K Means Clustering for %d Classes", num.cluster)) + labs(color = "Classes") +
  theme(plot.title = element_text(lineheight=0.7, face="bold", hjust=0.5)) +
  xlab("Time") + ylab("Volume - Calendar Day Production") +
  geom_line(color='red',data = cc.data.band, aes(y=pred.exp)) +
  geom_line(color='red',data = cc.data.band, aes(y=pred.band)) +
  scale_color_manual(values = mypalette[c(2, 4, 1, 3)])
  #scale_color_manual(values=c("blue", "purple", "red", "green3"))
  #scale_color_manual(values = mypalette)

plot.def

write.csv(cc.data.band, file="cc_data_band.csv")
write.csv(cc.data.band[, c(8, 9)], file="cc_data_band_2.csv")


