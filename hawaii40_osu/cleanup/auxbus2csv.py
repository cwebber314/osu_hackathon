"""Powerworld AUX file to CSV - only bisses. This is useful if you want to pull GPS data from the busses
or create a network from a script.
"""
import re
import os.path as osp
import os
import io
import pandas as pd

fn = osp.join(os.pardir, os.pardir, 'hawaii40', 'Hawaii40_20231026.aux')
with open(fn, "r") as f:
    text = f.read()

pattern = r'^Bus\s*\s\((.*?)\)\s*{(.*?)}'
mm = re.search(pattern, text, re.DOTALL | re.MULTILINE)

# print(mm.groups()[0])
# print(mm.groups()[1])

cols = mm.groups()[0]
cols = cols.replace('\n', '')
cols = cols.replace(' ', '')
cols = cols.split(',')

body = mm.groups()[1]

df = pd.read_csv(io.StringIO(body), sep='\\s+', header=None, names=cols)
df.to_csv('hawaii40_auxbus.csv', index=False)