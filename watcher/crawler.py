
import datacat
import logging
import os
import time

from CDMSDataCatalog import CDMSDataCatalog
from datacat.error import DcClientException
from datetime import date
from datetime import datetime

class Crawler:

    def __init__(self, dc : CDMSDataCatalog, config):
        self.dc = dc

        if 'fs_prefix' not in config['crawler']: 
            raise ValueError('Failed to provide dataset prefix on filesystem.')
        self.fs_prefix = config['crawler']['fs_prefix']

        self.site = 'SLAC'
        if 'site' in config['crawler']:
            self.site = config['crawler']['site']

    def get_dataset(self, path : str = '/CDMS'):
        try: 
            # Get the childen in the path to check if a folder needs to be explored
            children = self.dc.client.children(path)
    
            # This retrieves all datasets in the path excluding folders. If the path
            # doesn't contain a dataset, an empty list is returned.
            #query = "scanStatus = 'UNSCANNED' or scanStatus = 'MISSING'" 
            query = ""
            datasets = self.dc.client.search(path, site=self.site, query=query)
        except DcClientException as err: 
            logging.error('%s: %s', err, path)
            return []
        except requests.exceptions.HTTPError as err:
            logging.error('HTTPError %s' % err)
            return []

        # Loop through all the children and recursively retrieve the datasets.
        for child in children:
            if isinstance(child, datacat.model.Folder):
                datasets.extend(self.get_dataset(child.path))
                continue

        logging.info('Total datasets in %s : %s', path, len(datasets))
        return datasets

    def crawl(self, path : str = '/CDMS'):
        datasets = self.get_dataset(path)

        for dataset in datasets:
            for loc in dataset.locations:
                if loc.site == self.site: 
                    payload = { 'locationScanned': datetime.utcnow().isoformat()+"Z" }
                    if os.path.exists(self.fs_prefix+loc.resource):
                        stat = os.stat(self.fs_prefix+loc.resource)
                        if loc.site == 'SLAC': payload['master'] = True
                        payload.update( {'scanStatus': 'OK', 'size': stat.st_size } )
                    elif loc.site == 'SNOLAB' and len(dataset.locations) > 1:
                        payload['scanStatus'] = 'ARCHIVED'
                        logging.info('File %s at %s has been ARCHIVED.', loc.resource, loc.site)
                    else: 
                        payload['scanStatus'] = 'MISSING'
                        logging.info('File %s at %s is MISSING.', loc.resource, loc.site)
                    
                    try: 
                        self.dc.client.patch_dataset(dataset.path, payload, site=self.site)
                    except DcException as err:
                        logging.error('DataCat Error: %s', err)
