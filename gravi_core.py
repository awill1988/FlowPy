#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 15:15:37 2019

@author: neuhauser
This is core function
"""

import numpy as np
import sys
import time
#from multiprocessing import Pool
#import os

sys.path.append('/home/W/Neuhauser/Frei/python_libs/')
import raster_io as io
from gravi_class import Cell


## Programm:        
def get_start_idx(release):
    row_list, col_list = np.where(release > 0)  # Gives back the indices of the release areas
    if len(row_list) > 0:
        altitude_list = []
        for i in range(len(row_list)):
            altitude_list.append(dem[row_list[i], col_list[i]])    
        altitude_list, row_list, col_list = list(zip(*sorted(zip(altitude_list, row_list, col_list), reverse=False)))  #Sort this lists by altitude
    return row_list, col_list   

def back_calculation(cell):
    back_list = []
    for parent in cell.parent:
        back_list.append(parent)
    for cell in back_list:
        for parent in cell.parent:
            back_list.append(parent)
    return back_list

def calculation(row_list, col_list):

    startcell_idx = 0
    while startcell_idx < len(row_list):
        sys.stdout.write('\r' "Calculating Startcell: " + str(startcell_idx+1) + " of " + str(len(row_list)) + " = " + str(round((startcell_idx + 1)/len(row_list)*100,2)) + "%" '\r')
        sys.stdout.flush()
        cell_list = []
        row_idx = row_list[startcell_idx]
        col_idx = col_list[startcell_idx]    
        dem_ng = dem[row_idx - 1:row_idx + 2, col_idx - 1:col_idx + 2] # neighbourhood DEM
        if nodata in dem_ng:
            startcell_idx += 1
            continue
        
        startcell = Cell(row_idx, col_idx, dem_ng, cellsize, 1, 0, None, startcell=True)
        # If this is a startcell just give a Bool to startcell otherwise the object startcell
        
        cell_list.append(startcell)
        checked = 0
        #index = 0
        for cells in cell_list:
            row, col, mass, kin_e = cells.calc_distribution()
            #if len(mass) > 0:
                #mass, row, col, kin_e = list(zip(*sorted(zip(mass, row, col, kin_e), reverse=True)))  
                #Sort this lists by mass to start the spreading from the middle
    
            for i in range(int(checked), len(cell_list)):  # Check if Cell already exists
                k = 0
                while k < len(row):
                    if (row[k] == cell_list[i].rowindex and col[k] == cell_list[i].colindex):
                        cell_list[i].add_mass(mass[k])
                        cell_list[i].add_parent(cells)
                        row = np.delete(row, k)
                        col = np.delete(col, k)
                        mass = np.delete(mass, k)
                        kin_e = np.delete(kin_e, k)
                    else:                                 
                        k += 1
             
            for k in range(len(row)):
                dem_ng = dem[row[k]-1:row[k]+2, col[k]-1:col[k]+2]  # neighbourhood DEM
                if nodata in dem_ng:
                    #checked += 1# Dirty way to don´t care about the edge of the DEM
                    continue
                cell_list.append(Cell(row[k], col[k], dem_ng, cellsize, mass[k], kin_e[k], cells, startcell))            
            #checked += 1         
            elh[cells.rowindex, cells.colindex] = max(elh[cells.rowindex, cells.colindex], cells.kin_e)
            mass_array[cells.rowindex, cells.colindex] = cells.mass
            #index_array[cells.rowindex, cells.colindex] = index
            #index += 1
        release[elh > 0] = 0  # Check if i hited a release Cell, if so set it to zero and get again the indexes of release cells
        #ToDo: if i hit a startcell add this "mass"
        #ToDo: Backcalulation
        row_list, col_list = get_start_idx(release)
        startcell_idx += 1
        

   
#Reading in the arrays
path = '/home/neuhauser/git_rep/graviclass/'
file = path + 'Fonnbu_dhm.asc'
release_file = path + 'class_1.asc'
infra_path = path + 'infra.tif'
# =============================================================================
# path = '/home/P/Projekte/18130-GreenRisk4Alps/Simulation/PAR3_Oberammergau/'
# file = path + 'DEM_10_3.tif'
# release_file = path + 'init/release_class_1.asc'
# =============================================================================
elh_out = path + 'energy_flowr_fonnbu.asc' # V3 with dh dependend on energylinehight
mass_out = path + 'mass_flowr_fonnbu.asc'
#index_out = path + 'index_flowr.asc'

dem, header = io.read_raster(file)
cellsize = header["cellsize"]
nodata = header["noDataValue"]
release, header_release = io.read_raster(release_file) 
#infra, header = io.read_raster(infra_path) 

elh = np.zeros_like(dem)
mass_array = np.zeros_like(dem)
#index_array = np.zeros_like(dem)

start = time.time()
#Core
cell_list = []  
calc_list = []
row_list, col_list = get_start_idx(release)
# =============================================================================
# for i in range(len(row_list)):
#     calc_list.append((row_list[i], col_list[i]))
# 
# 
# cpu_number = len(os.sched_getaffinity(0)) # counts number of cpu free.
# pool = Pool(processes=4)
# pool.map(calculation, calc_list)
# =============================================================================
calculation(row_list, col_list)

end = time.time()            
print('Time needed: ' + str(end - start) + ' seconds')

# Output
io.output_raster(file, elh_out, elh, 4326)
io.output_raster(file, mass_out, mass_array, 4326)
#io.output_raster(file, index_out, index_array, 4326)
    

