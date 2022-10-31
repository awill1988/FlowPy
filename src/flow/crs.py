from rasterio import crs

def get_crs(dataset: OpenDataset) -> crs.CRS:
    try:
        dst_crs = crs.CRS.from_dict(dataset.crs.data)
    except:
        # todo log tis
        dst_crs = dst_crs.CRS.from_epsg(4326)
    return dst_crs
