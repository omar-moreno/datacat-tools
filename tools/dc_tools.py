import datacat
import logging
import os
import requests

from CDMSDataCatalog import CDMSDataCatalog

def get_dataset(dc : CDMSDataCatalog, path : str = '/CDMS', site : str = 'All', query : str = ''):
    """
    Recursively retrieve all datasets from the given path with a location
    as the specified site. If the path doesn't exist or the data catalog
    is down, an exception is thrown which results in an empty list being
    returned and an error logged.

    Args:
        path (str): The data catalog path to the dataset.
        site (str): The site (SLAC, SNOLAB, etc.) of a dataset location.

    Returns:
        list[]: A list containing all datasets in the given path.
    """
    try:
        #query = "scanStatus = 'UNSCANNED' or scanStatus = 'MISSING'"
        # First retrieve all dataset within the top level directory of the
        # given path.
        datasets = dc.client.search(path, site=site, query=query)
        # This retrieves recursively retrieves the datasets of all
        # containers in the path.
        datasets.extend(dc.client.search(path+'**', site=site, query=query))
    except datacat.error.DcClientException as err:
            logging.error('%s: %s', err, path)
            return []
    except requests.exceptions.HTTPError as err:
            logging.error('HTTPError %s' % err)
            return []

    logging.info('Total datasets in %s : %s', path, len(datasets))
    return datasets

def register_files(dc : CDMSDataCatalog, dc_path : str, path : str,  site : str = 'SLAC'):

    # Retrieve the dataset from the data catalog. The resulting dataset will be
    # used to check if the file has been registered with a location at the
    # given site.
    dataset = get_dataset(dc, dc_path, site)

    # Extract the resource path i.e. location on disk for each file in the
    # dataset
    registered_files = [data.path for data in dataset]

    # Retrieve a list of files on disk
    files = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in
             os.walk(path) for f in filenames]

    for f in files:
        fpath = f[f.find('/CDMS'):]
        if fpath not in registered_files:
            # Check if the file has been registered with any location. If so,
            # add a new location at the given site.
            if dc.exist(fpath):
                print('An entry in the DC exist for', f, '. Adding a new location.')
                dc.client.mkloc(fpath, site, f)
            else:
                print('File', f,'is not registered')

