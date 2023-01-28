import logging
import rasterio

from os import PathLike
from typing import Optional
from weakref import ProxyType
from rasterio import CRS
from rasterio.io import DatasetReader
from flowpy.memory import make_proxy

ReadDataset = ProxyType[DatasetReader]

logger = logging.getLogger("flow.util")


class IllegalArgumentError(ValueError):
    pass


class RasterHeaderInfo:
    """caches file information from a raster file for organizing for multiprocessing later.

    Args:
        dataset (ReadDataset): must be a proxy object to the underlying DatasetReader.
    """

    def __init__(self, dataset: ReadDataset):
        self._ncols = dataset.width
        self._nrows = dataset.height
        self._xllcorner = (dataset.transform * (0, 0))[0]
        self._yllcorner = (dataset.transform * (0, dataset.height))[1]
        self._cellsize = dataset.transform[0]
        self._no_data_value = dataset.nodata

    @property
    def ncols(self):
        return self._ncols

    @property
    def nrows(self):
        return self._nrows

    @property
    def xllcorner(self):
        return self._xllcorner

    @property
    def yllcorner(self):
        return self._yllcorner

    @property
    def cellsize(self):
        return self._cellsize

    @property
    def no_data_value(self):
        return self._cellsize


def read_crs(dataset: ReadDataset, epsg_fallback: int = 4326) -> CRS:
    """reads CRS data from open rasterio file.

    Args:
        dataset (ReadDataset): must be a proxy object to the underlying DatasetReader.

    Returns:
        crs.CRS: coordinate reference system information
    """
    try:
        _crs = CRS.from_dict(dataset.crs.data)
    except Exception as err:  # pylint: disable=broad-except
        logger.error(err)
        _crs = _crs.CRS.from_epsg(epsg_fallback)
        logger.warning(
            "could not determine coordinate reference system, will fallback to %d",
            epsg_fallback,
        )
    return _crs


def open_raster(src: PathLike) -> ProxyType[DatasetReader]:
    """
    Reads a raster into a dataset as a reference so ideally it will be
    re-used but efficiently garbage collected if no smells are present.
    """
    with rasterio.open(src, "r") as dataset:
        if dataset is None:
            raise IOError(f"failed to open {src}")
        return make_proxy(dataset)


def save_raster(src: PathLike, dst: PathLike, dataset: DatasetReader):
    """Input is the original file, path to new file, raster_data

    Input parameters:
        src         the path to the file to reference on, mostly DEM on where
                    Calculations were done
        dst         path for the output raster file in either GeoTiff or WebP format
    """

    # validate file extension
    ext: str = str(dst)[-3:]
    driver: Optional[str] = None
    if ext == "webp":
        driver = "WEBP"
    elif ext == "tif":
        driver = "GTiff"
    else:
        raise IllegalArgumentError("unsupported dst file type")

    with rasterio.open(src) as raster:
        nrows, ncols = dataset().shape[0], dataset().shape[1]
        dtype = dataset().dtype
        transform = raster.transform
        nodata = -9999
        count = 1

        with rasterio.open(
            dst,
            "w",
            driver=driver,
            height=nrows,
            width=ncols,
            count=count,
            dtype=dtype,
            crs=read_crs(raster),
            transform=transform,
            nodata=nodata,
        ) as dst_dataset:
            dst_dataset.write(dataset(), 1)
