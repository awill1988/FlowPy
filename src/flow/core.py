"""
This is the core function for Flow-Py, it handles:
- Sorting release pixels by altitude(get_start_idx)
- Splitting function of the release layer for multiprocessing(split_release)
- Back calculation if infrastructure is hit
- Calculation of runout, etc. (Creating the CellList and iterating through
the release pixels, erasing release pixels that were hit, stop at the border
of DEM, return arrays)
"""
from pathlib import Path
import sys
from typing import Any, Tuple, List
import numpy as np
from datetime import datetime
import logging
from flow.cell import Cell

logger = logging.getLogger("flow.core")

CoreArguments = Tuple[int, int, str, str]
CellList = List[Cell]


def by_z_desc(dem: Any, release: np.ndarray):
    """Sort Release Pixels by altitude and return the result as lists for the
    Rows and Columns, starting with the highest altitude

    Input parameters:
        dem         Digital Elevation Model to gain information about altitude
        release     The release layer, release pixels need int value > 0

    Output parameters:
        row_list    Row index of release pixels sorted by altitude
        col_list    Column index of release pixels sorted by altitude
    """
    row_list, col_list = np.where(
        release > 0
    )  # Gives back the indices of the release areas
    if len(row_list) > 0:
        altitude_list = []
        for (index, item) in enumerate(row_list):
            altitude_list.append(dem[item, col_list[index]])
        altitude_list, row_list, col_list = list(
            zip(*sorted(zip(altitude_list, row_list, col_list), reverse=True))
        )
        # Sort this lists by altitude
    return row_list, col_list


def back_calculation(back_cell: Cell) -> List[Cell]:
    """Here the back calculation from a "runout pixel" that hits a infrastructure
    to the release pixel is performed.

    Input parameters:
        hit_cell_list        All cells that hit a Infrastructure

    Output parameters:
        Back_list   List of descendent Cells (i.e. pixels from raster) which lead back
                    deterministically to the start cell.
    """
    back_list: List[Cell] = []
    for parent in back_cell.parent:
        if parent not in back_list:
            back_list.append(parent)
    for cell in back_list:
        for parent in cell.parent:
            if parent not in back_list:
                back_list.append(parent)
    return back_list


