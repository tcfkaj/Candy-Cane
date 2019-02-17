#####################################################################
## Using "data_prep.R" before section: "Initial Boxplot" (line 60) ##
#####################################################################

cc.data <- read.csv("cc_before_diff.csv", row.names = 1)

# Start from the production
start_vol <- as.numeric(rownames(cc.data)[cc.data$Vol.Day!=0][1])
cc.data <- cc.data[start_vol:nrow(cc.data), ]
cc.data$time <- c(1:nrow(cc.data))
rownames(cc.data) <- c(1:nrow(cc.data))
# Replace all negative Flow.Pr with 0
for (i in 1:nrow(cc.data)){
  if (cc.data$Flow.Pr[i] < 0){
    cc.data$Flow.Pr[i] = 0
  }
}

#write.csv(cc.data, file="cc_data_clean.csv")
# ============================================================================
#cc.data <- read.csv("cc_data_clean.csv", row.names = 1)

# Standardization
cc.data.stand <- cc.data

for (i in 1:(ncol(cc.data)-1)){
  cc.data.stand[, i] = (cc.data[, i] - mean(cc.data[, i]))/sd(cc.data[, i])
}

# K Means Clustering
library(ClusterR)
library(RColorBrewer)
library(ggplot2)
mypalette<-brewer.pal(9, name="Set1")

num.initial <- 1
num.cluster <- 4  # try 2,3,4...
km <- KMeans_rcpp(cc.data.stand[, -6], num.cluster, num_init = num.initial, seed=1, initializer = 'kmeans++')
cls_res <- as.factor(km$clusters)
levels(cls_res) <- c(3, 1, 4, 2)
cc.data$km.cls <- cls_res

# Plot for K Means clustering
plot.def <- ggplot(data=cc.data, aes(x=time))+
  geom_point(aes(y=Vol.Day, color = factor(cc.data$km.cls)))+
  ggtitle(sprintf("K Means Clustering for %d Classes", num.cluster)) + labs(color = "Classes") +
  theme(plot.title = element_text(lineheight=0.7, face="bold", hjust=0.5)) +
  xlab("Time") + ylab("Volume - Calendar Day Production") +
  #scale_color_manual(values=c("blue", "green3", "red", "darkorange"))
  scale_color_manual(values = mypalette)

plot.def

# Saving data
write.csv(cc.data, file="cc_data_km_cls.csv")
write.csv(cc.data$km.cls, file="cc_data_km_cls4.csv")
# ==============================================================================

# Loading data
cc.data <- read.csv("cc_data_km_cls.csv", row.names = 1)
