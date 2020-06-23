# Calculating total annual CA in/out domestic migration (i.e. US only) from IRS tax filing data (1991-2011)
import pandas as pd
import numpy as np
import os
import re

inmig_91_11 = os.listdir('CA In 91_11')
outmig_91_11 = os.listdir('CA Out 91_11')

master_df1 = pd.DataFrame()
folders = ['CA In 91_11', 'CA Out 91_11']
counter = 0
for folder in [inmig_91_11, outmig_91_11]:
    for file in folder:
        # Identifying year from different file names
        num = re.findall('\d+', file)[0][-2:]
        if int(num) > 20:
            yr = int('19' + num)
        else:
            yr = int('20' + num)
        
        # Extracting these cols: mig state code, mig state name, returns, exemptions
        if yr < 1993:
            cols = [0,2,3,5]
        elif yr > 2009:
            cols = [1,3,4,5]
        else:
            cols = [0,2,3,4]
            
        df = pd.read_excel(folders[counter] + '/' + file, usecols=cols)
        df.columns = ['State_Code', 'Mig_Type', 'Returns', 'Exemptions']
        df = df[df['State_Code'].isin(['06','96','63','57',6,96,63,57])]  # Including 63 for different mig state code in 1993 files (63 & 96=residents; 6=domestic migrants; 57=foreign migrants)
        if yr in [1994,1995]:
            df['State_Code'] = [96,57,6]
        
        df['Year'] = np.full(len(df), yr)
        master_df1 = pd.concat([master_df1, df])
    counter += 1
    
master_df1['Type'] = ['In']*63 + ['Out']*63
master_df1['State_Code'] = master_df1['State_Code'].astype(str)
master_df1 = master_df1.sort_values(['Type','Year'])

totals = master_df1[master_df1['State_Code'].isin(['6','06'])]
mig_tot = master_df1[master_df1['State_Code'].isin(['63','96'])]
mig_for = master_df1[master_df1['State_Code'].isin(['57'])]

mig_91_11 = pd.DataFrame({'Year':master_df1.Year.unique(),
                          'Non_Mig':totals.Exemptions[totals.Type == 'In'].values,
                          'Inmig_Exemp':mig_tot.Exemptions[mig_tot.Type == 'In'].values,
                          'Outmig_Exemp':mig_tot.Exemptions[mig_tot.Type == 'Out'].values,
                          'In_Foreign_Exemp':mig_for.Exemptions[mig_for.Type == 'In'].values,
                          'Out_Foreign_Exemp':mig_for.Exemptions[mig_for.Type == 'Out'].values})

mig_91_11['In_Dom_Exemp'] = mig_91_11.Inmig_Exemp - mig_91_11.In_Foreign_Exemp
mig_91_11['Out_Dom_Exemp'] = mig_91_11.Outmig_Exemp - mig_91_11.Out_Foreign_Exemp
mig_91_11 = mig_91_11[['Year', 'Non_Mig', 'Inmig_Exemp', 'In_Dom_Exemp', 'Outmig_Exemp', 'Out_Dom_Exemp']]

mig_91_11.to_csv('IRS_CA_mig_9111.csv', index=False)