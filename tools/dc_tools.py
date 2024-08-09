import os

from CDMSDataCatalog import CDMSDataCatalog

def get_dataset(dc : CDMSDataCatalog, path : str = '/CDMS', site : str = 'All'):
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
        datasets = dc.client.search(path, query=self.query)
        # This retrieves recursively retrieves the datasets of all 
        # containers in the path.
        datasets.extend(dc.client.search(path+'**', query=self.query))
    except datacat.error.DcClientException as err:
            logging.error('%s: %s', err, path)
            return []
    except requests.exceptions.HTTPError as err:
            logging.error('HTTPError %s' % err)
            return []

    logging.info('Total datasets in %s : %s', path, len(datasets))
    return datasets

def register_files(dc : CDMSDataCatalog, datasets, path : str, site : str = 'SLAC'):

    # List of files that are registered
    registered_files = [dataset.path for dataset in datasets]

    files = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in
             os.walk(path) for f in filenames]
    for f in files:
        if f[f.find('/CDMS'):] in registered_files:
            print('File is registered.')

