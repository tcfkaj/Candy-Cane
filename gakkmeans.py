import numpy as np
import matplotlib.pyplot as plt

from tslearn.utils import to_time_series_dataset
from tslearn.metrics import sigma_gak, cdist_gak
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.clustering import GlobalAlignmentKernelKMeans

hum_sub = np.loadtxt('HUM_subs.csv', delimiter=',', skiprows=1)
print(hum_sub.shape)

X = to_time_series_dataset(hum_sub)
print(X.shape)
X = TimeSeriesScalerMeanVariance().fit_transform(X)
sz = X.shape[1]

seed = 0
np.random.seed(seed)

nclust = 3
gak_km = GlobalAlignmentKernelKMeans(n_clusters=nclust, sigma=sigma_gak(X),
        n_init=10, verbose=True, random_state=seed)
y_pred = gak_km.fit_predict(X)

print(gak_km.inertia_)
print(y_pred)

plt.figure()
for yi in range(nclust):
    plt.subplot(nclust, 1, 1 + yi)
    for xx in X[y_pred == yi]:
        plt.plot(xx.ravel(), "k-")
    plt.xlim(0, sz)
    plt.ylim(-4, 4)
    plt.title("Cluster %d" % (yi+1))

plt.tight_layout()
plt.show()

