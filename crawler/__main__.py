import logging
import sys
import time

import click
import tomli
from CDMSDataCatalog import CDMSDataCatalog

from crawler import Crawler

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@click.command()
@click.option(
    "-c",
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to TOML based configuration file.",
)
def main(config):
    """Data catalog crawler used by the SCDMS experiment."""

    # Load config from TOML file
    with open(config, "rb") as f:
        config = tomli.load(f)

    dc_config = None
    if "config" in config["catalog"]:
        dc_config = config["catalog"]["config"]
    logging.debug("Configuring the DC client from %s", dc_config)

    excluded_paths = []
    if "exclude" in config["crawler"]:
        excluded_paths = config["crawler"]["exclude"]
    logging.debug("Excluded paths %s", excluded_paths)

    dc = CDMSDataCatalog(config_file=dc_config)
    crawler = Crawler(dc, config)

    paths = None
    while not paths:
        paths = dc.ls()
        if not paths:
            time.sleep(10)

    logging.debug("Paths: %s", paths)
    paths = list(set(paths).difference(excluded_paths))

    while True:
        for path in paths:
            cpaths = dc.ls(path)
            if not cpaths:
                logging.error("Skipping: %s", cpaths)
                continue
            for cpath in cpaths:
                try:
                    logging.debug("Processing %s", cpath)
                    crawler.crawl(cpath)
                except Exception:
                    logging.error("Skipping path after exception %s", cpath)
        # logging.info('Missing datasets: %s', len(self.missing_files))


if __name__ == "__main__":
    main()
