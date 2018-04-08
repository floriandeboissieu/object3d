# object3d

Simple 3D object class based on OBJ format.

Features:
- load from raster
- write to obj
- main script to convert a GDAL raster DEM (Digital Elevation Model) image in 3D object in OBJ format with command line.

# Command line usage
```
usage: object3d.py [-h] [-o OUTPUT] [--offset OffsetX OffsetY OffsetZ]
                   [-p PARSE] [-q] [-v]
                   input

Convert raster DEM to 3D OBJ

positional arguments:
  input                 DEM raster (1 layer) of any type supported by GDAL
                        drivers.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        OBJ output file (default: <raster file name>.obj)
  --offset OffsetX OffsetY OffsetZ
                        Computes X-OffsetX, Y-OffsetY, Z-OffsetZ before
                        writing to OBJ(default: min(X) min(Y) 0)
  -p PARSE, --parse PARSE
                        Coordinates order of vertex: default is yzx as is in
                        blender.
  -q, --quad            Make quadratic tessellation instead of triangular.
  -v, --verbose         Print processing details.
```


In further development it might be wise to use pyOpenGL... 
