# IRS CA in-migration from other states (1990-2010)
import pandas as pd
import numpy as np
import os
import re

inmig_91_11 = os.listdir('CA In 91_11')
outmig_91_11 = os.listdir('CA Out 91_11')

master_df = pd.DataFrame()
years = []
folders = ['CA In 91_11', 'CA Out 91_11']
types = ['In', 'Out']
counter = 0

for folder in [inmig_91_11, outmig_91_11]:
    temp_df = pd.DataFrame()
    for file in folder:
        # Identifying year from different file names
        num = re.findall('\d+', file)[0][-2:]
        if int(num) > 20:
            yr = int('19' + num)
        else:
            yr = int('20' + num)

        print(yr)
        
        # Extracting these cols: mig state code, mig state name, returns, exemptions
        if yr < 1993:
            cols = [0,2,5]
        elif yr > 2009:
            cols = [1,3,5]
        else:
            cols = [0,2,4]
            
        df = pd.read_excel(folders[counter] + '/' + file, usecols=cols)
        df.columns = ['State_FIPS', 'State', 'Exemptions']
        first_line_id = max(df.iloc[:15].State_FIPS[df.State_FIPS.isin(['96','06','63',96,6,63])].index)
        df = df.loc[first_line_id+1:][~df.State_FIPS.isin(['96''97','98','06','63','57',96,97,98,6,63,57])][:51]
        #df = df.loc[first_line_id+1:].iloc[:52]  # Including 50 states, DC & PR and excluding text at bottom
        df = df.dropna(subset=['State_FIPS','State'])
        df.State_FIPS = df.State_FIPS.astype(int)
        df = df[(df['State_FIPS'] < 58) & (~df.State_FIPS.isin([6]))]  # Excluding CA total
        years += [yr]*len(df)
        print(yr, len(df))

        temp_df = pd.concat([temp_df, df])
        
    temp_df['Type'] = [types[counter]] * len(temp_df)
    master_df = pd.concat([master_df, temp_df])
    counter += 1
    
master_df['Year'] = years
master_df.State = master_df.State.apply(lambda x:x.title())
master_df = master_df.sort_values(['Type', 'Year', 'Exemptions'], ascending=[True,True,False])
master_df.to_csv('IRS_CA_states_in_out_mig_9111.csv', index=False)