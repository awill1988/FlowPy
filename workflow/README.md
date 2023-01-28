# ATES Workflow

The following document describes how the ATES workflow is designed to run.

## Order of Operations

The following enumerated steps are provisional and subject to be change:

0. Data Cleaning
1. Prepare rasters in Area of Interest
2. PRA
3. FlowPy
4. Overhead Hazard
5. autoATES

### 0. Data Cleaning

This step is quite manual and is best to consult with GIS engineers directly. Some notes are provided below:

- NLCD is converted to binary raster prior to clipping and reprojection using the following values: Land cover types 41, 42, 43 = 1; all else = 0

## References

- [ATES Order of Operations](https://docs.google.com/document/d/156T8371EGI_Bz2VdCdyaA4T1_aLul6cUir_AlSOiY8I/edit)
