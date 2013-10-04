#
# Random Point Generator program (version 0.1, April 11, 2007)
#
# Generates a point shapefile of random points inside a polygon boundary.
# Three random selection methods are available:
#   Simple Random:   Random x and y values designate a point;
#     the exact number of points specified are returned.
#   Systematic Grid: Starting at an arbitrary (random) location,
#     points are generated on an fixed x and y spacing.
#     The spacing is determined by the number of points requested and
#     the area of the boundary polygon. The number of points returned is
#     approximately that requested.
#   Randomized Grid: Same as the systematic grid method except x and y
#     random offsets equal to the point spacing are added to each grid point.
#     The number of points returned is approximately that requested.
#
# Limitations: 
#   1) The program uses the first polygon in the shapefile as the area of
#     interest (aoi) boundary.
#
# This program was written by Jeff Walton
#                             USDA Forest Service
#                             Northern Research Station
#                             Syracuse, NY
#                             http://nrs.fs.fed.us/4952/
#
# Licensing: Since this program was written by a U.S. Government employee
#   on government time, it is in the Public Domain and can be freely distributed.
#
#
# This program requires the open source GDAL library http://www.gdal.org
# GDAL and its Python bindings are available on Debian-based Linux distributions
#   through the 'python-gdal' package.
# On Windows, use the FWTools kit (http://fwtools.maptools.org/), which will
#   install a Python interpreter and all of the required files. Run this program
#   in the 'FWTools Shell'.
#
# Run at the command line:  python RPG.py -n 200 aoiBoundary.shp randomPoints.shp
#
#

import sys
import os
from random import seed, uniform
from math import sqrt
import gdal
import ogr

#############################################################################
def Usage():
    print 'Usage: RPG.py [-m method] -n numberPts inShapefile outShapefile'
    print "    method = 'r'  (Simple Random) "
    print "             'sg' (Systematic Grid) "
    print "             'rg' (Randomized Grid) (default) "
    print
    sys.exit(1)


def SimpleRandom( n, aoiPoly, min_x, max_x, min_y, max_y ):
    # initialize random number generator
    seed()

    # initilaize point list
    ptList = []

    i = 1
    while i <= n:

        # make a point
        aPoint = ogr.Geometry( ogr.wkbPoint)

        aPoint.SetPoint(0, uniform(min_x, max_x), uniform(min_y, max_y) )

        if aPoint.Within( aoiPoly ):
            ptList.append(aPoint)

            i = i + 1
    return ptList


def Gridded( n, aoiPoly, min_x, max_x, min_y, max_y, offSet=None ):

    if offSet == 'random':
        # initialize random number generator
        seed()

    # Calculate grid spacing
    aoiArea = aoiPoly.GetArea()
    if aoiArea <= 0.001:
        print 'ERROR: function: Gridded()  aoiArea <= 0.001  -- area too small'
        sys.exit(1)
    pointSpacing = sqrt( aoiArea / n )
    print 'pointSpacing =', pointSpacing

    # initilaize point list
    ptList = []

    y = min_y + (pointSpacing / 2.0)
    while y <= max_y:
        x = min_x + (pointSpacing / 2.0)
        while x <= max_x:
            # make a point
            aPoint = ogr.Geometry( ogr.wkbPoint)
            if offSet == 'random':
                aPoint.SetPoint(0, uniform(x - (pointSpacing / 2.0), x + (pointSpacing / 2.0)),
                                   uniform(y - (pointSpacing / 2.0), y + (pointSpacing / 2.0)) )
            else:
                aPoint.SetPoint(0, x, y)
            if aPoint.Within( aoiPoly ):
                ptList.append(aPoint)

            x = x + pointSpacing

        y = y + pointSpacing

    return ptList
   

#############################################################################
# Argument processing.

method = None
numberPts = None
inShapefile = None
outShapefile = None
method = 'rg'

i = 1
while i < len(sys.argv):
    arg = sys.argv[i]

    if arg == '-m':
        method = sys.argv[i+1]
        i = i + 1
        
    elif arg == '-n':
        numberPts = int(sys.argv[i+1])
        i = i + 1
        
    elif inShapefile is None:
	inShapefile = arg

    elif outShapefile is None:
	outShapefile = arg

    else:
	Usage()

    i = i + 1

