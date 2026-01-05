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


def load_config(config_path):
    """Load configuration from a TOML file."""
    with open(config_path, "rb") as f:
        config_data = tomli.load(f)

    if "catalog" not in config_data:
        logging.error(
            "[ crawler ] 'catalog' section is missing in the configuration file."
        )
        sys.exit(1)

    return config_data


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

    config_data = load_config(config)

    dc_config = None
    if "config" in config_data["catalog"]:
        dc_config = config_data["catalog"]["config"]
    logging.debug("Configuring the DC client from %s", dc_config)

    excluded_paths = []
    if "exclude" in config_data["crawler"]:
        excluded_paths = config_data["crawler"]["exclude"]
    logging.debug("Excluded paths %s", excluded_paths)

    dc = CDMSDataCatalog(config_file=dc_config)
    crawler = Crawler(dc, config_data)

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
