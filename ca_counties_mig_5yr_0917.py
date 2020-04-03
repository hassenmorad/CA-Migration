# Census 2009-2017 CA county migration counts (in & out- same state, another state, abroad) from Census Migration Flows API (https://www.census.gov/data/developers/data-sets/acs-migration-flows.html)
# Note: data represents 5 year period (the year listed represents the last year)
import pandas as pd
import numpy as np
import requests

# Retrieving data from Census API
master_df = pd.DataFrame()
master_df_adj = pd.DataFrame()
for year in range(2009, 2018):
    print(year)
    r = requests.get('https://api.census.gov/data/' + str(year) + '/acs/flows?get=COUNTY1_NAME,GEOID1,STATE2_NAME,COUNTY2_NAME,GEOID2,POP1YR,MOVEDIN,MOVEDOUT,MOVEDNET,NONMOVERS,SAMECOUNTY,FROMDIFFCTY,FROMDIFFSTATE,FROMABROAD,TODIFFCTY,TODIFFSTATE,TOPUERTORICO&for=county:*&in=state:06')
    df = pd.DataFrame(r.json()[1:])
    df.columns = ['County1Name', 'County1FIPS', 'State2Name', 'County2Name', 'County2FIPS', 'County1Population', 'MovedIn', 'MovedOut', 'Net_Dom', 'NonMovers', 
                  'Within_Same_County', 'From_Diff_County_Same_State', 'From_Diff_State', 'From_Abroad', 'To_Diff_County_Same_State', 'To_Diff_State', 'To_PR', 'State', 'County']
    df = df.drop(['County'], axis=1)
    df['Year'] = list(np.full(len(df), year))
    df = df.replace(' ', np.nan).fillna(0)
    master_df = pd.concat([master_df, df])

    # Creating file w/ adjusted values (excluding weird FIPS)
    df.to_csv('temp.csv', index=False)  # To solve formatting issues (w/ large FIPS code- too long for Python to interpret as an int)
    adj_df = pd.read_csv('temp.csv')
    adj_df = adj_df[adj_df.County2FIPS < 80000]  # Excluding weird counties (distorted data)
    master_df_adj = pd.concat([master_df_adj, adj_df])

master_df_adj.to_csv('ca_counties_mig_5yr_0917_adj.csv', index=False)
master_df.to_csv('ca_counties_mig_5yr_0917_unadj.csv', index=False)