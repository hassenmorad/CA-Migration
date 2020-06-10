# Distribution of housing costs for homeowners (renters not included) in all US counties
import pandas as pd
import numpy as np
import requests

# Adding column descriptions
hous_df = pd.read_csv('Census_Housing_Costs.csv')  # Copied from [https://api.census.gov/data/2018/acs/acs5/variables.html] and slightly formatted in excel
hous_df['Vals'] = hous_df['Vals'].apply(lambda x:x.split('!!')[-2:]).apply(lambda x:' '.join(x)).apply(lambda x:x.replace('!!',' '))
cols = hous_df.Vals.values.tolist()[:-3] + ['Median', 'Median_Mort', 'Median_No_Mort', 'State', 'County']
hous_vars = ','.join(hous_df.Code.values)

# Retrieving data from Census API
r = requests.get('https://api.census.gov/data/2017/acs/acs5?get=' + hous_vars + '&for=county:*')
df = pd.DataFrame(r.json()[1:])
df.columns = cols

df = df.replace(' ', np.nan).fillna(0)    
df = df.sort_values(['State', 'County'])
df['FIPS'] = df.State.astype(str) + df.County.astype(str).apply(lambda x:x.zfill(3))
df.to_csv('Census_API_Homeowner_Housing_Costs_mort_nomort_17.csv', index=False)