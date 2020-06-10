# Distribution of home values for all US counties
import pandas as pd
import numpy as np
import requests

# Adding column descriptions
home_df = pd.read_csv('Census_Home_Value1.csv')  # Copied from [https://api.census.gov/data/2018/acs/acs5/variables.html] and slightly formatted in excel
home_df['Vals'] = home_df['Vals'].apply(lambda x:x.split('!!')[-2:]).apply(lambda x:' '.join(x)).apply(lambda x:x.replace('!!',' '))
cols = home_df.Vals.values.tolist()[:-3] + ['Lower_Quartile', 'Median', 'Upper_Quartile', 'State', 'County']
home_vars = ','.join(home_df.Code.values)

# Retrieving data from Census API
r = requests.get('https://api.census.gov/data/2017/acs/acs5?get=' + home_vars + '&for=county:*')
df = pd.DataFrame(r.json()[1:])
df.columns = cols

df = df.replace(' ', np.nan).fillna(0)    
df = df.sort_values(['State', 'County'])
df['FIPS'] = df.State.astype(str) + df.County.astype(str).apply(lambda x:x.zfill(3))
df.to_csv('Census_API_Home_Value_quartiles_17.csv', index=False)