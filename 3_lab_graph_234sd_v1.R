cc.data.band <- read.csv("cc_data_band_234sd_7K_2.csv", row.names = 1)
cc.labs <- read.csv("cc_labs_234sd.csv", row.names = 1)

# Plot for K Means clustering and bands
library(ClusterR)
library(RColorBrewer)
library(ggplot2)
mypalette<-brewer.pal(9, name="Set1")
num.cluster <- 4

# Labeled graph for 2 SD bands
plot.def <- ggplot(data=cc.data.band, aes(x=time))+
  geom_point(aes(y=Vol.Day, color = factor(cc.labs$lab_2sd)))+
  ggtitle(sprintf("Labeled Graph for 3 Classes with 2*SD Threshold", num.cluster)) + labs(color = "Classes") +
  theme(plot.title = element_text(lineheight=0.7, face="bold", hjust=0.5)) +
  xlab("Time") + ylab("Volume - Calendar Day Production") +
  #geom_line(color='black',data = cc.data.band, aes(y=pred.exp), size=1) +
  geom_line(color='red',data = cc.data.band, aes(y=pred.band), size=1) +
  # geom_line(color='purple',data = cc.data.band, aes(y=pred.band3sd), size=1) +
  # geom_line(color='blue',data = cc.data.band, aes(y=pred.band4sd), size=1) +
  scale_color_manual(values = mypalette[c(3, 1, 2)])
#scale_color_manual(values=c("blue", "purple", "red", "green3"))
#scale_color_manual(values = mypalette)

plot.def

# Labeled graph for 3 SD bands
plot.def <- ggplot(data=cc.data.band, aes(x=time))+
  geom_point(aes(y=Vol.Day, color = factor(cc.labs$lab_3sd)))+
  ggtitle(sprintf("Labeled Graph for 3 Classes with 3*SD Threshold", num.cluster)) + labs(color = "Classes") +
  theme(plot.title = element_text(lineheight=0.7, face="bold", hjust=0.5)) +
  xlab("Time") + ylab("Volume - Calendar Day Production") +
  #geom_line(color='black',data = cc.data.band, aes(y=pred.exp), size=1) +
  # geom_line(color='red',data = cc.data.band, aes(y=pred.band), size=1) +
  geom_line(color='purple',data = cc.data.band, aes(y=pred.band3sd), size=1) +
  # geom_line(color='blue',data = cc.data.band, aes(y=pred.band4sd), size=1) +
  scale_color_manual(values = mypalette[c(3, 1, 2)])
#scale_color_manual(values=c("blue", "purple", "red", "green3"))
#scale_color_manual(values = mypalette)

plot.def

# Labeled graph for 4 SD bands
plot.def <- ggplot(data=cc.data.band, aes(x=time))+
  geom_point(aes(y=Vol.Day, color = factor(cc.labs$lab_4sd)))+
  ggtitle(sprintf("Labeled Graph for 3 Classes with 4*SD Threshold", num.cluster)) + labs(color = "Classes") +
  theme(plot.title = element_text(lineheight=0.7, face="bold", hjust=0.5)) +
  xlab("Time") + ylab("Volume - Calendar Day Production") +
  #geom_line(color='black',data = cc.data.band, aes(y=pred.exp), size=1) +
  # geom_line(color='red',data = cc.data.band, aes(y=pred.band), size=1) +
  # geom_line(color='purple',data = cc.data.band, aes(y=pred.band3sd), size=1) +
  geom_line(color='blue',data = cc.data.band, aes(y=pred.band4sd), size=1) +
  scale_color_manual(values = mypalette[c(3, 1, 2)])
#scale_color_manual(values=c("blue", "purple", "red", "green3"))
#scale_color_manual(values = mypalette)

plot.def