def calculation(args: CoreArguments):
    """This is the core function where all the data handling and calculation is
    done.

    Input parameters:
        dem             The digital elevation model
        header          The header of the elevation model
        forest          The forest layer
        process         Which process to calculate (Avalanche, Rockfall, SoilSlides)
        release         The list of release arrays
        -----------------------------------------------------------------------------
        alpha           alpha angle
        exp             exponent
        flux_threshold  TODO: what is this?
        max_z_delta     TODO: what is this?

    Output parameters:
        z_delta     Array like DEM with the max. kinetic Energy Height for every
                    pixel
        flux_array  Array with max. concentration factor saved
        count_array Array with the number of hits for every pixel
        elh_sum     Array with the sum of Energy Line Height
        back_calc   Array with back calculation, still to do!!!
    """
    # parse the arguments
    # TODO, move this out of this function!
    alpha = float(args[2])
    exp = float(args[3])
    cellsize = float(args[4])
    nodata = float(args[5])
    flux_threshold = float(args[6])
    max_z_delta = float(args[7])

    temp_dir = Path(args[8])

    # load the raster data from numpy
    pickled_dem = np.load(temp_dir + "dem_{}_{}.npy".format(args[0], args[1]))
    pickled_release = np.load(temp_dir + "init_{}_{}.npy".format(args[0], args[1]))
    pickled_infra = np.load(temp_dir + "infra_{}_{}.npy".format(args[0], args[1]))

    z_delta_array = np.zeros_like(pickled_dem, dtype=np.float32)
    z_delta_sum = np.zeros_like(pickled_dem, dtype=np.float32)
    flux_array = np.zeros_like(pickled_dem, dtype=np.float32)
    count_array = np.zeros_like(pickled_dem, dtype=np.int32)
    backcalc = np.zeros_like(pickled_dem, dtype=np.int32)
    fp_travelangle_array = np.zeros_like(
        pickled_dem, dtype=np.float32
    )  # fp = Flow Path
    sl_travelangle_array = (
        np.zeros_like(pickled_dem, dtype=np.float32) * 90
    )  # sl = Straight Line

    back_list = []

    # Core
    start = datetime.now().replace(microsecond=0)
    rows, cols = by_z_desc(pickled_dem, pickled_release)

    idx = 0
    while idx < len(rows):
        fmt = " ".join(
            [
                f"\rcalculating start cell: {len(rows) - (idx + 1)}",
                "of",
                f"{len(rows)}",
                "=" f"{round((idx + 1) / len(rows) * 100, 2)}%",
            ]
        )
        logger.info(fmt)
        cells = []
        row = rows[idx]
        col = cols[idx]
        # neighbourhood DEM
        dem_ng = pickled_dem[(row - 1) : (row + 2), (col - 1) : (col + 2)]
        if (nodata in dem_ng) or np.size(dem_ng) < 9:
            idx += 1
            continue

        startcell = Cell(
            row,
            col,
            dem_ng,
            cellsize,
            1,
            0,
            None,
            alpha,
            exp,
            flux_threshold,
            max_z_delta,
            startcell=True,
        )
        # If this is a startcell just give a Bool to startcell otherwise the object startcell

        cells.append(startcell)

        for idx, cell in enumerate(cells):
            row, col, flux, z_delta = cell.calc_distribution()

            if len(flux) > 0:
                # mass, row, col  = list(zip(*sorted(zip( mass, row, col), reverse=False)))

                z_delta, flux, row, col = list(
                    zip(*sorted(zip(z_delta, flux, row, col), reverse=False))
                )
                # Sort this lists by elh, to start with the highest cell

            for i in range(idx, len(cells)):  # Check if Cell already exists
                k = 0
                while k < len(row):
                    if row[k] == cells[i].rowindex and col[k] == cells[i].colindex:
                        cells[i].add_os(flux[k])
                        cells[i].add_parent(cell)
                        if z_delta[k] > cells[i].z_delta:
                            cells[i].z_delta = z_delta[k]
                        row = np.delete(row, k)
                        col = np.delete(col, k)
                        flux = np.delete(flux, k)
                        z_delta = np.delete(z_delta, k)
                    else:
                        k += 1

            for k in range(len(row)):
                dem_ng = pickled_dem[
                    row[k] - 1 : row[k] + 2, col[k] - 1 : col[k] + 2
                ]  # neighbourhood DEM
                if (nodata in dem_ng) or np.size(dem_ng) < 9:
                    continue
                cells.append(
                    Cell(
                        row[k],
                        col[k],
                        dem_ng,
                        cellsize,
                        flux[k],
                        z_delta[k],
                        cell,
                        alpha,
                        exp,
                        flux_threshold,
                        max_z_delta,
                        startcell,
                    )
                )

            z_delta_array[cell.rowindex, cell.colindex] = max(
                z_delta_array[cell.rowindex, cell.colindex], cell.z_delta
            )
            flux_array[cell.rowindex, cell.colindex] = max(
                flux_array[cell.rowindex, cell.colindex], cell.flux
            )
            count_array[cell.rowindex, cell.colindex] += int(1)
            z_delta_sum[cell.rowindex, cell.colindex] += cell.z_delta
            fp_travelangle_array[cell.rowindex, cell.colindex] = max(
                fp_travelangle_array[cell.rowindex, cell.colindex], cell.max_gamma
            )
            sl_travelangle_array[cell.rowindex, cell.colindex] = max(
                sl_travelangle_array[cell.rowindex, cell.colindex], cell.sl_gamma
            )

            # Backcalculation
            if pickled_infra[cell.rowindex, cell.colindex] > 0:
                # backlist = []
                back_list = back_calculation(cell)

                for back_cell in back_list:
                    backcalc[back_cell.rowindex, back_cell.colindex] = max(
                        backcalc[back_cell.rowindex, back_cell.colindex],
                        pickled_infra[cell.rowindex, cell.colindex],
                    )
        pickled_release[z_delta_array > 0] = 0
        # Check if i hit a release Cell, if so set it to zero and get again
        # the indexes of release cells
        rows, cols = by_z_desc(pickled_dem, pickled_release)
        idx += 1
    end = datetime.now().replace(microsecond=0)

    # Save Calculated tiles
    np.save(temp_dir + "./res_z_delta_{}_{}".format(args[0], args[1]), z_delta_array)
    np.save(temp_dir + "./res_z_delta_sum_{}_{}".format(args[0], args[1]), z_delta_sum)
    np.save(temp_dir + "./res_flux_{}_{}".format(args[0], args[1]), flux_array)
    np.save(temp_dir + "./res_count_{}_{}".format(args[0], args[1]), count_array)
    np.save(temp_dir + "./res_fp_{}_{}".format(args[0], args[1]), fp_travelangle_array)
    np.save(temp_dir + "./res_sl_{}_{}".format(args[0], args[1]), sl_travelangle_array)
    np.save(temp_dir + "./res_backcalc_{}_{}".format(args[0], args[1]), backcalc)

    print("\n Time needed: " + str(end - start))
    print("Finished calculation {}_{}".format(args[0], args[1]))


