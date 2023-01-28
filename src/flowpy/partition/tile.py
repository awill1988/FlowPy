import logging
from os import PathLike
import pickle
import gc
from typing import Any, Tuple
import numpy as np


def create(
    fNameIn: str, fNameOut: str, dirName: str, xDim: np.number, yDim: np.number, U
):
    # TODO use multiprocessing on dumps
    nrows, ncols = dump_extent(fNameIn, dirName)

    # todo: document what is happening here...
    I, J, IMAX, JMAX = 0, 0, 0, 0
    while eY < nrows:
        eY = sY + yDim
        while eX < ncols:
            eX = sX + xDim

            sX = eX - 2 * U
            JMAX = max(J, JMAX)
            J += 1
        sX, J, eX = 0, 0, 0
        sY = eY - 2 * U
        IMAX = max(I, IMAX)
        I += 1

    # todo: document what is happening here
    sX, sY, eX, eY = 0, 0, 0, 0
    i, j, imax, jmax = 0, 0, 0, 0

    while eY < nrows:
        eY = sY + yDim
        while eX < ncols:
            eX = sX + xDim

            rangeRowsCols = ((sY, eY), (sX, eX))
            pickle.dump(
                rangeRowsCols, open("{0}ext_{1}_{2}".format(dirName, i, j), "wb")
            )

            initRas = raster[sY:eY, sX:eX].copy()

            if j != JMAX:
                initRas[:, -U:] = -9999  # Rand im Osten
            if i != 0:
                initRas[0:U, :] = -9999  # Rand im Norden
            if j != 0:
                initRas[:, 0:U] = -9999  # Rand im Westen
            if i != IMAX:
                initRas[-U:, :] = -9999  # Rand im Sueden

            np.save("{0}{1}_{2}_{3}".format(dirName, fNameOut, i, j), initRas)

            del initRas

            logging.info("saved %s - TileNr.: %i_%i", fNameOut, i, j)

            sX = eX - 2 * U
            jmax = max(j, jmax)
            j += 1

        sX, j, eX = 0, 0, 0
        sY = eY - 2 * U
        imax = max(i, imax)
        i += 1

    pickle.dump((imax, jmax), open("{}nTiles".format(dirName), "wb"))
    logging.info(
        "finished tiling %s: nTiles=%s\n----------------------------",
        fNameOut,
        (imax + 1) * (jmax + 1),
    )

    del raster
    gc.collect()


def update(
    fNameIn: str, fNameOut: str, dirName: str, xDim: np.number, yDim: np.number, U
):
    # TODO use multiprocessing on dumps
    nrows, ncols = dump_extent(fNameIn, dirName)

    i, j, imax, jmax = 0, 0, 0, 0
    sX, sY, eX, eY = 0, 0, 0, 0

    while eY < nrows:
        eY = sY + yDim
        while eX < ncols:
            eX = sX + xDim
            rangeRowsCols = ((sY, eY), (sX, eX))

            with open(dirName + "ext_{}_{}".format(i, j), "wb") as file:
                pickle.dump(rangeRowsCols, file)

            # write the tile
            data = raster[sY:eY, sX:eX]

            np.save(f"{dirName}{fNameOut}_{i}_{j}", data)

            logging.info("saved %s - TileNr.: %i_%i", fNameOut, i, j)

            sX = eX - 2 * U
            jmax = max(j, jmax)
            j += 1
        sX, j, eX = 0, 0, 0
        sY = eY - 2 * U
        imax = max(i, imax)
        i += 1

    pickle.dump((imax, jmax), open("{}nTiles".format(dirName), "wb"))
    logging.info(
        "finished tiling %s: nTiles=%s\n----------------------------",
        fNameOut,
        (imax + 1) * (jmax + 1),
    )

    # del largeRaster, largeHeader
    del raster
    gc.collect()
    # return largeRaster


def merge_tiles(path: PathLike, filename: str):
    with open(path / "/extentLarge", "rb") as extent, open(
        path / "nTiles", "rb"
    ) as tiles:
        extL = pickle.load(extent)
        tile_metadata = pickle.load(tiles)
        mergedRas = np.zeros((extL[0], extL[1]))

        # create Raster with original size
        mergedRas[:, :] = np.NaN

        for i in range(tile_metadata[0] + 1):
            for j in range(tile_metadata[1] + 1):
                smallRas = np.load(f"{path}{filename}_{i}_{j}.npy")
                with open(f"{path}/ext_{i}_{j}", "rb") as p:
                    # print smallRas
                    pos = pickle.load(p)
                    # print pos
                    mergedRas[pos[0][0] : pos[0][1], pos[1][0] : pos[1][1]] = np.fmax(
                        mergedRas[pos[0][0] : pos[0][1], pos[1][0] : pos[1][1]],
                        smallRas,
                    )
                    logging.info("appended result %s_%i_%i", filename, i, j)
                del smallRas

        return mergedRas
