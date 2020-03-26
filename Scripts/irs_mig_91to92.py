# Cleaning '91 & '92 IRS mig files (.txt)
import pandas as pd
import numpy as np
import os

master_df = pd.DataFrame()
for year in [1991, 1992]:
    source = 'irs/' + str(year-1) + 'to' + str(year) + 'CountyMigration/'
    folder = os.listdir(source)
    counter = 0
    year_df = pd.DataFrame()
    # Resetting df for each state (to add outmigrators col)
    if counter % 2 == 0:
        state_in_out_df = pd.DataFrame()
        
    for doc in folder:
        file = open(source + doc)
        states = []
        counties = []
        pops = []
        migs = []
        for line in file:
            line = line.rstrip()
            if line[0] != ' ':
                states.append(line.split()[0])
                counties.append(line.split()[1])
                migs.append(line.split()[-2])
            if 'Non-Migrants' in line.split():
                pops.append(line.split()[-2])
                
        if counter % 2 == 0:
            state_in_out_df = pd.DataFrame({'State':states, 'County':counties, 'Residents':pops, 'Inmigrants':migs})
        else:
            state_in_out_df['Outmigrants'] = migs
            year_df = pd.concat([year_df, state_in_out_df])
            
        counter += 1
        
    year_df['Year'] = np.full(len(year_df), year)
    master_df = pd.concat([master_df, year_df])

# Replacing -1 w/ nan to be consistent w/ 93-18 data
for col in master_df.columns[2:]:
    master_df[col] = master_df[col].astype(int).replace(-1, np.nan).replace(0, np.nan)
    
master_df['FIPS'] = master_df.State.astype(str).apply(lambda x:x.zfill(2)) + master_df.County.astype(str).apply(lambda x:x.zfill(3))
master_df['County'] = pd.Series()
master_df = master_df[['Year', 'County', 'FIPS', 'Residents', 'Inmigrants', 'Outmigrants']]
master_df.to_csv('county_migration_91to92.csv', index=False)