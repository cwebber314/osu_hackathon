"""Add Unique Line Name (eg L20) to lines geojson 

Input geojson file: gis\oneline_lines_noname.geojson
Input name <-> LineName mapping: csv\lines.csv

Output file: gis\oneline_lines.geojson
"""
import json
import pandas as pd
import os.path as osp
import pdb

df = pd.read_csv(osp.join('csv', 'lines.csv'))

geofn_in = osp.join('gis', 'oneline_lines_noname.geojson')
with open(geofn_in, 'r') as f:
    geo = json.load(f)

# Set the index so you can lookup by branch_name easier.
df = df.set_index('branch_name')

for feat in geo['features']:
    line_name = feat['properties']['LineName']
    # lookup the unique name in lines.csv - like L23
    name = df.loc[line_name]['name'] # 
    feat['properties']['Name'] = name

# pdb.set_trace()

with open(osp.join('gis', 'oneline_lines.geojson'), 'w') as f:
    json.dump(geo, f, indent=2)
