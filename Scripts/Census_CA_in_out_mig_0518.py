import pandas as pd
import numpy as np
import os

# Cleaning Census State Mig Tables
master_df = pd.DataFrame()
yr05 = pd.read_excel('Census States Mig 1yr/' + os.listdir('Census States Mig 1yr')[1], skiprows=6, skipfooter=3)[2:]
states = [col for col in yr05.columns if col[:3] != 'Unn']
for file in os.listdir('Census States Mig 1yr')[1:]:
    yr = file[-8:-4]
    df = pd.read_excel('Census States Mig 1yr/' + file, skiprows=6, skipfooter=3)[2:]
    df = df.loc[:,['Unnamed: 0'] + states]
    df = df.rename({'Unnamed: 0':'Current_Res'}, axis=1).dropna(subset=['Current_Res'])
    first_row = df['Current_Res'][df['Current_Res'].isin(['Alabama'])].index[0]
    last_row = df['Current_Res'][df['Current_Res'].isin(['Puerto Rico', 'Wyoming'])].index.max()
    df = df[~df.Current_Res.str.contains('Current')].loc[first_row:last_row]
    df['Year'] = np.full(len(df), int(yr))
    master_df = pd.concat([master_df, df])
    
# Calculating total mig to/from other states (and DC & Puerto Rico)
in_out_df = pd.DataFrame()
for year in master_df.Year.unique():
    df = master_df[master_df.Year == year]
    inmigs = []
    outmigs = []
    for state in df.columns[1:-1]:
        inmigs.append(sum(df[df.Current_Res == state].drop(state, axis=1).values[0].tolist()[1:-1]))
        outmigs.append(sum(df[state][df.Current_Res != state].values.tolist()))
    yr_df = pd.DataFrame({'State':df.columns[1:-1].values, 'Inmig':inmigs, 'Outmig':outmigs})
    yr_df['Year'] = np.full(len(df), year)
    in_out_df = pd.concat([in_out_df, yr_df])
    
in_out_df['Net_Mig'] = in_out_df.Inmig - in_out_df.Outmig
in_out_df.to_csv('Census_CA_states_in_out_mig_0518.csv', index=False)

ca = in_out_df[in_out_df.State == 'California']
ca.to_csv('Census_CA_in_out_mig_0518.csv', index=False)