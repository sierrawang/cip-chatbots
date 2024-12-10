import pandas as pd

# HDI data download from https://hdr.undp.org/data-center/human-development-index#/indicies/HDI
# on May 23, 2024
un_data = pd.read_excel('../misc_data/HDR23-24_Statistical_Annex_HDI_Table.xlsx', skiprows=5, header=0)

def convert_country_name(country):
    switcher = {
            'Bolivia': 'Bolivia (Plurinational State of)', 
            'Iran': 'Iran (Islamic Republic of)', 
            'Venezuela': 'Venezuela (Bolivarian Republic of)', 
            'Czech Republic': 'Czechia', 
            'Russia': 'Russian Federation', 
            'Ivory Coast': "Côte d'Ivoire", 
            'Tanzania': 'Tanzania (United Republic of)', 
            'Turkey': 'Türkiye', 
            'South Korea': 'Korea (Republic of)', 
            'Hong Kong': 'Hong Kong, China (SAR)', 
            'Vietnam': 'Viet Nam', 
            'Myanmar [Burma]': 'Myanmar',
            'Syria': 'Syrian Arab Republic', 
            'Cape Verde': 'Cabo Verde', 
            'Republic of the Congo': 'Congo (Democratic Republic of the)', 
            'Brunei': 'Brunei Darussalam', 
            'Swaziland': 'Eswatini (Kingdom of)', 
            'New Caledonia': None,
            'Kosovo': None, 
            'Gibraltar': None, 
            'French Guiana': None, 
            'Somewhere on Earth': None, 
            'Cayman Islands': None, 
            'Guam': None, 
            'Taiwan': 'Korea (Republic of)', # This is a dummy value that might be close to accurate... 
            'Puerto Rico': None, 
            'Jersey': None, 
            'U.S. Virgin Islands': None,
            'Monaco': None # Monaco is actually listed in the data, but there isn't an HDI for it
        }
    return switcher.get(country, country)

def get_hdi(country):
    official_country_name = convert_country_name(country)
    hdi = un_data[un_data['Country'] == official_country_name]['Value']

    if hdi.empty:
        return -1

    return float(hdi.values[0])

HDI_boundaries = {
    'Low': [0, 0.55],
    'Medium': [0.55, 0.699],
    'High': [0.7, 0.799],
    'Very High': [0.8, 1]
}

def get_hdi_category(hdi):
    if hdi < 0:
        return 'Unknown'

    for key, value in HDI_boundaries.items():
        if value[0] <= hdi <= value[1]:
            return key
        
    assert False, "HDI value is invalid"