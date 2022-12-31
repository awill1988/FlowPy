"""
Utility Tests.
"""


from os import PathLike
from typing import Optional
from weakref import ReferenceType
from rasterio.io import DatasetReader, MemoryFile
import rasterio
from flow.memory import make_ref


def _test_raster(dim: int) -> MemoryFile:
    pass


def open_raster(src: PathLike) -> ReferenceType[DatasetReader]:
    """
    Reads a raster into a dataset as a reference so ideally it will be
    re-used but efficiently garbage collected if no smells are present.
    """
    with rasterio.open(src, "r") as dataset:
        if dataset is None:
            raise IOError(f"failed to open {src}")
        return make_ref(dataset)


def save_raster(src: PathLike, dst: PathLike, ref: ReferenceType[DatasetReader]):
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
        raise ValueError("unsupported dst file type value")

    # dereference the dataset
    dataset = ref()
    assert dataset is not None
    nrows, ncols = dataset().shape[0], dataset().shape[1]
    dtype = dataset().dtype

    with rasterio.open(src) as raster:
        transform = raster.transform

    nodata = -9999
    count = 1
    # crs = read_crs(raster)

    with rasterio.open(
        dst,
        "w",
        driver=driver,
        height=nrows,
        width=ncols,
        count=count,
        dtype=dtype,
        # crs=crs,
        transform=transform,
        nodata=nodata,
    ) as dst_dataset:
        dst_dataset.write(dataset(), 1)


def test_open_raster():
    assert open_raster is not None


def test_save_raster():
    assert save_raster is not None
