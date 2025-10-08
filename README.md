# OSU Hackathon

## Environment

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
You can view the case data in the PowerWorld Viewer - which is helpful to visualize the powerflows and explore the data.
The original data is provided in the `hawaii40\` folder.

We've exported the synthetic grid to a set of CSV and JSON files which are eaier to consume. 
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

The rating of the line is based on conductor properties like resistance and the ambient conditions. For example, a high windspeed provides
convective cooling and and allows more current to flow through the conductor before it reach it's maximum operating temperature.

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

## Daily Load profiles

Daily Load follows roughly a sine wave with a 6pm peak and 3am valley. Assume ~30% swing from min to max - eg 700 MW min, 1000 MW max.
Load also changes based on weather. For example, in the summer hotter days have higher load. This project doesn't provide a relationship
or data between ambient temperature and load - this analysis may ignore the relationship or make a guess like 
"no load change between 15C - 25C and 1% load increase per degree between 25C - 40C"

For this project we've provided 3 load/gen profiles:
- nominal: origial values from model
- min: 15% lower than nominal
- max: 15% higher than nominal

Note that as load scales up and down, the generation must also scale up and down otherwise the the model won't converge and just 
doesn't make sense. The slack buses in the model allow for small mismatches between load and gen.

## Files

Folder          | Description
----------------|-----------------------------------------
`hawaii40\`     | Original model from Texas A&M. :warning: Reference only - do not use the ratings in this case
`hawaii40_osu`  | Modified model for hackathon

## Story

The model shows the load under very normal conditions - none of the lines are overloaded.
As environment conditions worsen (ie ambient temperature increases), the rating of lines
will start to decrease. At some point lines will start to overload.  Questions to  
answer:
- at what point does everything fall apart?
  - Ambient temp increase? Wind speed decrease
- What gets overloaded first as ambient temperature increases
  - IRL we use these weakneses to decide what to improve. 
- For a certain set of ambient conditions how stressed is the system?
  - 90% danger
  - 60-90% caution
  - 0-60% Nominal  

^ We want to visualize this data. Probably there's a geospatial component to the visulazion, 
but maybe it's tabular, or maybe both. 


Bonus ideas (Chip):
- ~~Load profiles through the day (too much work)~~
- case solves, take outages (maybe, requires learning loadflow library)

When we operate the grid we are always worried about what happens when loose a part of 
a network.  Use the [pypsa](https://github.com/PyPSA/PyPSA) library or other powerflow engine like [pypower](https://github.com/rwl/PYPOWER) or [matpower](https://matpower.org/) 
to evaluate what happens to the network when you lose a transmission line.  Which lines
are the most important to the network? 

AEP Operations always know if we lose "Line A" then "Line B, C" overload. 

- The main challenge answers the question what is overloaded as ambient conditions change?
- The bonus challenge answers the question what will be overloaded if we lose any line in the network. 


## References

- Southwire datasheet for ACSR [link](# https://www.southwire.com/wire-cable/bare-aluminum-overhead-transmission-distribution/acsr/p/ALBARE6)
- [IEEE738](ieee738/ieee738-2006.pdf)
- [SPP Price Countour Map](https://pricecontourmap.spp.org/pricecontourmap/) - contains daily load graphs   