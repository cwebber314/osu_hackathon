# OSU Hackathon

## Environment

You should have a recent version of python to run the ieee738 kernel and other reference code.
We used Python 3.12, but any recent version will do. 

Python libraries:
```sh
pip install pandas jupyterlab pypsa
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
- Ratings re-calculated based the overhead conductor

The ratings are close to the original rating 

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

## References

- Southwire datasheet for ACSR [link](# https://www.southwire.com/wire-cable/bare-aluminum-overhead-transmission-distribution/acsr/p/ALBARE6)
- [IEEE738](ieee738/ieee738-2006.pdf)
