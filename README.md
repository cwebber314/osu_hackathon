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
maximum operating temperature of the line. We call this the rating of the transmission line.  

The rating of the line is based on the conductor properties and the ambient conditions. For example, a high windspeed provides
convective cooling and and allows more current to flow through the conductor before it reach it's maximum operating temperature.

Even though ratings are calculated in Amps, they are usually converted to MVA for anlalysis using the following format.  

$$ S_{MVA} = \sqrt(3) \cdot I_{Amps} \cdot V \cdot 10^{-6} $$

For example:
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

## References

- Southwire datasheet for ACSR [link](# https://www.southwire.com/wire-cable/bare-aluminum-overhead-transmission-distribution/acsr/p/ALBARE6)
- [IEEE738](ieee738/ieee738-2006.pdf)
- [SPP Price Countour Map](https://pricecontourmap.spp.org/pricecontourmap/) - contains daily load graphs   