# IRS CA in-migration from other states (1991-2018)
import pandas as pd

irs9111 = pd.read_csv('IRS_CA_states_mig_9111.csv')
irs1218 = pd.read_csv('IRS_CA_states_mig_1218.csv')
irs = pd.concat([irs9111,irs1218]).sort_values(['Type','Year','Exemptions'], ascending=[True,True,False])

inmig = irs[irs.Type == 'In']
outmig = irs[irs.Type == 'Out']
inmig = inmig.rename({'Exemptions':'Inmig'}, axis=1)
outmig = outmig.rename({'Exemptions':'Outmig'}, axis=1)

comb = pd.merge(inmig, outmig, on=['Year','State']).drop(['State_FIPS_x', 'Type_x', 'State_FIPS_y', 'Type_y'], axis=1)
comb['Net_Mig'] = comb.Inmig - comb.Outmig
comb = comb.sort_values(['Year','Net_Mig'], ascending=[True,False])
comb = comb[['Year', 'State', 'Inmig', 'Outmig', 'Net_Mig']]
comb.to_csv('IRS_CA_states_mig_9118.csv', index=False)