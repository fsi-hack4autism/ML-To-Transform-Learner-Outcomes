
#%%
# This script build cluster models
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
#%%
df = df.drop( 'assessment_recency_in_days', axis=1)
# %%
df.info()

# %%
# check duplicates
#df[df.duplicated()].shape # (5, 70)
# remove duplicates
#df = df[~df.duplicated()] # (23349, 70)
#df.shape
#%%
#df = df.drop(columns=['assessment_recency_in_days', 'unspec_gender_ind', 'FirstAssessment_byStudent.1'], axis=1)
# %%
df.describe().T
#%%
df.head()
#%%
df.shape # (23354, 51)
# %%
# check correlation
#plt.figure(figsize  = (50, 50))
#df_no_id = df.drop("StudentId", axis=1)
#sns.heatmap(df_no_id.corr(), annot = True, cmap = "YlGnBu")

#plt.show()
# %%
"""
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
"""
#%%
df.columns
#%%
len(df.columns)

#%%
df['FirstAssessment_byStudent'].value_counts()
#%%
# keep rows where the value of column 'FirstAssessment_byStudent' is 0
#df = df[df['FirstAssessment_byStudent'] == 0]
#df.shape
# %%
#Scaling the data 
from sklearn.preprocessing import StandardScaler, MinMaxScaler
scaler = StandardScaler()
#scaler = MinMaxScaler()
data_scaled = pd.DataFrame(scaler.fit_transform(df), columns = df.columns)
data_scaled.head()
#%%
#Creating copy of the data to store labels from each algorithm
data_scaled_copy = data_scaled.copy(deep = True)
#%%
data_scaled.head()
# %%
# kmeans model
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
# Empty dictionary to store the Silhouette score for each value of K
sc = {} 

# Iterate for a range of Ks and fit the scaled data to the algorithm. Store the Silhouette score for that K 
for k in range(2, 10):
    kmeans = KMeans(n_clusters = k, random_state = 1).fit(data_scaled)
    labels = kmeans.predict(data_scaled)
    sc[k] = silhouette_score(data_scaled, labels)

# Elbow plot
plt.figure()
plt.plot(list(sc.keys()), list(sc.values()), 'bx-')
plt.xlabel("Number of cluster")
plt.ylabel("Silhouette Score") #
plt.show()
# # best 3: 0.1410034755315065,
# %%
sc
#%%
#%%
kmeans = KMeans(n_clusters = 3, random_state = 1)
kmeans.fit(data_scaled)
#%%

# Adding predicted labels to the original data
df['KMeans_Labels'] = kmeans.predict(data_scaled)
df['KMeans_Labels'].value_counts()
#%%

#%%
cols_visualise = df.columns

for col in cols_visualise:
    sns.boxplot(x = 'KMeans_Labels', y = col, data = df)
    plt.show()