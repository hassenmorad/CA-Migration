# Distribution of rent costs in all US counties
import pandas as pd
import numpy as np
import requests

# Adding column descriptions
rent_df = pd.read_csv('Census_Rent.csv')  # Copied from [https://api.census.gov/data/2018/acs/acs5/variables.html] and slightly formatted in excel
rent_df['Vals'] = rent_df['Vals'].apply(lambda x:x.split('!!')[-1:]).apply(lambda x:' '.join(x))
cols = rent_df.Vals.values.tolist()[:-1] + ['Median', 'State', 'County']
rent_vars = ','.join(rent_df.Code.values)

# Retrieving data from Census API
r = requests.get('https://api.census.gov/data/2017/acs/acs5?get=' + rent_vars + '&for=county:*')
df = pd.DataFrame(r.json()[1:])
df.columns = cols

df = df.replace(' ', np.nan).fillna(0)    
df = df.sort_values(['State', 'County'])
df['FIPS'] = df.State.astype(str) + df.County.astype(str).apply(lambda x:x.zfill(3))
df.to_csv('Census_API_Rent_dist_17.csv', index=False)