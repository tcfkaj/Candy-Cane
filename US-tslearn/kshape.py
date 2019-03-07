import numpy as np
import matplotlib.pyplot as plt

from tslearn.utils import to_time_series_dataset
from tslearn.metrics import sigma_gak, cdist_gak
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.clustering import KShape

hum_sub = np.loadtxt('../../HUM_subs.csv', delimiter=',', skiprows=0)
print(hum_sub.shape)

X = to_time_series_dataset(hum_sub)
print(X.shape)
X = TimeSeriesScalerMeanVariance().fit_transform(X)
sz = X.shape[1]

seed = 4
np.random.seed(seed)

nclust = 3
ks = KShape(n_clusters=nclust, verbose=True, random_state=seed)
y_pred = ks.fit_predict(X)

print(y_pred+1)
print(len(y_pred))

# for i,j in enumerate(y_pred+1):
#     if j == 2:
#         print(i+1)

plt.figure()
for yi in range(nclust):
    plt.subplot(nclust, 1, 1 + yi)
    for xx in X[y_pred == yi]:
        plt.plot(xx.ravel(), "k-", alpha=0.2)
    plt.plot(ks.cluster_centers_[yi].ravel(), "r-")
    plt.xlim(0, sz)
    plt.ylim(-4, 4)
    plt.title("Cluster %d" % (yi+1))

plt.tight_layout()
plt.show()

