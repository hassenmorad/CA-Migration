# Cleaning previously wrangled IRS migration data (need to fill in missing values- res, inmig, outmig)
import pandas as pd
import numpy as np
import math

source = 'C:/users/mahmoud/desktop/projects/migration/'
# IRS migration data source: https://www.irs.gov/statistics/soi-tax-stats-migration-data
file0 = pd.read_csv(source + 'county_migration_91to92.csv')
file1 = pd.read_csv(source + 'county_migration_93to11.csv')
file2 = pd.read_csv(source + 'county_migration_12to18.csv')

combined = pd.concat([file0, file1, file2]).sort_values(['FIPS', 'Year']).reset_index(drop=True)
combined = combined[combined.FIPS != 15005]  # Missing almost all values

# Changing Dade County (FL) code to updated Miami-Dade County code
combined.loc[combined.FIPS == 12025, 'FIPS'] = 12086
#combined.loc[combined.FIPS == 12086, 'County'] = 'Miami-Dade'
#-------------------------------------------------------------------------------------------------------------------------------
"""# Adding missing WY 1994 records (replacing w/ avg. of '93 & '95 values)
temp = combined.copy() 
wy94 = temp[(temp.FIPS > 56000) & (temp.FIPS < 57000) & (temp.Year == 1993)]
wy94.Year = list(np.full(len(wy94), 1994))
for col in wy94.columns[3:]:  # Columns: ['Year', 'County', 'FIPS', 'Residents', 'Inmigrants', 'Outmigrants']
    wy94[col] = pd.Series()
        
wy9395 = temp[(temp.FIPS > 56000) & (temp.FIPS < 57000) & (temp.Year.isin([1993,1995]))]  # 93 & 95 Wyoming records
wy = pd.concat([wy9395, wy94]).sort_values(['FIPS', 'Year'])

# Filling missing values (Res, Inmig, Outmig) w/ avg. of 93 & 95 values
for col in wy.columns[3:]:
    wy[col] = wy[col].fillna((wy[col].shift() + wy[col].shift(-1))/2).fillna(method='bfill')
wynew = wy[wy.Year == 1994].sort_values('FIPS')
combined = pd.concat([combined, wynew]).sort_values(['FIPS', 'Year']).reset_index(drop=True)"""

#-------------------------------------------------------------------------------------------------------------------------------
# Adding rows if county is missing years (applies to about 40 counties)
new_rows = pd.DataFrame()
missing_fips1 = []
for fips in combined.FIPS.unique():
    df = combined[combined.FIPS == fips]
    if len(df) < 28:  # Complete year range (91-18)
        missing_fips1.append(fips)
        missing = [yr for yr in range(1991, 2019) if yr not in df.Year.values]
        length = len(missing)
        fips_new = pd.DataFrame({'Year':list(np.full(length, missing)), 'County':list(np.full(length, df.County.iloc[0])), 
                            'FIPS':list(np.full(length, fips)), 'Residents':list(np.full(length, np.nan)), 
                            'Inmigrants':list(np.full(length, np.nan)), 'Outmigrants':list(np.full(length, np.nan))})
        new_rows = pd.concat([new_rows, fips_new])
        
combined = pd.concat([combined, new_rows]).sort_values(['FIPS', 'Year'])
combined['State'] = combined.FIPS.astype(str).apply(lambda x:x.zfill(5)[:2])  # Needed for filtering in next section

#-------------------------------------------------------------------------------------------------------------------------------
# Filling in Missing Res, Inmig, & Outmig Values
missing_fips2 = set(list(combined.FIPS[combined.Inmigrants.isnull()].unique()) + list(combined.FIPS[combined.Outmigrants.isnull()].unique()))
not_missing_df = combined[~combined.FIPS.isin(missing_fips2)]

for fips in missing_fips2:
    df = combined[combined.FIPS == fips]
    temp_df = df.copy()
    # Assigning all nulls if 4 or fewer mig values are available (b/c too few to calculate accurate estimates)
    if len(df[df.Inmigrants.isnull()]) > 23 or len(df[df.Outmigrants.isnull()]) > 23:
        df['Inmigrants'] = np.full(28, np.nan)
        df['Outmigrants'] = np.full(28, np.nan)
        df['Residents'] = df[col].fillna((df['Residents'].shift() + df['Residents'].shift(-1))/2).fillna(method='bfill').fillna(method='ffill').round(0).astype(int)
        
    else:
        for col in ['Residents', 'Inmigrants', 'Outmigrants']:
            df[col] = df[col].fillna((df[col].shift() + df[col].shift(-1))/2).fillna(method='bfill').fillna(method='ffill').round(0).astype(int)
    
    not_missing_df = pd.concat([not_missing_df, df])

combined = not_missing_df.copy()

#-------------------------------------------------------------------------------------------------------------------------------
# Adding Areaname col & splitting values to County & State cols
# Source: https://www.census.gov/library/publications/2011/compendia/usa-counties-2011.html
counties = pd.read_excel('CLF01.xls', usecols=[0,1])[2:]
areaname_dict = {}
for fips in counties['STCOU'].unique():
    area = counties.Areaname[counties.STCOU == fips].iloc[0]
    areaname_dict[fips] = area

combined['Areaname'] = combined['FIPS'].map(areaname_dict)
combined[['County', 'State']] = combined.Areaname.str.split(', ', expand=True)

# Filling missing DC state col
combined.loc[combined.Areaname == 'District of Columbia', 'State'] = 'DC'

#-------------------------------------------------------------------------------------------------------------------------------
# Adding New Migration Columns
combined['Net_Mig'] = combined['Inmigrants'] - combined['Outmigrants']
combined['Rel_Mig_Pct'] = round(combined['Net_Mig'] / combined['Residents'], 4)

#-------------------------------------------------------------------------------------------------------------------------------
# Replacing Extreme Migration #s w/ avg. of 3 yrs before & 3 yrs after (same county)
extreme_mig = combined[(combined.Rel_Mig_Pct < -.15) | (combined.Rel_Mig_Pct > .15)]
for i, row in extreme_mig.iterrows():
    fips = row.FIPS
    year = row.Year
    inmig = abs(row.Inmigrants)
    outmig = abs(row.Outmigrants)
    extreme_ids = extreme_mig.index[extreme_mig.FIPS == fips].values
    # Replacing both in & out mig counts
    avg_inmig = round(combined.Inmigrants[(combined.FIPS == fips) & 
                                    (~combined.index.isin(extreme_ids)) & 
                                    (combined.Year.isin(range(year-3, year+3)))].mean(), 4)
    combined.loc[i, 'Inmigrants'] = avg_inmig
    avg_outmig = round(combined.Outmigrants[(combined.FIPS == fips) & 
                                        (~combined.index.isin(extreme_ids)) & 
                                        (combined.Year.isin(range(year-3, year+3)))].mean(), 4)
    combined.loc[i, 'Outmigrants'] = avg_outmig

#-------------------------------------------------------------------------------------------------------------------------------
# Re-calculating Migration Columns (after identifying extreme numbers)
combined['Net_Mig'] = combined['Inmigrants'] - combined['Outmigrants']
combined['Rel_Mig_Pct'] = round(combined['Net_Mig'] / combined['Residents'], 4)


# Converting cols to ints
#for col in ['Residents', 'Inmigrants', 'Outmigrants', 'Net_Mig']:
    #combined[col] = combined[col].astype(int)

combined = combined.sort_values(['Year', 'FIPS'])
combined.to_csv('irs_mig_91to2018.csv', index=False)