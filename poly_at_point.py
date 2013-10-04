#
# poly_at_point.py (version 0.0, April 17, 2007)
#
# Generates a polygon centered at each point in a pointShapefile.
#
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
# Run at the command line:  python poly_at_point.py type size pointShapefile.shp polygonShapefile.shp
#
#

import sys
import os
import math
import ogr

#############################################################################
def Usage():
    print 'Usage: poly_at_point.py type size pointShapefile polygonShapefile'
    print "    type = 'c' (circle)     size = radius "
    print "           's' (square)            sideLength "
    print "           'r' (rectangle)         xSideLength ySideLength "
    print
    sys.exit(1)


def Rectangle( center, xSideLength, ySideLength ):
    center_X = center.GetX(0)
    center_Y = center.GetY(0)

    deltaY = ySideLength / 2.0
    bottom = center_Y - deltaY
    top = center_Y + deltaY
    deltaX = xSideLength / 2.0
    left = center_X - deltaX
    right = center_X + deltaX 

    ring = ogr.Geometry( ogr.wkbLinearRing )
    ring.AddPoint_2D( left, bottom )
    ring.AddPoint_2D( right, bottom )
    ring.AddPoint_2D( right, top )
    ring.AddPoint_2D( left, top )
    ring.AddPoint_2D( left, bottom )

    rect_poly = ogr.Geometry( ogr.wkbPolygon )
    rect_poly.AddGeometry( ring )

    return rect_poly


def Circle( center, radius ):    # This could be mad more efficient to take advantage of symmetry
    center_X = center.GetX(0)
    center_Y = center.GetY(0)

    ring = ogr.Geometry( ogr.wkbLinearRing )
    a = 0.0
    while a <= 2*math.pi:
        ca = math.cos(a)
        sa = math.sin(a)
        ring.AddPoint_2D(center_X + (radius * ca), center_Y + (radius * sa))
        a = a + 0.01

    circle_poly = ogr.Geometry( ogr.wkbPolygon )
    circle_poly.AddGeometry( ring )

    return circle_poly

#############################################################################
# Argument processing.

type = None
radius = None
sideLength = None
xSideLength = None
ySideLength = None
pointShapefile = None
polygonShapefile = None

i = 1
while i < len(sys.argv):

    if type is None:
        type = sys.argv[i]
        if type == 'c':
            radius = float(sys.argv[i+1])   # make sure these are numbers
            i = i + 1
        elif type == 's':
            sideLength = float(sys.argv[i+1])
            i = i + 1
        elif type == 'r':
            xSideLength = float(sys.argv[i+1])
            ySideLength = float(sys.argv[i+2])
            i = i + 2
        else:
            Usage()
 
    elif pointShapefile is None:
	    pointShapefile = sys.argv[i]

    elif polygonShapefile is None:
	    polygonShapefile = sys.argv[i]

    else:
	    Usage()

    i = i + 1


if pointShapefile is None:
    Usage()
elif polygonShapefile is None:
    Usage()
elif (type is None) or ( (type <> 'c') and (type <> 's') and (type <> 'r') ):
    Usage()


if type == 'c':
    typeString = 'circle'
    print 'Type:', type, '(', typeString, ') radius:', radius
elif type == 's':
    typeString = 'square'
    print 'Type:', type, '(', typeString, ') side length:', sideLength
elif type == 'r':
    typeString = 'rectangle'
    print 'Type:', type, '(', typeString, ') x side length:', xSideLength, 'y side length:', ySideLength
else:
    Usage()

print 'Point Shapefile:', pointShapefile
print 'Polygon Shapefile:', polygonShapefile
print


#----------------------------------------------------------------------------
# Open the datasource to operate on.

in_ds = ogr.Open( pointShapefile, update = 0 )

# Use only first layer
in_layer = in_ds.GetLayer( 0 )   # ToDo: handle more than one layer?

# check feature type
in_defn = in_layer.GetLayerDefn()
if in_defn.GetGeomType() <> ogr.wkbPoint:
   print 'ERROR: pointShapefile is not POINT geometry'
   print
   Usage()


#----------------------------------------------------------------------------
#	Create output point file with same spatial reference.

shp_driver = ogr.GetDriverByName( 'ESRI Shapefile' )

if os.path.exists(polygonShapefile):
    shp_driver.DeleteDataSource( polygonShapefile )

shp_ds = shp_driver.CreateDataSource( polygonShapefile )

shp_layer = shp_ds.CreateLayer( typeString,
                                geom_type = ogr.wkbPolygon,
                                srs = in_layer.GetSpatialRef() )

#----------------------------------------------------------------------------
#   

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

# add size field(s)

shp_defn  = shp_layer.GetLayerDefn()
field_Id = shp_defn.GetFieldIndex('Id')
field_X = shp_defn.GetFieldIndex('X')
field_Y = shp_defn.GetFieldIndex('Y')



n = 0
in_feat = in_layer.GetNextFeature()
while in_feat is not None:
    n = n + 1

    center = in_feat.GetGeometryRef()

    out_feat = ogr.Feature( feature_def = shp_layer.GetLayerDefn() )

    if type == 'c':
        polygon = Circle( center, radius )
    elif type == 's':
        polygon = Rectangle( center, sideLength, sideLength )
    elif type == 'r':
        polygon = Rectangle( center, xSideLength, ySideLength )

    out_feat.SetField(field_Id, n)  # make Id the same as the point's Id
    out_feat.SetField(field_X, center.GetX(0))
    out_feat.SetField(field_Y, center.GetY(0))
    out_feat.SetGeometry(polygon)

    shp_layer.CreateFeature( out_feat )
    out_feat.Destroy()

    in_feat.Destroy()
    in_feat = in_layer.GetNextFeature()


shp_layer.CommitTransaction()
shp_layer.SyncToDisk()

print n, typeString, 'polygons generated'
print 'Done.'