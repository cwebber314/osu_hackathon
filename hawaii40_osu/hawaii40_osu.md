# Hawaii40 OSU

This folder contains the model for the Hawaii40 synthic grid for the OSU Hackathon.
This notable enhancement to the original Texas model are:

- Line conductor and Maximum Operating Temperature (MOT) added to every line in the model
- Line ratings recalculated based on IEEE738 and conductor
 
Files:
- `cleanup\`: Do not use - scripts to transform the original Texas A&M model
- `gis\`
  - `oneline.qgz`: QGIS project which plots and styles the geoJSON 
  - `oneline_lines.goejson`: GIS information for lines.
  - `oneline_busses.geojson`: GIS information for busses.
- `ieee738\`: Material related to the IEEE738 ratings calculation the rating of overhead transmission lines.
  - `ieee738.py`: calculations kernel for steady state thermal rating
  - `example_ieee738.py`: Very simple example of calcating a rating of a transmission line.
  - `conductor_library.csv`: Conductor parameters of 
  - `conductor_ratings.csv`: 
  - `calculate_nominal_ratings.py`: Calculate the ratings of all the conductors in the `conductor_library.csv`
  - `ieee738-2006.pdf`

 