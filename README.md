# California Migration Analysis

This repository contains all files used to analyze issues California's migration patterns, resulting in the following research report:
[**Is California Out Migration Fueled By Unaffordable Housing?**](https://hassenmorad.github.io/CA_migration.html)

## Data Sources:
1. Migration
    - [**IRS**](https://www.irs.gov/statistics/soi-tax-stats-migration-data): state and county level migration figures for tax filers (1990-2018)
    - [**Census API**](https://www.census.gov/data/developers/data-sets.html): 5-yr county-level estimates
    
    *Note: Census data was assumed to be the more reliable of the two sources, since IRS data is based on tax filings and Americans don't file for taxes for a variety of reasons). I chose to include IRS data since it extends back to 1990, whereas Census data only extends back to 2005. Details on how I adjusted IRS migration figures and combined them with Census data can be found in the following [notebook](https://github.com/hassenmorad/CA-Migration/blob/master/Notebooks/Combining%20Census%20%26%20IRS.ipynb)
2. Population
    - [**California Department of Finance**](http://www.dof.ca.gov/Forecasting/Demographics/Estimates/)
3. Income
    - [**Census API**](https://www.census.gov/data/developers/data-sets.html): 5-yr county-level estimates
4. Housing
    - [**Census API**](https://www.census.gov/data/developers/data-sets.html): 5-yr county-level estimates

### Misc:
- Scripts of data cleaning and analysis are stored in the "Scripts" folder
- Altair chart code is stored in the "Notebooks" folder
