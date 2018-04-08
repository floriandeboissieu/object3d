#-*-coding: utf8 -*-
'''
@date: 2018-04-03
@author: Florian de Boissieu
@license: GPLv3
@comment: for python 3.5
'''

import argparse
import numpy as np
import gdal
import os

"""
Simple object 3D class based on OBJ format:
    - load from raster
    - write to obj
Main script converts a GDAL raster DEM (Digital Elevation Model) image in 3D object in OBJ format.
In further development it might be wise to use pyOpenGL... 
"""

class Object3D(object):

    def __init__(self):
        self.inputfile = ""
        self.input = None
        self.offset = None
        self.quad = False
        self.vertices = []
        self.faces = []

    def from_raster(filename, offset=None, quad=False, verbose=False):
        """
        Creates an Object3D from a raster of any type supported by GDAL drivers.
        :param offset: 3 element vector [offsetx, offsety, offsetz], removed from x,y,z coordinates.
    If `None`, it is set to [min(x), min(y), 0].
        :param quad: shape of face, triangle if False, quadrilateral if True.
        :param verbose: if True prints details on processing.
        :return: an Object3D.
        """
        new_3d_obj = Object3D()
        new_3d_obj.inputfile = filename
        new_3d_obj.offset = offset
        new_3d_obj.quad = quad
        new_3d_obj.input = read_raster(filename, verbose)
        new_3d_obj.vertices = vertex_array_from_raster(new_3d_obj.input, new_3d_obj.offset, verbose)
        new_3d_obj.faces = face_array_from_raster(new_3d_obj.input, new_3d_obj.quad)
        return new_3d_obj


    def write_obj(self, filename=None, order='xyz', verbose=True):
        """
        Write the 3D object to an OBJ file.
        :param filename: output file path.
        :param order: string of type 'xyz' giving the order in which coordinates should be written.
        :return: void.
        """
        if filename is None:
            filename = os.path.splitext(self.inputfile)[0] + ".obj"


        header = "# Tessellation generated from file: '%s'\n" % self.inputfile
        header += "# vertex coordinates order: %s\n" % order
        header += "# Vertices: {nvertices:n}\n"
        header += "# Faces: {nfaces:n}\n"


        context = {
            "nvertices": len(self.vertices),
            "nfaces": len(self.faces)
        }

        if verbose:
            print("\nWriting tessellation to OBJ file: '%s'\n" % filename)

        colorder = ['xyz'.find(order[0]), 'xyz'.find(order[1]), 'xyz'.find(order[2])]

        with open(filename, 'w') as fstream:
            fstream.write(header.format(**context))

            ## Write all vertices
            fstream.write("\n".join(
                ["v " + " ".join([str(coord) for coord in point])
                 for point in self.vertices[:, colorder]]))

            ## Add empty line between vertices and faces list
            fstream.write("\n")

            ## Write all faces
            fstream.write("\n".join(
                ["f " + " ".join([str(index) for index in face])
                 for face in self.faces]))


        ## Not working with numpy 1.14.0, bug fixed in next versions and may accelerate write
        ## see https://github.com/numpy/numpy/issues/9859
        #     np.savetxt(outfile, vertices, fmt="v %.6f %.6f %.6f")
        #     if faces.shape[1] == 3:
        #         np.savetxt(outfile, faces, fmt="f %i %i %i")
        #     elif faces.shape[1] == 4:
        #         np.savetxt(outfile, faces, fmt="f %i %i %i %i")


def read_raster(filename, verbose=False):
    '''
    Reads a raster of any type supported by GDAL drivers
    :param filename: path the raster file.
    :param verbose: if True prints raster info.
    :return: GDAL raster handle.
    '''
    raster = gdal.Open(filename)
    if verbose:
        print("Reading raster %s" % filename)
        print("Size is {} x {} x {}".format(raster.RasterXSize,
                                            raster.RasterYSize,
                                            raster.RasterCount))
        geotransform = raster.GetGeoTransform()
        if geotransform:
            print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
            print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

    return raster


def vertex_array_from_raster(raster, offset=None, verbose=False):
    '''
    Create the vertex array on the raster.
    :param raster: GDAL raster handle.
    :param offset: 3 element vector [offsetx, offsety, offsetz], removed from x,y,z coordinates.
    If `None`, it is set to [min(x), min(y), 0].
    :param verbose: if True prints details on processing.
    :return: Nx3 numpy array, with N the raster pixel count, and the columns x, y, z coordinates.
    '''
    transform = raster.GetGeoTransform()
    width = raster.RasterXSize
    height = raster.RasterYSize
    x = np.arange(0, width) * transform[1] + transform[0]
    y = np.arange(0, height) * transform[5] + transform[3]

    if offset is None:
        offset=[min(x), min(y), 0]

    if verbose:
        print("\nRemoved offsets: " + str(offset))

    x = x - offset[0]
    y = y - offset[1]

    xx, yy = np.meshgrid(x, y)

    if verbose:
        print("\nReading raster data...")
    zz = raster.ReadAsArray()
    if verbose:
        print("Done")
    zz = zz - offset[2]
    vertices = np.vstack((xx, yy, zz)).reshape([3, -1]).transpose()
    return vertices


def face_array_from_raster(raster, quad=False):
    """
    Create face array
    :param raster: GDAL raster handle.
    :param quad: shape of face, triangle if False, quadrilateral if True.
    :return: NxM numpy array, with N the number of faces, M either 3 or 4 depending on quad argument.
    """
    width = raster.RasterXSize
    height = raster.RasterYSize

    ai = np.arange(0, width - 1)
    aj = np.arange(0, height - 1)
    aii, ajj = np.meshgrid(ai, aj)
    a = aii + ajj * width
    a = a.flatten()

    if quad:  # rectangular mesh
        faces = np.vstack((a, a + width, a + width + 1, a + 1))
        faces = np.transpose(faces)
    else:  # triangular mesh
        faces = np.vstack((a, a + width, a + width + 1, a, a + width + 1, a + 1))
        faces = np.transpose(faces).reshape([-1, 3])

    return faces






def main(args):

    new_3d_obj = Object3D.from_raster(args.inputfile, args.offset, args.quad, args.verbose)
    new_3d_obj.write_obj(args.output, args.order)


if __name__ == "__main__":
    # Get argument parser
    parser = argparse.ArgumentParser(description="Convert raster DEM to 3D OBJ")

    # Add argument
    parser.add_argument("input", action="store", type=str,
                        help="Raster DEM image"
                        )

    parser.add_argument("-o", "--output", action="store", type=str,
                        default=None,
                        help="OBJ output file (default: <raster file name>.obj)"
                        )

    parser.add_argument("--offset", action="store", type=float, nargs=3,
                        metavar=('OffsetX', 'OffsetY', 'OffsetZ'),
                        default=None,
                        help="OffsetX OffsetY OffsetZ: makes X-OffsetX, Y-OffsetY, Z-OffsetZ before writing to OBJ."
                             "Default is min(X) min(Y) 0."
                        )

    parser.add_argument("-p", "--parse", action="store", type=str, nargs=1,
                        default='yzx',
                        help="Coordinates order of vertex: default is yzx as is in blender."
                        )

    parser.add_argument("-q", "--quad", action="store_true",
                        help="Make quadratic tessellation instead of triangular."
                        )

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Makes scene repetitive.')
    # Parse argument
    args = parser.parse_args()

    # Launch
    main(args)
