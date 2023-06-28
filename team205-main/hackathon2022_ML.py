import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as pltdf = pd.read_csv("h_k.csv")
df.rename(columns={'Unnamed: 0': 'location'}, inplace=True)
df = df.replace({np.nan: None})for i in range(999):
    if df.loc[i, 'Diabetes Short-term Complications'] is None:
        df = df.drop([i])df.drop(df.columns[[12, 13, 14]], axis=1, inplace=True)cols = df.columns[1:11]
df = df.groupby('location')[cols].sum()X = df.iloc[:, 0:10]
y = df.iloc[:,-1]rf = RandomForestRegressor(n_estimators=50)
rf.fit(X, y)
print(rf.feature_importances_)
plt.barh(list(X.columns), rf.feature_importances_)
print(list(X.columns))
plt.show()