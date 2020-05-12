# Calculating total annual CA in/out migration from IRS tax filing data (2012-2018)
import pandas as pd
import numpy as np
import os

inmig_12_18 = os.listdir('CA In 12_18')
outmig_12_18 = os.listdir('CA Out 12_18')

master_df2 = pd.DataFrame()
folders = ['CA In 12_18', 'CA Out 12_18']
counter = 0
for folder in [inmig_12_18, outmig_12_18]:
    for file in folder:
        yr = int('20'+ file[-6:-4])
        df = pd.read_csv(folders[counter] + '/' + file, usecols=[0,1,4,5])
        df.columns = ['State', 'Mig_Type', 'Returns', 'Exemptions']
        df = df[(df.State == 6) & (df.Mig_Type.isin([6,96,97]))].drop_duplicates(subset='Mig_Type')  # Code 97 used for foreign & same state (only want the first one, corresponding to foreign migrants)
        
        df['Year'] = np.full(len(df), yr)
        master_df2 = pd.concat([master_df2, df])
    counter += 1
    
master_df2['Type'] = ['In']*21 + ['Out']*21
mig_12_18 = pd.DataFrame({'Year':master_df2.Year.unique(), 
                          'Non_Mig':master_df2.Exemptions[(master_df2.Mig_Type == 6) & (master_df2.Type == 'In')].values, 
                          'Inmig_Exemp':master_df2.Exemptions[(master_df2.Mig_Type == 96) & (master_df2.Type == 'In')].values, 
                          'In_Dom_Exemp':master_df2.Exemptions[(master_df2.Mig_Type == 97) & (master_df2.Type == 'In')].values, 
                          'Outmig_Exemp':master_df2.Exemptions[(master_df2.Mig_Type == 96) & (master_df2.Type == 'Out')].values, 
                          'Out_Dom_Exemp':master_df2.Exemptions[(master_df2.Mig_Type == 97) & (master_df2.Type == 'Out')].values}).sort_values('Year')

mig_12_18.to_csv('IRS_CA_mig_1218.csv', index=False)