if inShapefile is None:
    Usage()
elif outShapefile is None:
    Usage()
elif (method is None) or ( (method <> 'r') and (method <> 'sg') and (method <> 'rg') ):
    method = 'rg'
elif numberPts is None:
    Usage()
elif numberPts < 1:
    print numberPts, 'Error: numberPts is less than 1'
    Usage()


if method == 'r':
    methodString = 'Simple Random'
elif method == 'sg':
    methodString = 'Systematic Grid'
else:
    methodString = 'Randomized Grid'

print 'Method:', method, '(', methodString, ')'
print 'Approximate number of points to select:', numberPts
print 'Input Shapefile:', inShapefile
print 'Output Shapefile:', outShapefile
print


#############################################################################
# Open the datasource to operate on.

in_ds = ogr.Open( inShapefile, update = 0 )

# Use only first layer
in_layer = in_ds.GetLayer( 0 )   # ToDo: handle more than one layer?

in_defn = in_layer.GetLayerDefn()
if in_defn.GetGeomType() <> ogr.wkbPolygon:
   print 'ERROR: inShapefile is not a polygon'
   print
   Usage()


#############################################################################
#	Create output point file with same spatial reference.

shp_driver = ogr.GetDriverByName( 'ESRI Shapefile' )

if os.path.exists(outShapefile):
    shp_driver.DeleteDataSource( outShapefile )

shp_ds = shp_driver.CreateDataSource( outShapefile )

shp_layer = shp_ds.CreateLayer( 'RandomPoints',
                                geom_type = ogr.wkbPoint,
                                srs = in_layer.GetSpatialRef() )

#############################################################################
#   

# Get Input Extent
in_extent = in_layer.GetExtent()
min_x = in_extent[0]
min_y = in_extent[2]
max_x = in_extent[1]
max_y = in_extent[3]

# Get the polygon
in_feat = in_layer.GetNextFeature()  # ToDo: handle more than one feature

boundaryPolygon = in_feat.GetGeometryRef()

# ToDo: check boundary poly does not have zero (small) area
print 'AOI Boundary Area:', boundaryPolygon.GetArea(), in_layer.GetSpatialRef().GetLinearUnitsName(), '^2'
print

# Make some fields in the output file
fd_Id = ogr.FieldDefn('Id',ogr.OFTInteger)
fd_Id.SetWidth(8)
shp_layer.CreateField( fd_Id )

fd_X = ogr.FieldDefn('X',ogr.OFTReal)
fd_X.SetWidth(16)
fd_X.SetPrecision(3)
shp_layer.CreateField( fd_X )

fd_Y = ogr.FieldDefn('Y',ogr.OFTReal)
fd_Y.SetWidth(16)
fd_Y.SetPrecision(3)
shp_layer.CreateField( fd_Y )

shp_defn  = shp_layer.GetLayerDefn()
field_Id = shp_defn.GetFieldIndex('Id')
field_X = shp_defn.GetFieldIndex('X')
field_Y = shp_defn.GetFieldIndex('Y')


# Generate a list of points
if method == 'r':
    ptList = SimpleRandom( numberPts, boundaryPolygon, min_x, max_x, min_y, max_y )
elif method == 'sg':
    ptList = Gridded( numberPts, boundaryPolygon, min_x, max_x, min_y, max_y, None )
else:
    ptList = Gridded( numberPts, boundaryPolygon, min_x, max_x, min_y, max_y, 'random' )


# Write points to output shapefile
id = 0
for p in ptList:
    id = id + 1

    out_feat = ogr.Feature( feature_def = shp_layer.GetLayerDefn() )

    out_feat.SetField(field_Id, id)
    out_feat.SetField(field_X, p.GetX(0))
    out_feat.SetField(field_Y, p.GetY(0))
    out_feat.SetGeometry(p)

    shp_layer.CreateFeature( out_feat )
    out_feat.Destroy()


shp_layer.CommitTransaction()
shp_layer.SyncToDisk()

print id, 'points generated'
print 'Done.'