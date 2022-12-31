from os import PathLike
import pickle
from typing import Any, Tuple
from flow.util import open_raster


def dump_extent(src: PathLike, dst: PathLike) -> Tuple[Any, Any]:
    """determines the extent from a file"""
    raster, _ = open_raster(src)
    nrows, ncols = raster.shape[0], raster.shape[1]

    with open(str(dst) + "extentLarge", "wb") as file:
        pickle.dump((nrows, ncols), file)

        return raster.shape[0], raster.shape[1]
