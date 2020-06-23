import pandas as pd
import numpy as np
import math
import os

master_df = pd.DataFrame()
source = '/Users/Mahmoud/Desktop/projects/migration/irs/'
years = range(1993, 2012)
years_counter = 0

for folder in os.listdir(source)[2:14] + os.listdir(source)[-8:-1]:  # Each folder contains 102 files- two for each state (inmig & outmig counts) for a particular year (93-11)
    yr_df = pd.DataFrame()  # Will be reset for every year (since each folder contains files for a particular year) and concatenated to master_df (below)
    state_df = pd.DataFrame()  # Will be reset for every state (below) and concatenated to yr_df (below)
    counter = 0
    for excel in os.listdir(source + folder):  # Files rotate b/w inmig & outmig counts for each state (in alphabetical order)
        name = source + folder + '/' + excel
        file = pd.read_excel(name, skiprows=10, usecols=[0,1,5,6,8])
        file.columns = ['State_FIPS', 'County_FIPS', 'County', 'Counts', 'Income']
        file = file[file.County_FIPS != 0]

        # Removing footnotes from 2010 & 2011 files
        if years[years_counter] > 2009:
            file = file[:-3]
            
        for col in ['Counts', 'Income']:
            if file[col].dtype == 'O':  # Some files (e.g. 9899 Idaho) contained random strings in the counts col- removing non-digits from value (e.g. '  d  49' -> '49')
                file[col] = file[col].replace(-1, 0).astype(str).str.replace(r'\D', '').replace('', np.nan).astype(float).replace(0, np.nan)
            
        # Converting to int before creating FIPS (so decimal point isn't included in zfill)
        for col in file.columns[:2]:
            file[col] = file[col].astype(int)
            
        file['FIPS'] = file['State_FIPS'].astype(str).apply(lambda x:x.zfill(2)) + file['County_FIPS'].astype(str).apply(lambda x:x.zfill(3))
       
        # Creating df w/ inmigrator counts col
        incs = []
        pops = []
        migs = []
        for fips in file.FIPS.unique():
            df = file[file.FIPS == fips]
            incs.append(round(df.Income.max() * 1000 / df.Counts.max(),0))  # The max value is the total county income (in thousands)
            pops.append(df.Counts.max())  # The max value is the total county population
            mig = df.Counts.iloc[0]
            if not math.isnan(mig):  # The first entry is the total count of migrators
                migs.append(df.Counts.iloc[0])
            else:
                migs.append(df.Counts.sort_values(ascending=False).values[1])  # If the first entry is missing, the second biggest value is the mig count (though it could also be missing)
                

        dataframe = pd.DataFrame({'FIPS':file.FIPS.unique(), 'Residents':pops, 'Inmigrants':migs, 'Income':incs})

        # Adding col w/ outmigrator counts (when counter is odd)
        if counter % 2 == 0:
            state_df = dataframe.copy()  # Resets variable for each state (b/c inmig & outmig files ordered in pairs)
            counter += 1
        else:
            counter += 1             
            # Confirming that both contain same FIPS and in same order (before joining)
            if list(state_df['FIPS'].sort_values().unique()) == list(dataframe['FIPS'].sort_values().unique()):  
                state_df['Outmigrants'] = migs
            else:
                missing = []
                # Removing FIPS not in both inmig & outmig state files
                for fips in state_df.FIPS.unique():
                    if fips not in dataframe.FIPS.unique():
                        missing.append(fips)
                for fips in dataframe.FIPS.unique():
                    if fips not in state_df.FIPS.unique():
                        missing.append(fips)
                        
                state_df = state_df[~state_df.FIPS.isin(missing)]
                dataframe = dataframe[~dataframe.FIPS.isin(missing)]
                state_df['Outmigrants'] = dataframe['Inmigrants'].values
            
            # Joining State DF w/ Year DF after completely formed (contains inmig & outmig counts)
            yr_df = pd.concat([yr_df, state_df])
                    
    yr_df['Year'] = list(np.full(len(yr_df), years[years_counter]))

    master_df = pd.concat([master_df, yr_df])
    years_counter += 1
    
# Adding county col (will fill w/ values when combining files for all years)
master_df['County'] = pd.Series()
master_df = master_df[['Year', 'County', 'FIPS', 'Residents', 'Inmigrants', 'Outmigrants', 'Income']]

# Retreived residents data from 1996 outmigrators file (missing from inmigrators)
master_df.loc[(master_df.FIPS == '16075') & (master_df.Year == 1996), 'Residents'] = 5380
master_df.loc[(master_df.FIPS == '22007') & (master_df.Year == 1996), 'Residents'] = 7968

master_df.to_csv('county_migration_93to11.csv', index=False)