def calculation_effect(args: CoreArguments):
    """This is the core function where all the data handling and calculation is
    done.

    Input parameters:
        dem         The digital elevation model
        release     The list of release arrays

    Output parameters:
        z_delta        Array like DEM with the max. Energy Line Height for every
                    pixel
        flux_array  Array with max. concentration factor saved
        count_array Array with the number of hits for every pixel
        z_delta_sum     Array with the sum of Energy Line Height
        back_calc   Array with back calculation, still to do!!!
    """

    temp_dir = args[8]

    dem = np.load(temp_dir + "dem_{}_{}.npy".format(args[0], args[1]))
    release = np.load(temp_dir + "init_{}_{}.npy".format(args[0], args[1]))

    alpha = float(args[2])
    exp = float(args[3])
    cellsize = float(args[4])
    nodata = float(args[5])
    flux_threshold = float(args[6])
    max_z_delta = float(args[7])

    z_delta_array = np.zeros_like(dem, dtype=np.float32)
    z_delta_sum = np.zeros_like(dem, dtype=np.float32)
    flux_array = np.zeros_like(dem, dtype=np.float32)
    count_array = np.zeros_like(dem, dtype=np.int32)
    # backcalc = np.zeros_like(dem, dtype=np.int32)
    fp_travelangle_array = np.zeros_like(dem, dtype=np.float32)  # fp = Flow Path
    sl_travelangle_array = (
        np.ones_like(dem, dtype=np.float32) * 90
    )  # sl = Straight Line

    # Core
    start = datetime.now().replace(microsecond=0)
    row_list, col_list = by_z_desc(dem, release)

    startcell_idx = 0
    while startcell_idx < len(row_list):

        sys.stdout.write(
            "\r"
            "Calculating Startcell: "
            + str(startcell_idx + 1)
            + " of "
            + str(len(row_list))
            + " = "
            + str(round((startcell_idx + 1) / len(row_list) * 100, 2))
            + "%"
            "\r"
        )
        sys.stdout.flush()

        cell_list = []
        row_idx = row_list[startcell_idx]
        col_idx = col_list[startcell_idx]
        dem_ng = dem[
            row_idx - 1 : row_idx + 2, col_idx - 1 : col_idx + 2
        ]  # neighbourhood DEM
        if (nodata in dem_ng) or np.size(dem_ng) < 9:
            startcell_idx += 1
            continue

        startcell = Cell(
            row_idx,
            col_idx,
            dem_ng,
            cellsize,
            1,
            0,
            None,
            alpha,
            exp,
            flux_threshold,
            max_z_delta,
            True,
        )
        # If this is a startcell just give a Bool to startcell otherwise the object startcell

        cell_list.append(startcell)

        for idx, cell in enumerate(cell_list):
            row, col, flux, z_delta = cell.calc_distribution()

            if len(flux) > 0:
                z_delta, flux, row, col = list(
                    zip(*sorted(zip(z_delta, flux, row, col), reverse=False))
                )  # reverse = True == descending

            for i in range(idx, len(cell_list)):  # Check if Cell already exists
                k = 0
                while k < len(row):
                    if (
                        row[k] == cell_list[i].rowindex
                        and col[k] == cell_list[i].colindex
                    ):
                        cell_list[i].add_os(flux[k])
                        cell_list[i].add_parent(cell)
                        if z_delta[k] > cell_list[i].z_delta:
                            cell_list[i].z_delta = z_delta[k]

                        row = np.delete(row, k)
                        col = np.delete(col, k)
                        flux = np.delete(flux, k)
                        z_delta = np.delete(z_delta, k)
                    else:
                        k += 1

            for k in range(len(row)):
                dem_ng = dem[
                    row[k] - 1 : row[k] + 2, col[k] - 1 : col[k] + 2
                ]  # neighbourhood DEM
                if (nodata in dem_ng) or np.size(dem_ng) < 9:
                    continue
                cell_list.append(
                    Cell(
                        row[k],
                        col[k],
                        dem_ng,
                        cellsize,
                        flux[k],
                        z_delta[k],
                        cell,
                        alpha,
                        exp,
                        flux_threshold,
                        max_z_delta,
                        startcell,
                    )
                )

        for cell in cell_list:
            z_delta_array[cell.rowindex, cell.colindex] = max(
                z_delta_array[cell.rowindex, cell.colindex], cell.z_delta
            )
            flux_array[cell.rowindex, cell.colindex] = max(
                flux_array[cell.rowindex, cell.colindex], cell.flux
            )
            count_array[cell.rowindex, cell.colindex] += 1
            z_delta_sum[cell.rowindex, cell.colindex] += cell.z_delta
            fp_travelangle_array[cell.rowindex, cell.colindex] = max(
                fp_travelangle_array[cell.rowindex, cell.colindex], cell.max_gamma
            )
            sl_travelangle_array[cell.rowindex, cell.colindex] = max(
                sl_travelangle_array[cell.rowindex, cell.colindex], cell.sl_gamma
            )

        startcell_idx += 1

    # Save Calculated tiles
    np.save(temp_dir + "./res_z_delta_{}_{}".format(args[0], args[1]), z_delta_array)
    np.save(temp_dir + "./res_z_delta_sum_{}_{}".format(args[0], args[1]), z_delta_sum)
    np.save(temp_dir + "./res_flux_{}_{}".format(args[0], args[1]), flux_array)
    np.save(temp_dir + "./res_count_{}_{}".format(args[0], args[1]), count_array)
    np.save(temp_dir + "./res_fp_{}_{}".format(args[0], args[1]), fp_travelangle_array)
    np.save(temp_dir + "./res_sl_{}_{}".format(args[0], args[1]), sl_travelangle_array)

    logging.info("finished calculation {}_{}".format(args[0], args[1]))
    print("Finished calculation {}_{}".format(args[0], args[1]))

    end = datetime.now().replace(microsecond=0)
    print("\n Time needed: " + str(end - start))
