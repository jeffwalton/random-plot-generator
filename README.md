random-plot-generator
=====================

Python and R scripts to generate random study plot locations.

Random Point Generator program (version 0.1, April 11, 2007)

Generates a point shapefile of random points inside a polygon boundary.
Three random selection methods are available:
  Simple Random:   Random x and y values designate a point;
    the exact number of points specified are returned.
  Systematic Grid: Starting at an arbitrary (random) location,
    points are generated on an fixed x and y spacing.
    The spacing is determined by the number of points requested and
    the area of the boundary polygon. The number of points returned is
    approximately that requested.
  Randomized Grid: Same as the systematic grid method except x and y
    random offsets equal to the point spacing are added to each grid point.
    The number of points returned is approximately that requested.

Limitations: 
  1) The program uses the first polygon in the shapefile as the area of
    interest (aoi) boundary.

This program was written by Jeff Walton
                            USDA Forest Service
                            Northern Research Station
                            Syracuse, NY
                            http://nrs.fs.fed.us/4952/

Licensing: Since this program was written by a U.S. Government employee
  on government time, it is in the Public Domain and can be freely distributed.


This program requires the open source GDAL library http://www.gdal.org
GDAL and its Python bindings are available on Debian-based Linux distributions
  through the 'python-gdal' package.
On Windows, use the FWTools kit (http://fwtools.maptools.org/), which will
  install a Python interpreter and all of the required files. Run this program
  in the 'FWTools Shell'.

Run at the command line:  python RPG.py -n 200 aoiBoundary.shp randomPoints.shp
