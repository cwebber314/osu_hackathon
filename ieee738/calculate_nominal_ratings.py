"""Calcualte the nominal ratings of all the conductors in the conductor_library.csv
Create the output file conductor_ratings.csv

I'm using this to infer the conductor from the existing case rating 
"""
import ieee738
import pandas as pd
from ieee738 import Conductor
from ieee738 import ConductorParams
import pdb

ambient_defaults = {
    'Ta': 25,
    'WindVelocity': 2.0, 
    'WindAngleDeg': 90,
    'SunTime': 12,
    'Elevation': 1000,
    'Latitude': 27,
    'SunTime': 12,
    'Emissivity': 0.8,
    'Absorptivity': 0.8,
    'Direction': 'EastWest',
    'Atmosphere': 'Clear',
    'Date': '12 Jun',
    }


df = pd.read_csv('conductor_library.csv')
ratings = []
for i, row in df.iterrows():
    for MOT in (75, 80, 85, 90, 95):
        cond = {'TLo': 25, 
                'THi': 50, 
                'RLo': row.RES_25C/5280,
                'RHi': row.RES_50C/5280,
                'Diameter': 2.0*row['CDRAD_in'], 
                'Tc': MOT
                }
        cp = ConductorParams(**ambient_defaults, **cond)
        con = Conductor(cp)
        rating_amps = con.steady_state_thermal_rating()
        rating_mva_69 = 3**0.5 * rating_amps * 69e3 * 1e-6
        rating_mva_138 = 3**0.5 * rating_amps * 138e3 * 1e-6
        
        # Please forgive the mixed CamelCase and snake_case - some of this data comes from another 
        # system with differen naming conventions
        ratings.append({'ConductorName': row.ConductorName, 
                        'MOT': MOT,
                        'RatingAmps': int(rating_amps),
                        'RatingMVA_69': int(rating_mva_69),
                        'RatingMVA_138': int(rating_mva_138)})

# pdb.set_trace()
df = pd.DataFrame.from_records(ratings)
df.to_csv('conductor_ratings.csv', index=False)
