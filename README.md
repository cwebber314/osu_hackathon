# OSU Hackathon

## Important Data

### Line Model 

`hawaii40_osu\csv\lines.csv`

Columns:
- `name`: Unique name of the line - use this to match data between the the GIS data. PyPSA uses this as the index
- `bus0`: Reference to bus. This is one endpoint of the line.  
- `bus1`: Reference to bus. This is the other endpoint of the line
- `s_nom`: Rating in MVA for the line. This is how much flow the line can handle before something bad happens.
- `conductor`: Conductor used in the line. This is used to calculate the rating of the line `s_nom` 
- `MOT`: Maximum Operating Temperature of the line. This is used to calculate the rating of the line `s_nom`  
- `branch_name`: Readable name for the branch/line

Note on kV: The nominal operating voltage is not included in the `lines.csv` file because it is a property of the bus.
The psuedo-sql to get the the nomkv looks like this:

```sql
SELECT bus.v_nom AS nom_kv
FROM lines
INNER JOIN busses 
  ON lines.bus0 = busses.name
```

Note that bus0 and bus1 have the same kV by definition for a line. 

### Line GIS data

See `hawaii40_osu\gis\oneline_lines.geojson`

Keys:
- `Features.properties.Name`: Reference to the `name` column in `lines.csv` - use this to connect the two data sets.
- `Features.properties.BusNumFrom`: Same as `bus0` column in `lines.csv`
- `Features.properties.BusNumTo`: Same as `bus1` column in `lines.csv` 


### Nominal Line flows

See `hawaii40_osu\line_flows_nominal.csv`

Columns: 
- `name`: Unique name of line
- `p0_nominal`: Line flow in MVA 

A lot of this project is based on comparing the rating of a line `s_nom` with the flow on the line `p0`, 
let's take a quick look at what this compare looks like for the nominal data.

From line_flows_nominal.csv:
```csv
name,p0_nominal
L0,79.2
L1,79.2
L2,22.4
```

From lines.csv:
```csv
name,s_nom
L0,228
L1,228
L2,172
```

If we line up the flows and the rating we get a table that looks like this

Line Name | flow (p0) | rating (s_nom) | Loading
----------|-----------|----------------|----------
L0        | 79.2      | 228            | 35%
L1        | 79.2      | 228            | 35%
L2        | 22.4      | 172            | 13%



## Python Environment

You should have a recent version of python to run the ieee738 kernel and other reference code.
We used Python 3.12, but any recent version will do. 

Install the python libraries:
```sh
pip install pandas jupyterlab pypsa pydantic 
```

Or if you go the virtualenv route:
```sh
python -m venv .venv
.venv/scripts/activate
pip install -r requirements.txt
```

