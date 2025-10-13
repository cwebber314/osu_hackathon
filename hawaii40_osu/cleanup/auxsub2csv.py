"""Powerworld AUX file to CSV - only substations. This is useful if you want to pull GPS data from the busses.
"""
import re
import os.path as osp
import os
import io
import pandas as pd

fn = osp.join(os.pardir, os.pardir, 'hawaii40', 'Hawaii40_20231026.aux')
with open(fn, "r") as f:
    text = f.read()

pattern = r'^Substation\s*\s\((.*?)\)\s*{(.*?)}'
mm = re.search(pattern, text, re.DOTALL | re.MULTILINE)

cols = mm.groups()[0]
cols = cols.replace('\n', '')
cols = cols.replace(' ', '')
cols = cols.split(',')

body = mm.groups()[1]

df = pd.read_csv(io.StringIO(body), delim_whitespace=True, header=None, names=cols)
df.to_csv('hawaii40_auxsub.csv', index=False)