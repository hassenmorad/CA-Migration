import pandas as pd
import numpy as np
import math

master_df = pd.DataFrame()
for year in range(2011, 2018):
    yrs = str(year)[2:] + str(year+1)[2:]
    yr_df = pd.DataFrame()
    mig_types = ['inflow', 'outflow']
    counter = 0
    
    for mig_type in mig_types:
        file = pd.read_csv('irs/county12to18/county' + mig_type + yrs + '.csv', encoding='latin', usecols=[0,1,5,6,8])
        file.columns = ['State_FIPS', 'County_FIPS', 'County', 'Counts', 'Income']
        file = file[file.County_FIPS != 0]
        file['Counts'] = file['Counts'] = file['Counts'].replace(-1, 0).astype(str).str.replace(r'\D', '').replace('', np.nan).astype(float).replace(0, np.nan)
        
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
            incs.append(round(df.Income.max() * 1000 / df.Counts.max(), 0))  # The max value is the total county income (in thousands)
            pops.append(df.Counts.max())  # The max value is the total county population
            mig = df.Counts.iloc[0]
            if not math.isnan(mig):  # The first entry is the total count of migrator households
                migs.append(df.Counts.iloc[0])
            else:
                migs.append(df.Counts.sort_values(ascending=False).values[1])  # If the first entry is missing, the second biggest value is the mig count (though it could also be missing)
            
        dataframe = pd.DataFrame({'Year':np.full(len(pops), year+1).tolist(), 'FIPS':file.FIPS.unique(), 'Households':pops, 'Inmigrants':migs, 'Income':incs})
            
        # Inmigrators file
        if counter == 0:
            yr_df = dataframe.copy()
        # Outmigrators file
        else:
            # Confirming that contains same FIPS and in same order before joining
            if list(yr_df['FIPS'].sort_values().unique()) == list(dataframe['FIPS'].sort_values().unique()):  
                yr_df['Outmigrants'] = migs
            else:
                missing = []
                for fips in yr_df.FIPS.unique():
                    if fips not in dataframe.FIPS.unique():
                        missing.append(fips)
                yr_df = yr_df[~yr_df.FIPS.isin(missing)]
                yr_df['Outmigrants'] = migs
                
        counter += 1
        
    master_df = pd.concat([master_df, yr_df])
    
# master_df = master_df[master_df.Households != 0]
# Adding county col (will fill w/ values when combining files for all years)
master_df['County'] = pd.Series()
master_df = master_df[['Year', 'County', 'FIPS', 'Households', 'Inmigrants', 'Outmigrants', 'Income']]
master_df.to_csv('county_migration_12to18.csv', index=False)