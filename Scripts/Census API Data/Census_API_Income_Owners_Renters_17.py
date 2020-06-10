# Distribution of housing cost for all US counties
import pandas as pd
import numpy as np
import requests

# Adding column descriptions
inc_vars_df = pd.read_csv('Census_Income_Owners_Renters.csv')  # Copied from [https://api.census.gov/data/2018/acs/acs5/variables.html] and slightly formatted in excel
inc_vars_df['Vals'] = inc_vars_df['Vals'].apply(lambda x:x.split('!!')[-2:]).apply(lambda x:' '.join(x)).apply(lambda x:x.replace('!!',' ')).apply(lambda x:x.replace(' occupied',':'))
cols = inc_vars_df.Vals.values.tolist()[:-3] + ['Median', 'Median_Owner', 'Median_Renter', 'State', 'County']
inc_vars = ','.join(inc_vars_df.Code.values)

# Retrieving data from Census API
r = requests.get('https://api.census.gov/data/2017/acs/acs5?get=' + inc_vars + '&for=county:*')
df = pd.DataFrame(r.json()[1:])
df.columns = cols

df = df.replace(' ', np.nan).fillna(0)    
df = df.sort_values(['State', 'County'])
df['FIPS'] = df.State.astype(str) + df.County.astype(str).apply(lambda x:x.zfill(3))
df.to_csv('Census_API_Income_Owners_Renters_17.csv', index=False)