import logging
import os
import time

import datacat
from CDMSDataCatalog import CDMSDataCatalog
from datacat.error import DcException
from datetime import datetime


class Crawler:
    """
    SuperCDMS data catalog crawler used to perform various checks on the
    registered datasets in the given path.

    Attributes:
        dc (CDMSDataCatalog): An instance of the CDMSDataCatalog client.
        config (dict): Dictionary with parameters used to configure this
            class.
    """

    def __init__(self, dc: CDMSDataCatalog, config: dict):
        """
        Constructor of the class Crawler.

        Args:
            dc (CDMSDataCatalog): An instance of the CDMSDataCatalog client.
            config (dict): Dictionary with parameters used to configure this
                class.
        """
        self.dc = dc

        self.site = "All"
        if "site" in config["crawler"]:
            self.site = config["crawler"]["site"]

        self.query = ""
        if "query" in config["crawler"]:
            self.query = config["crawler"]["query"]

        self.missing_files = set()

    def get_dataset(self, path: str = "/CDMS", site: str = "All"):
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
            # query = "scanStatus = 'UNSCANNED' or scanStatus = 'MISSING'"
            # First retrieve all dataset within the top level directory of the
            # given path.
            datasets = self.dc.client.search(path, query=self.query, site=site)
            # This retrieves recursively retrieves the datasets of all
            # containers in the path.
            datasets.extend(
                self.dc.client.search(path + "**", query=self.query, site=site)
            )
        except datacat.error.DcClientException as err:
            logging.error("%s: %s", err, path)
            return []
        except requests.exceptions.HTTPError as err:
            logging.error("HTTPError %s" % err)
            return []

        logging.info("Total datasets in %s : %s", path, len(datasets))
        return datasets

    def crawl(self, path: str = "/CDMS") -> None:
        """
        Perform a series of checks on all datasets within a path and update the
        scan status of a dataset to reflect the results.  Currently, if a
        dataset exist, the size of the file and the locationScanned timestamp
        are both updated.  If a dataset contains a location with site SLAC,
        the location is made the 'Master' location. If a dataset at SNOLAB is found
        to be missing but a copy exist at SLAC, the dataset is marked as 'ARCHIVED'.

        Args:
            path (str): The data catalog path to the dataset.

        """
        try:
            datasets = self.get_dataset(path, self.site)
        except requests.exceptions.HTTPError as err:
            logging.error("HTTPError %s" % err)
            return

        for dataset in datasets:
            try:
                locations = dataset.locations
                logging.info('Dataset: %s', dataset)
            except AttributeError as err:
                logging.error("AttributeError: %s", err)
                logging.error("Dataset %s doesn't have a location.", dataset)
                continue

            for loc in locations:
                if loc.site == self.site:
                    payload = {
                        "locationScanned": datetime.utcnow().isoformat() + "Z"
                    }
                    if os.path.exists(loc.resource):
                        stat = os.stat(loc.resource)
                        if loc.site == "SLAC":
                            payload["master"] = True
                        payload.update(
                            {"scanStatus": "OK", "size": stat.st_size}
                        )
                    elif loc.site == "SNOLAB" and len(dataset.locations) > 1:
                        payload["scanStatus"] = "ARCHIVED"
                        logging.info(
                            "%s %s from %s",
                            payload["scanStatus"],
                            loc.resource,
                            loc.site
                        )
                    else:
                        payload["scanStatus"] = "MISSING"
                        logging.info(
                            "%s %s from %s",
                            payload["scanStatus"],
                            loc.resource,
                            loc.site
                        )
                        self.missing_files.add(dataset.path)
                    try:
                        self.dc.client.patch_dataset(
                            dataset.path, payload, site=self.site
                        )
                    except DcException as err:
                        logging.error(
                            "DataCat Error: %s when patching path %s",
                            err,
                            dataset.path,
                        )
        logging.info('Missing datasets: %s', len(self.missing_files))
