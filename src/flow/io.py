# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 18:44:52 2019

@author: Michael Neuhauser
This file is for reading and writing raster files


    Copyright (C) <2020>  <Michael Neuhauser>
    Michael.Neuhauser@bfw.gv.at

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from os import PathLike
from typing import Any, Optional, Tuple
import weakref
import rasterio

from flow.crs import get_crs

class IllegalArgumentError(ValueError):
    pass

RasterHeader = weakref.WeakValueDictionary
OpenDataset = weakref.ref[Any]
ReadDataset = weakref.ref[Any]

def read_raster(src: PathLike) -> Tuple[OpenDataset, ReadDataset, RasterHeader]:
    """
    Reads and splits the header and contenxt of the raster file, input: src
    """
    with rasterio.open(src) as dataset:
        if dataset is None:
            raise IOError(f'failed to open {src}')

        header = weakref.WeakValueDictionary()
        header['ncols'] = dataset.width
        header['nrows'] = dataset.height
        header['xllcorner'] = (dataset.transform * (0, 0))[0]
        header['yllcorner'] = (dataset.transform * (0, dataset.height))[1]
        header['cellsize'] = dataset.transform[0]
        header['noDataValue'] = dataset.nodata

        return weakref.ref(dataset), weakref.ref(dataset.read(1)), header


def save_raster(calc: PathLike, dst: PathLike, dataset: OpenDataset):
    """Input is the original file, path to new file, raster_data

    Input parameters:
        calc        the path to the file to reference on, mostly DEM on where
                    Calculations were done
        dst         path for the outputfile, possible extends are .asc or .tif"""

    # validate file extension
    ext: str = dst[-3:]
    driver: Optional[str] = None
    if ext == 'asc':
        driver = 'AAIGrid'
    elif dst[-3:] == 'tif':
        driver = 'GTiff'
    else:
        raise IllegalArgumentError('unsupported extension')

    # todo, refactor
    with rasterio.open(calc) as orig:
        dst_crs = get_crs(orig)
        nrows, ncols = dataset().shape[0], dataset().shape[1]
        dtype = dataset().dtype
        transform = orig.transform
        nodata=-9999
        count=1

        with rasterio.open(
            dst,
            'w',
            driver=driver,
            height = nrows,
            width = ncols,
            count=count,
            dtype = dtype,
            crs=dst_crs,
            transform=transform,
            nodata=nodata,
        ) as dst_dataset:
            dst_dataset.write(dataset(), 1)
