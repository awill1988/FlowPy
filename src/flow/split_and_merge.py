import logging
from os import PathLike
import pickle
import gc
from typing import Any, Tuple
import numpy as np
import io as io

def dump_extent(src: PathLike, dst: PathLike) -> Tuple[Any, Any]:
    raster, _ = io.read_raster(src)
    nrows, ncols = raster.shape[0], raster.shape[1]

    with open(dst + "extentLarge", "wb") as file:
        pickle.dump((nrows, ncols), file)

        return raster.shape[0], raster.shape[1]

def create_tile(fNameIn: str, fNameOut: str, dirName: str, xDim: np.number, yDim: np.number, U):
    # TODO use multiprocessing on dumps
    nrows, ncols = dump_extent(fNameIn, dirName)

    # todo: document what is happening here...
    I, J, IMAX, JMAX = 0, 0, 0, 0
    while eY < nrows:
        eY = sY + yDim
        while eX < ncols:
            eX = sX+xDim

            sX = eX-2*U
            JMAX = max(J, JMAX)
            J += 1
        sX, J, eX = 0, 0, 0
        sY = eY-2*U
        IMAX = max(I, IMAX)
        I += 1

    # todo: document what is happening here
    sX, sY, eX, eY = 0, 0, 0, 0
    i, j, imax, jmax = 0, 0, 0, 0

    while eY < nrows:
        eY = sY+yDim
        while eX < ncols:
            eX = sX+xDim

            rangeRowsCols = ((sY, eY), (sX, eX))
            pickle.dump(rangeRowsCols,
                        open("{0}ext_{1}_{2}".format(dirName, i, j), "wb"))

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

            sX = eX-2*U
            jmax = max(j, jmax)
            j += 1

        sX, j, eX = 0, 0, 0
        sY = eY-2*U
        imax = max(i, imax)
        i += 1

    pickle.dump((imax, jmax), open("{}nTiles".format(dirName), "wb"))
    logging.info("finished tiling %s: nTiles=%s\n----------------------------",
                 fNameOut, (imax+1)*(jmax+1))

    del raster
    gc.collect()

def update_tile(fNameIn: str, fNameOut: str, dirName: str, xDim: np.number, yDim: np.number, U):
    # TODO use multiprocessing on dumps
    nrows, ncols = dump_extent(fNameIn, dirName)

    i, j, imax, jmax = 0, 0, 0, 0
    sX, sY, eX, eY = 0, 0, 0, 0

    while eY < nrows:
        eY = sY+yDim
        while eX < ncols:
            eX = sX+xDim
            rangeRowsCols = ((sY, eY), (sX, eX))

            with open(dirName + "ext_{}_{}".format(i, j), "wb") as file:
                pickle.dump(rangeRowsCols, file)

            # write the tile
            data = raster[sY:eY, sX:eX]

            np.save(f"{dirName}{fNameOut}_{i}_{j}", data)

            logging.info("saved %s - TileNr.: %i_%i", fNameOut, i, j)

            sX = eX-2*U
            jmax = max(j, jmax)
            j += 1
        sX, j, eX = 0, 0, 0
        sY = eY-2*U
        imax = max(i, imax)
        i += 1

    pickle.dump((imax, jmax), open("{}nTiles".format(dirName), "wb"))
    logging.info("finished tiling %s: nTiles=%s\n----------------------------",
                 fNameOut, (imax+1)*(jmax+1))

    # del largeRaster, largeHeader
    del raster
    gc.collect()
    # return largeRaster

def merge_tiles(inDirPath, fName):
    extL = pickle.load(open(inDirPath + "extentLarge", "rb"))
    nTiles = pickle.load(open(inDirPath + "nTiles", "rb"))
    mergedRas = np.zeros((extL[0], extL[1]))

    # create Raster with original size
    mergedRas[:, :] = np.NaN

    for i in range(nTiles[0]+1):
        for j in range(nTiles[1]+1):
            smallRas = np.load(inDirPath + "%s_%i_%i.npy" % (fName, i, j))
            # print smallRas
            pos = pickle.load(open(inDirPath + "ext_%i_%i" % (i, j), "rb"))
            # print pos

            mergedRas[pos[0][0]:pos[0][1], pos[1][0]:pos[1][1]] =\
                np.fmax(mergedRas[pos[0][0]:pos[0][1],
                                  pos[1][0]:pos[1][1]], smallRas)
            del smallRas
            logging.info("appended result %s_%i_%i", fName, i, j)

    return mergedRas
