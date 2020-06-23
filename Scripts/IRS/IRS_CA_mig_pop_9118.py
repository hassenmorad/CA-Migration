# Combining cleaned IRS CA migration data & adding annual population figures
import pandas as pd
import re

irs9111 = pd.read_csv('IRS_CA_mig_9111.csv')
irs1218 = pd.read_csv('IRS_CA_mig_1218.csv')
comb = pd.concat([irs9111, irs1218])
comb_clean = comb.copy()  # Creating another CSV using only exemption figures (which cover tax filers and their dependants)

# CA 1991-2018 Population (source: http://www.dof.ca.gov/Forecasting/Demographics/Estimates/)
pops = '30143555	30722998	31150786	31418940	31617770	31837399	32207869	32657877	33140771	33721583	34256789	34725516	35163609	35570847	35869173	36116202	36399676	36704375	36966713	37223900	37594781	37971427	38321459	38622301	38952462	39214803	39504609	39740508'
pops = re.sub('\s',',',pops).split(',')
comb['Population'] = [int(p) for p in pops]
comb_clean['Population'] = [int(p) for p in pops]

comb['Net_Mig_Dom_Exemp'] = comb.In_Dom_Exemp - comb.Out_Dom_Exemp
comb['Rel_Mig_Dom_Exemp'] = round(comb.Net_Mig_Dom_Exemp / comb.Non_Mig, 4)
comb['Inmig_Exemp_pct_chg'] = comb.Inmig_Exemp.pct_change().abs()
comb['Outmig_Exemp_pct_chg'] = comb.Outmig_Exemp.pct_change().abs()

comb = comb.fillna(0)  # First row of pct_chg cols
comb.to_csv('IRS_CA_mig_pop_9118.csv', index=False)

# Clean file (only exemptions)
comb_clean = comb_clean[['Year', 'In_Dom_Exemp', 'Out_Dom_Exemp']]
comb_clean.columns = ['Year', 'Inmig', 'Outmig']
comb_clean['Net_Mig'] = comb_clean.Inmig - comb_clean.Outmig
comb_clean['Tot_Mig'] = comb_clean.Inmig + comb_clean.Outmig
comb_clean['Population'] = [int(p) for p in pops]
comb_clean.to_csv('IRS_CA_mig_pop_clean_9118.csv', index=False)