"""Example of how to perform a couple ratings calculations.

Use: 

    python example.py

Output:

    rating for 336.4 Oriole at 75C | 532 Amps
    rating for 336.4 Oriole at 75C | 64 MVA at 69 kV
    rating for 336.4 Oriole at 75C | 127 MVA at 138 kV

    rating for 795 Drake at 75C | 903 Amps
    rating for 795 Drake at 75C | 108 MVA at 69 kV
    rating for 795 Drake at 75C | 216 MVA at 138 kV

    rating for 1590 Falcon at 75C | 1349 Amps
    rating for 1590 Falcon at 75C | 161 MVA at 69 kV
    rating for 1590 Falcon at 75C | 322 MVA at 138 kV

"""
import ieee738
from ieee738 import ConductorParams
import logging

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
MOT = 75 # Maximum operating temperature of conductor in deg C

# -----------------------
# 336.4 ACSR 30/7 ORIOLE
# -----------------------
# Resistance from mfg is in ohms/mi - conver to ohms/ft for the IEEE738 kernel
acsr_falcon = {'TLo': 25, 'THi': 50, 'RLo': 0.2708/5280, 'RHi': 0.29740/5280, 
              'Diameter': 0.3705*2, 'Tc': MOT}

cp_oriole = ConductorParams(**ambient_defaults, **acsr_falcon)
con = ieee738.Conductor(cp_oriole)
rating_amps = con.steady_state_thermal_rating()

rating_69kv_mva = 3**0.5 * rating_amps * 69e3  / 1e6
rating_138kv_mva = 3**0.5 * rating_amps * 138e3  / 1e6

# Note the Southwire datasheet lists the allowable ampacity at 1359 Amps.
# Our calculations use different ambient conditions, but the ampacity should be simlar.
print()
print(f"rating for 336.4 Oriole at {MOT}C | {rating_amps:.0f} Amps")
print(f"rating for 336.4 Oriole at {MOT}C | {rating_69kv_mva:.0f} MVA at 69 kV")
print(f"rating for 336.4 Oriole at {MOT}C | {rating_138kv_mva:.0f} MVA at 138 kV")

# -----------------------
# 795 KCM ACSR Drake 26/7
# -----------------------
# Resistance from mfg is in ohms/mi - conver to ohms/ft for the IEEE738 kernel
acsr_drake = {'TLo': 25, 'THi': 50, 'RLo': 0.1166/5280, 'RHi': 0.12780/5280, 
              'Diameter': 0.5540*2, 'Tc': MOT}

cp_drake = ConductorParams(**ambient_defaults, **acsr_drake)
con = ieee738.Conductor(cp_drake)
rating_amps = con.steady_state_thermal_rating()

rating_69kv_mva = 3**0.5 * rating_amps * 69e3  / 1e6
rating_138kv_mva = 3**0.5 * rating_amps * 138e3  / 1e6

# Note the Southwire datasheet lists the allowable ampacity at 907 Amps.
# Our calculations use different ambient conditions, but the ampacity should be simlar.
print()
print(f"rating for 795 Drake at {MOT}C | {rating_amps:.0f} Amps")
print(f"rating for 795 Drake at {MOT}C | {rating_69kv_mva:.0f} MVA at 69 kV")
print(f"rating for 795 Drake at {MOT}C | {rating_138kv_mva:.0f} MVA at 138 kV")

# -----------------------
# 1590 ACSR 54/19 FALCON
# -----------------------
# Resistance from mfg is in ohms/mi - conver to ohms/ft for the IEEE738 kernel
acsr_falcon = {'TLo': 25, 'THi': 50, 'RLo': 0.0613/5280, 'RHi': 0.06780/5280, 
              'Diameter': 0.7725*2, 'Tc': MOT}

cp_falcon = ConductorParams(**ambient_defaults, **acsr_falcon)
con = ieee738.Conductor(cp_falcon)
rating_amps = con.steady_state_thermal_rating()

rating_69kv_mva = 3**0.5 * rating_amps * 69e3  / 1e6
rating_138kv_mva = 3**0.5 * rating_amps * 138e3  / 1e6

# Note the Southwire datasheet lists the allowable ampacity at 1359 Amps.
# Our calculations use different ambient conditions, but the ampacity should be simlar.
print()
print(f"rating for 1590 Falcon at {MOT}C | {rating_amps:.0f} Amps")
print(f"rating for 1590 Falcon at {MOT}C | {rating_69kv_mva:.0f} MVA at 69 kV")
print(f"rating for 1590 Falcon at {MOT}C | {rating_138kv_mva:.0f} MVA at 138 kV")

