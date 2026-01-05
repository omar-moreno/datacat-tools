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


def initialize_catalog(config_data):
    """Initialize the CDMSDataCatalog and crawler."""
    dc_config = config_data["catalog"].get("config")

    excluded_paths = config_data["crawler"].get("exclude", [])
    logging.debug(
        f"Initializing DC client from {dc_config} with excluded paths: {excluded_paths}"
    )

    dc = CDMSDataCatalog(config_file=dc_config)
    return dc, excluded_paths


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
    dc, excluded_paths = initialize_catalog(config_data)

    paths = []
    while not paths:
        paths = dc.ls() or []
        if not paths:
            time.sleep(10)

    logging.debug(f"Paths: {paths}")
    paths = list(set(paths) - set(excluded_paths))

    # Instantiate the crawler
    crawler = Crawler(dc, config_data)

    while True:
        for path in paths:
            cpaths = dc.ls(path) or []
            if not cpaths:
                logging.error(f"Skipping: {path} - no contents found.")
                continue

            for cpath in cpaths:
                try:
                    logging.debug(f"Processing {cpath}")
                    crawler.crawl(cpath)
                except Exception as e:
                    logging.error(f"Skipping {cpath} after exception: {e}")
        # logging.info('Missing datasets: %s', len(self.missing_files))


if __name__ == "__main__":
    main()
