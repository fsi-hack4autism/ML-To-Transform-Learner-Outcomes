# %% [markdown]
# ## **Autism Hackathon**

# %% [markdown]
# ### Load Libraries

# %%
#%pip install scikit-learn

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# configure display options
pd.set_option("display.max_columns", None)  # show all columns
pd.set_option("display.max_rows", None)  # show all rows
pd.set_option("display.width", None)  # auto-adjust width
#%%
# ### Load data
data = pd.read_csv('../data/joinedData_assessmentStudentAssessor3_clean Anonymized.csv')
df = data.copy() 
df.head()

# %%
df.shape
# %%
cols_todrop = [
       'medTime_allTaskData_grpAssessor', 'avgTime_allTaskData_grpAssessor',
       'medTime_allTaskData_grpStudent', 'avgTime_allTaskData_grpStudent',
       'AssessorId','avgTime_startAssessment_grpAssessor',
       'medTime_startAssessment_grpAssessor',  
       'medTime_startAssmnt_grpStudent', 'OrganizationId', 
       'bit_multipleAssessors_grpStudent', 'avgTime_startAssmnt_grpStudent',
       'avgTime_endAssmnt_grpStudent', 'medTime_endAssmnt_grpStudent', 
       'AssessmentEndTime', 'AssessmentStartTime', 'studentDOB_moYear']

df.drop(columns=cols_todrop, inplace=True)

#%%
# profile  new column called 'assessment_recency_in_days' that has the difference 
# in days between the 'latest_date' and the 'assessmentDate', 
# convert 'assessmentDate' column to datetime format
df['assessmentDate'] = pd.to_datetime(df['assessmentDate'])
# find the earliest and latest dates in the column
earliest_date = df['assessmentDate'].min()
latest_date = df['assessmentDate'].max()
# print the range of dates
print('Date range:', earliest_date, 'to', latest_date)
# calculate the difference in days between latest date and assessmentDate
df['assessment_recency_in_days'] = (latest_date - df['assessmentDate']).dt.days
df.head()
#%%
df.dtypes
#%%
# profile gender in 3 columns: male_ind, female_ind, unspecied_gender_ind
df['male_ind'] = df['IsMale'].apply(lambda x: 1 if x==1 else 0) 
df['female_ind'] = df['IsMale'].apply(lambda x: 1 if x==0 else 0) 
df['unspec_gender_ind'] = df['IsMale'].apply(lambda x: 1 if np.isnan(x) else 0)
#%%
# drop unneeded cols
df = df.drop(columns = ['IsMale', 'assessmentDate'], axis=1)
#%%
df.dtypes
#%%
#import datetime as dt
#df['AssessmentDuration'] = pd.to_timedelta(df['AssessmentDuration'], unit='ns')
#df['AssessmentDurationInSeconds'] = df['AssessmentDuration'].dt.seconds
#%%
# create a new column to store the converted values
df['AssessmentDurationInSeconds'] = np.nan

# iterate through each row and convert the value to total seconds
for i, row in df.iterrows():
    duration = row['AssessmentDuration']
    if isinstance(duration, str) and duration != '':
        if duration.startswith(':'):
            duration = duration[1:] # remove extra colon if present
        try:
            h, m, s, ms = map(int, duration.split(':'))
            total_seconds = (h * 3600) + (m * 60) + s + (ms / 1000)
            df.at[i, 'AssessmentDurationInSeconds'] = total_seconds
        except ValueError:
            print(f"Invalid value in row {i}: {duration}")

# QA
#df[['AssessmentDuration', 'AssessmentDurationInSeconds']].head()
#%%
# drop unneeded cols
df = df.drop(columns = ['AssessmentDuration'], axis=1)

#%%
# set student_id as index
df = df.set_index('StudentId')
#%%
df = df.drop(columns = ['AssessmentId'], axis=1)
# %% 
# ### Check missing data
def get_missing_values_perc(df):
    """
    Calculates the percentage of missing values 
    """
    total = df.isnull().sum().sort_values(ascending = False)
    percent = (df.isnull().sum()/df.isnull().count()*100).sort_values(ascending = False)
    return pd.concat([total, percent], axis=1, keys=['Total', 'Perc%'])


missing_values = get_missing_values_perc(df)
missing_values= missing_values[missing_values['Perc%'] > 0]
missing_values_cols = missing_values.index.tolist()
#%%
#df_missing_cols = df[missing_values.index.tolist()]
#df_missing_cols.columns

# %%
#df_missing_cols.info()

# %%
# impute missing values  with mean
for colname in missing_values_cols:
    df[colname].fillna(df[colname].mean(), inplace=True)

#df_missing_cols.info()
# %%
df.describe()
#%%
list(df.columns)

#%%
# Save file
df.to_csv('./out/prep_data.csv')



