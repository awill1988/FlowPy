#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 14:23:00 2018

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
# import standard libraries
import os
import sys
from typing import Any, List, Tuple
import numpy as np
from datetime import datetime
from multiprocessing import cpu_count
import multiprocessing as mp
import logging
import pickle

# Flow-Py Libraries
import io as io
import core as fc
import split_and_merge as SPAM

def main(args, kwargs):
    # todo what are these??
    alpha = args[0]
    exp = args[1]
    directory = args[2]
    dem_path = args[3]
    release_path = args[4]

    if 'infra' in kwargs:
        infra_path = kwargs.get('infra')
    else:
        infra_path = None

    if 'flux' in kwargs:
        flux_threshold = float(kwargs.get('flux'))
    else:
        flux_threshold = 3 * 10 ** -4

    if 'max_z' in kwargs:
        max_z = kwargs.get('max_z')
    else:
        max_z = 8848
        # Recomendet values:
                # Avalanche = 270
                # Rockfall = 50
                # Soil Slide = 12

    print("Starting...")
    print("...")

    start = datetime.now().replace(microsecond=0)
    infra_bool = False
    # Create result directory
    time_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        os.makedirs(directory + 'res_{}/'.format(time_string))
        res_dir = ('res_{}/'.format(time_string))
    except FileExistsError:
        res_dir = ('res_{}/'.format(time_string))

    try:
        os.makedirs(directory + res_dir + 'temp/')
        temp_dir = (directory + res_dir + 'temp/')
    except FileExistsError:
        temp_dir = (directory + res_dir + 'temp/')

    # Setup logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=(directory + res_dir + 'log_{}.txt').format(time_string),
                        filemode='w')

    # Start of Calculation
    logging.info('Start Calculation')
    logging.info('Alpha Angle: {}'.format(alpha))
    logging.info('Exponent: {}'.format(exp))
    logging.info('Flux Threshold: {}'.format(flux_threshold))
    logging.info('Max Z_delta: {}'.format(max_z))
    logging.info
    # Read in raster files
    try:
        dem, header = io.read_raster(dem_path)
        logging.info('DEM File: {}'.format(dem_path))
    except FileNotFoundError:
        print("DEM: Wrong filepath or filename")
        return

    try:
        release, release_header = io.read_raster(release_path)
        logging.info('Release File: {}'.format(release_path))
    except FileNotFoundError:
        print("Wrong filepath or filename")
        return

    # Check if Layers have same size!!!
    if header['ncols'] == release_header['ncols'] and header['nrows'] == release_header['nrows']:
        print("DEM and Release Layer ok!")
    else:
        print("Error: Release Layer doesn't match DEM!")
        return

    try:
        infra, infra_header = io.read_raster(infra_path)
        if header['ncols'] == infra_header['ncols'] and header['nrows'] == infra_header['nrows']:
            print("Infra Layer ok!")
            infra_bool = True
            logging.info('Infrastructure File: {}'.format(infra_path))
        else:
            print("Error: Infra Layer doesn't match DEM!")
            return
    except:
        infra = np.zeros_like(dem)

    del dem, release, infra
    logging.info('Files read in')

    cellsize = header["cellsize"]
    nodata = header["noDataValue"]

    tileCOLS = int(15000 / cellsize)
    tileROWS = int(15000 / cellsize)
    U = int(5000 / cellsize) # 5km overlap

    logging.info("Start Tiling.")
    print("Start Tiling...")

    SPAM.tileRaster(dem_path, "dem", temp_dir, tileCOLS, tileROWS, U)
    SPAM.tileRaster(release_path, "init", temp_dir, tileCOLS, tileROWS, U, isInit=True)
    if infra_bool:
        SPAM.tileRaster(infra_path, "infra", temp_dir, tileCOLS, tileROWS, U)

    print("Finished Tiling...")
    nTiles = pickle.load(open(temp_dir + "nTiles", "rb"))

    optList: List[Tuple[int, int, str, str]] = []
    # das hier ist die batch-liste, die von mulitprocessing
    # abgearbeitet werden muss - sieht so aus:
    # [(0,0,alpha,exp,cellsize,-9999.),
    # (0,1,alpha,exp,cellsize,-9999.),
    # etc.]

    for i in range(nTiles[0]+1):
        for j in range(nTiles[1]+1):
            optList.append((i, j, alpha, exp, cellsize, nodata, flux_threshold, max_z, temp_dir))

    # Calculation
    logging.info('Multiprocessing starts, used cores: {}'.format(cpu_count() - 1))
    print("{} Processes started and {} calculations to perform.".format(mp.cpu_count() - 1, len(optList)))
    pool = mp.Pool(mp.cpu_count() - 1)

    if infra_bool:
        pool.map(fc.calculation, optList)
    else:
        pool.map(fc.calculation_effect, optList)

    pool.close()
    pool.join()

    logging.info('Calculation finished, merging results.')

    # Merge calculated tiles
    z_delta = SPAM.merge_tiles(temp_dir, "res_z_delta")
    flux = SPAM.merge_tiles(temp_dir, "res_flux")
    cell_counts = SPAM.merge_tiles(temp_dir, "res_count")
    z_delta_sum = SPAM.merge_tiles(temp_dir, "res_z_delta_sum")
    fp_ta = SPAM.merge_tiles(temp_dir, "res_fp")
    sl_ta = SPAM.merge_tiles(temp_dir, "res_sl")
    if infra_bool:
        backcalc = SPAM.merge_tiles(temp_dir, "res_backcalc")

    # time_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.info('Writing Output Files')
    output_format = '.tif'
    io.save_raster(dem_path,
                     directory + res_dir + "flux{}".format(output_format),
                     flux)
    io.save_raster(dem_path,
                     directory + res_dir + "z_delta{}".format(output_format),
                     z_delta)
    io.save_raster(dem_path,
                     directory + res_dir + "FP_travel_angle{}".format(output_format),
                     fp_ta)
    io.save_raster(dem_path,
                     directory + res_dir + "SL_travel_angle{}".format(output_format),
                     sl_ta)
    if not infra_bool:  # if no infra
        io.save_raster(dem_path,
                         directory + res_dir + "cell_counts{}".format(output_format),
                         cell_counts)
        io.save_raster(dem_path,
                         directory + res_dir + "z_delta_sum{}".format( output_format),
                         z_delta_sum)
    if infra_bool:  # if infra
        io.save_raster(dem_path,
                         directory + res_dir + "backcalculation{}".format(output_format),
                         backcalc)

    print("Calculation finished")
    print("...")
    end = datetime.now().replace(microsecond=0)
    logging.info('Calculation needed: ' + str(end - start) + ' seconds')


if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) < 1:
        print("Too few input arguments!!!")
        sys.exit(1)

    args=[arg for arg in argv if arg.find('=')<0]
    kwargs={kw[0]:kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=')>0]}

    main(args, kwargs)
