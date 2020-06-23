# Top 50 in/out migration counties for 5-yr estimates, each year b/w 05-09 to 13-17
import pandas as pd
import numpy as np

census5yr = pd.read_csv('ca_counties_mig_5yr_0917.csv')
ca0917 = census5yr[((census5yr.County1FIPS > 6000) & (census5yr.County1FIPS < 7000)) & (census5yr.County2FIPS < 60000) & (census5yr.State2Name != 'California')].sort_values('MovedOut', ascending=False)

for year in ca0917.Year.sort_values().unique():
    print(year)
    df = ca0917[ca0917.Year == year]
    ca_out_in = pd.DataFrame()
    counter = 0
    mig_types = ['MovedOut', 'MovedIn']
    for mig in mig_types:
        series = df.groupby('County2FIPS')[mig].sum()  # Calculating total CA outmig figures for each non-CA county
        ca_mig = pd.DataFrame({'FIPS':series.index, mig:series.values})[1:]  # Removing first row (Int'l migration)
        counties = []
        states = []
        
        # Adding County,State col (for DataWrapper map coordinates)
        for fips in ca_mig.FIPS.unique():
            counties.append(df.County2Name[df.County2FIPS == fips].iloc[0])
            states.append(df.State2Name[df.County2FIPS == fips].iloc[0])

        ca_mig['County_Name'] = counties
        ca_mig['State_Name'] = states
        ca_mig['County_State'] = ca_mig.County_Name + ', ' + ca_mig.State_Name
        ca_mig = ca_mig.drop(['County_Name', 'State_Name'], axis=1)

        if counter == 0:
            ca_out_in = ca_mig.copy()
        elif counter == 1:
            ca_out_in = ca_out_in.merge(ca_mig, on=['FIPS', 'County_State'])
            ca_out_in = ca_out_in.rename({'MovedOut':'Inmig', 'MovedIn':'Outmig'}, axis=1)
            ca_out_in['Net_Mig'] = ca_out_in.Inmig - ca_out_in.Outmig
            ca_out_in = ca_out_in.sort_values('Net_Mig')
        counter += 1

    top50_out_in = pd.concat([ca_out_in.iloc[:50], ca_out_in.iloc[-50:]])
    top50_out_in['Mig_Abs'] = top50_out_in.Net_Mig.abs()
    top50_out_in['Type'] = ['Net Out']*50 + ['Net In']*50
    top50_out_in['More'] = [c.split(',')[0] for c in top50_out_in.County_State[:50].values] + list(np.full(50, 'California'))
    top50_out_in['Year'] = np.full(len(top50_out_in), year)
    top50_out_in.to_csv('Census_5yr_CA_top50_mig_counties_' + str(year) + '.csv', index=False)