Other optional tools:
- [PowerWorld viewer](https://www.powerworld.com/download-purchase/demo-software/powerworld-viewer-download) - Windows only. Used to view the network at nominal conditions.
- [QGIS LTR](https://qgis.org/download/) for exploring/editing GIS data. I used this to tweak
  the line and bus locations and properties. It's got a bit of a learning curve and may not
  be helpful.

## Hawaii Synthetic Grid

The example system is taken from the Texas A&M [electric grid testcase](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/). 
The original data is provided in the `hawaii40\` folder. You can view the case data in the PowerWorld Viewer - which is helpful to visualize
the powerflows and explore the data.

We've modifed and exported the grid to a set of CSV and JSON files which are eaier to consume.
- `hawaii40_osu\csv`: Model data in PyPSA compatible CSV format.
- `hawaii40_osu\gis`: Export of lines to geoJSON. 

For this project, the model has been slightly changed from the original:
- Overhead conductor and max operating temperature associated with each line
- Ratings re-calculated based the overhead conductor. The new ratings are close to the original rating.

Note that the coordinates for the transmission lines do not match the physical line routes. 

Screenshots:
- [Screenshot of the case in Powerworld](./hawaii40_powerworld.png)
- [Screenshot of the case in GIS tools](./hawaii40_gis.png)

## IEEE-738 Overhead conductor ratings

The IEEE-738 standard calculates how much current can flow through an overhead line before it exceeds the
maximum operating temperature (MOT) of the line. We call this the rating of the transmission line.  

See the [iee738_primer](ieee738_primer.md) for a brief introduciton to the principle behind
the calculation and line ratings.

The rating of the line is based on conductor properties like resistance and the ambient conditions. For example, a high windspeed provides
convective cooling and and allows more current to flow through the conductor before it reach it's maximum operating temperature.

### Python ieee738 kernel

See the `ieee738\example_ieee738.py` for several example calculations.

Here is a minimal code sample:
```py
import ieee738
from ieee738 import ConductorParams

ambient_defaults = {
    'Ta': 25,
    'WindVelocity': 2.0, 
    'WindAngleDeg': 90,
    'SunTime': 12,
    'Date': '12 Jun',
    'Emissivity': 0.8,
    'Absorptivity': 0.8,
    'Direction': 'EastWest',
    'Atmosphere': 'Clear',
    'Elevation': 1000,
    'Latitude': 27,
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
```

Environment Parameters:
- `Ta`: Ambient temperature in degC
- `WindVelocity`: Wind Velocity in ft/sec
- `WindAngleDeg`: Wind Angle relative to the line. I like to keep this one constant because
line route typically changes and the angle isn't meaningful.
- `SunTime`: What hour of the day between 0-24 - determines solar heat gain
- `Date`: Determines angle of the sun which determines solar heat gain
- `MOT`: Maximum Operating Temperature of the line conductor in degC. This is called Tc (Temperature of Conductor in the IEEE738 spec)

Parameters you may want to ignore:
- `Emissivity`: Property of the conductor - doesn't vary with ambient comditions
- `Absorptivity`: Property of the conductor - doesn't vary with ambient comditions
- `Direction`: Constant - doesn't vary with ambient comditions
- `Atmosphere`: Trivial Impact. We typically worst case of clear.
- `Elevation`: Constant - doesn't vary with ambient comditions. Also I didn't include elevation data in the data. There may be room to do something clever and create a more general solution.  
- `Latitude`: Trivial Impact across our region. If you include it in you solution it would be more applicable to networks in other locations.

### Conductor Params

See `ieee738\conductor_library.csv` for conductor properties needed for the calculation.

Columns:
- `ConductorName`: Name of the conductor. Exactly matches the conductor name in `lines.csv`
- `RES_25C`: Resistance at 25C in Ohms/Mi
- `RES_50C`: Resistance at 50C in Ohms/Mi
- `CDRAD_IN`: Conductor radius in inches.
- `CDGMR_ft`: NOT USED in the rating calculation.

### Amps and MVA

Even though ratings are calculated in Amps, they are usually converted to MVA which is more meaningful to engineers.
Use the following equations to convert from Amps to 3-phase MVA:  

$$ S_{MVA} = \sqrt(3) \cdot I_{Amps} \cdot V \cdot 10^{-6} $$

For example in python:
```py
rating_amps = 900 # 900 Amps is the approx raitng of 795 KCM ACSR 26/7 

# At 69 kV 
V = 69e3 # 69 kV = 69,000 V
rating_mva = 3**0.5 * rating_amps * V * 1e-6
print(f"{rating_mva:.0f}") # 108 MVA

# At 138 kV 
V = 138e3 # 69 kV = 69,000 V
rating_mva = 3**0.5 * rating_amps * V * 1e-6
print(f"{rating_mva:.0f}") # 215 MVA
```

## Story / Challenge

This section contains some of my notes on the challenge. 

The model shows the load under very normal conditions - none of the lines are overloaded.
As environment conditions worsen (ie ambient temperature increases), the rating of lines
will start to decrease. At some point lines will start to overload.  

Questions to answer:
- At what point do lines start to overload? 
  - Do things start to overload at ambient temps of 40C, 50C?
  - What if the wind stops blowing?  
- What lines get overloaded first as ambient temperature increases?
  - IRL we use these weakneses to decide what to improve. 
- For a certain set of ambient conditions how stressed is the system?
  - 90% Critical
  - 60-90% caution
  - 0-60% Nominal  

How can we visualize this data?  There's probalby a geospatial component - we probably show the potential overloads 
on a map. Keep in mind that our synthetic grid is much smaller than AEP transmission footprint in the Ohio region. 
Ideally the visualization scales to view issues on 1000's of lines - so some sort of tabular view may be helpful.

### Contingencies (Bonus)

Overview:
- The main challenge answers the question what is overloaded as ambient conditions change?
- The bonus challenge answers the question what will be overloaded if we lose any line in the network. 

The eletric transmission system is designed to survive the loss of any element - we call these N-1 contingencies.
In our example system we see that in nominal conditions almost all the lines are loaded under 50%. 
Ambient conditions have to get pretty bad before lines start to overload. 

As we operate the grid we constantly monitor what will happen when we lose an transmission line.
For example if we lose the line from "ALOHA138 TO  HONOLULU138 CKT 1" does anything overload? Is 
anything close to overloading? 

For a set of ambient conditions, you should evaluate the N-1 contingencies. Take each line out 
of service, solve the case, and evaluate the overloads. 

Example output of a N-1 contingencies analysis
```
For loss of "ALOHA138 TO HONOLULU138 CKT 1"

Ratings Issues:
"ALOHA138 TO HONOLULU138 CKT 2" 95% 


For loss of "FLOWER69 TO HONOLULU69  CKT 1"

Ratings Issues:
"FLOWER69 TO HONOLULU69  CKT 2" 92% 
"SURF69 TO TURTLE69 CKT 1" 84%
"SURF69 TO COCONUT69 CKT 1" 81%
```

Running the contingency analysis requires a powerflow solver. Here are a couple open source options to 
solve power-flow cases: 
- [PyPSA](https://github.com/PyPSA/PyPSA) - example contingency and case solve included.
- [matpower](https://matpower.org/) - not tested requires matlab 
- [pypower](https://github.com/rwl/PYPOWER) - python port of matpower not tested 

Commercial tools like PSSE, PLSF, and PowerWorld can also be used to solve powerflow models, but
have very limited options for free use and are typically cumbersome to integrate with another 
applicaiton.

### Daily Load profiles (Bonus)

In the actual system, load and gen change throughout the day. For this hackathon you can 
ignore changes in load throughout the day. 

However, if you want to consider load/gen changes through the day stress the
system see the notebook `hawaii40\pypsa_load_scale.ipynb` to get started. This
requires using the PyPSA library to changing the model and solve the case with
each load/generation dispatch change.

## References

- Southwire datasheet for ACSR [link](# https://www.southwire.com/wire-cable/bare-aluminum-overhead-transmission-distribution/acsr/p/ALBARE6)
- [IEEE738](ieee738/ieee738-2006.pdf)
- [SPP Price Countour Map](https://pricecontourmap.spp.org/pricecontourmap/) - contains daily load graphs

## Visualization Ideas

A couple visualization examples:
- Powerworld shows the loading with a pie chart on each line and colors the chart based on severity. [Powerworld Example](powerworld_line_capacity_example.png)
- SPP shows congestion icons on a map and links it to table data. See the [screenshot](spp_lmp_example.png) or the live [website](https://pricecontourmap.spp.org/pricecontourmap/)
  - NOTE: This app is very different than what we are doing, but it's a decent example of combining table and GIS data for the grid. 

## PyPSA notes

PyPSA just released 1.x - I recommend using the 1.x release - mostly because the online docs 
point to this version. It's okay to ignore warnings about the model being created with v0.35.2.

I haven't done any testing with pypower or matpower to solve the powerflow cases. 
Unless you have prior experience with one of these solvers, I strongly recommend you 
stay with PyPSA if you tackle the bonus objectives.

Note that you can complete the entire challenge without using the PyPSA library. 
Solving the model again is only required if you:
- Take a line out of service
- Change the load/generation