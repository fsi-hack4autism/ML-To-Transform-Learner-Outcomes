# This create conduct PCA analysis aiming to reduce dim. of data
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# To scale the data using z-score 
from sklearn.preprocessing import StandardScaler
# Importing PCA and t-SNE
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# configure display options
pd.set_option("display.max_columns", None)  # show all columns
pd.set_option("display.max_rows", None)  # show all rows
pd.set_option("display.width", None)  # auto-adjust width

#%%
# loading the data
df = pd.read_csv('../out/prep_data.csv') # (23354, 553)
df.shape
# %%
# summary stat
df.describe().T
# %%
df = df.set_index('StudentId')
# %%
# scale data
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df)
df_scaled = pd.DataFrame(df_scaled, columns=df.columns)
df_scaled.head()
# %%
# PCA
# Defining the number of principal components to generate
n = df_scaled.shape[1]

# Finding principal components for the data
pca1 = PCA(n_components = n, random_state = 1)
data_air_pol_pca = pd.DataFrame(pca1.fit_transform(df_scaled))
# The percentage of variance explained by each principal component
exp_var1 = pca1.explained_variance_ratio_

#%%
# Find the least number of components that can explain >= 70% variance
sum = 0
for ix, i in enumerate(exp_var1):
    
    sum = sum + i
    if(sum>=0.70):
        print("Number of PCs that explain at least 70% variance: ", ix + 1)
        break

# results: Number of PCs that explain at least 60% variance:  30
#%%
# Making a new dataframe with first 5 principal components as columns and original features as indices
cols = []
n_pca_components = ix+1
for i in range(1, n_pca_components+1):
    cols.append('PC{}'.format(i))
cols
#%%
pc1 = pd.DataFrame(np.round(pca1.components_.T[:, 0:n_pca_components], 2), index = df_scaled.columns, columns = cols)
#%%
pc1.to_csv('../out/pca_loadings.csv')
# %%
# Assuming your data is stored in a numpy array called "data"
# where each row represents an observation and each column represents a feature
# You should normalize your data before running PCA

# Create a PCA object with the number of components you want to extract
pca = PCA(n_components=30)

# Fit the PCA model to your data
pca.fit(df_scaled)

# Get the absolute values of the PCA loadings for each component
loadings = np.abs(pca.components_)

# Find the indices of the features with the highest loadings for each component
indices = np.argsort(loadings, axis=1)[:, ::-1][:, :3]

# Create a list of feature names with the same length as the number of features in your data
num_features = df.shape[1]
#feature_names = ['feature{}'.format(i+1) for i in range(num_features)]
feature_names = list(df.columns)

# Print out the names of the features with the highest loadings for each component
features_sel = []
for i, component in enumerate(indices):
    print("Component ", i+1)
    print([feature_names[idx] for idx in component])
    features_sel.append([feature_names[idx] for idx in component])


# %%
features =  list(set([element for sublist in features_sel for element in sublist]))
features
#%%
len(features)
# %%
# store selected features
features.append('StudentId')
features.append('assessment_recency_in_days')
features.append('FirstAssessment_byStudent')
df.reset_index()[features].to_csv('../out/data_features_eng.csv', index=False)

# %%
features
# %%
