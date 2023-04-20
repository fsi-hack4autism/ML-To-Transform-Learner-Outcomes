# This script build cluster models

# %%
#%pip install scikit-learn-extra
#%%
# load libraries
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns


# Importing clustering algorithms
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

from sklearn_extra.cluster import KMedoids
from sklearn.cluster import AgglomerativeClustering

from sklearn.cluster import DBSCAN

# Silhouette score
from sklearn.metrics import silhouette_score

import warnings
warnings.filterwarnings("ignore")
#%%
# load data
df = pd.read_csv('../out/data_features_eng.csv') # (23354, 71)
df.shape
#%%
df.head()

# %%
df = df.set_index('StudentId')
df.head()
# %%
list(df.columns)
# %%
df.info()
# %%
# check duplicates
df[df.duplicated()].shape # (5, 70)
# remove duplicates
df = df[~df.duplicated()] # (23349, 70)
df.shape
# %%
df.describe().T
#%%
df.head()
# %%
# check correlation
#plt.figure(figsize  = (50, 50))
df_no_id = df.reset_index().drop("StudentId", axis=1)
#sns.heatmap(df_no_id.corr(), annot = True, cmap = "YlGnBu")

#plt.show()
# %%
# create the correlation matrix
corr_matrix = df_no_id.corr()

# create a mask to only show the lower triangle
mask = np.zeros_like(corr_matrix)
mask[np.triu_indices_from(mask)] = True

# plot the heatmap
plt.figure(figsize=(20,20))
sns.heatmap(corr_matrix, mask=mask, cmap='YlGnBu', annot=True, fmt='.2f')
plt.title('Correlation Heatmap')
plt.savefig('correlation.png', dpi=300, bbox_inches='tight')
plt.show()

# %%
#Scaling the data 
from sklearn.preprocessing import StandardScaler, MinMaxScaler
scaler = StandardScaler()
data_scaled = pd.DataFrame(scaler.fit_transform(df), columns = df.columns)
data_scaled.head()
# %%
# k means model
# Empty dictionary to store the SSE for each value of K
sse = {} 

# Iterate for a range of Ks and fit the scaled data to the algorithm. 
# Use inertia attribute from the clustering object and store the inertia value for that K 
for k in range(1, 10):
    kmeans = KMeans(n_clusters = k, random_state = 1).fit(data_scaled)
    
    sse[k] = kmeans.inertia_

# Elbow plot
plt.figure()

plt.plot(list(sse.keys()), list(sse.values()), 'bx-')

plt.xlabel("Number of cluster")

plt.ylabel("SSE")
plt.show()
# %%