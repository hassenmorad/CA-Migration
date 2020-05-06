# IRS CA in-migration from other states (1990-2010)
import pandas as pd
import numpy as np
import os
import re

inmig_12_18 = os.listdir('CA In 12_18')
outmig_12_18 = os.listdir('CA Out 12_18')

master_df = pd.DataFrame()
years = []
folders = ['CA In 12_18/', 'CA Out 12_18/']
types = ['In', 'Out']
counter = 0

for folder in [inmig_12_18, outmig_12_18]:
    temp_df = pd.DataFrame()
    for file in folder:
        # Identifying year from different file names
        num = re.findall('\d+', file)[0][-2:]
        yr = int('20' + num) - 1
        print(yr)
                    
        df = pd.read_csv(folders[counter] + file, usecols=[0,1,3,5])
        df.columns = ['Origin', 'State_FIPS', 'State', 'Exemptions']
        df = df[df.Origin == 6].drop('Origin', axis=1)
        df = df[(df.State_FIPS != 6) & (df.State_FIPS < 57)]
        years += [yr]*len(df)
        print(yr, len(df))

        temp_df = pd.concat([temp_df, df])
        
    temp_df['Type'] = [types[counter]] * len(temp_df)
    master_df = pd.concat([master_df, temp_df])
    counter += 1
    
master_df['Year'] = years
master_df.State = master_df.State.apply(lambda x:x.title())
master_df = master_df.sort_values(['Type', 'Year', 'Exemptions'], ascending=[True,True,False])
master_df.to_csv('IRS_CA_states_inmig_1117.csv', index=False)