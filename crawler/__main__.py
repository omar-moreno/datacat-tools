import argparse
import tomli
import logging

from crawler import Crawler
from CDMSDataCatalog import CDMSDataCatalog
from datetime import date

log_fn = ('%s_crawler.log' % date.today().isoformat())
logging.basicConfig(filename=log_fn, level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Parse the command line arguments
parser = argparse.ArgumentParser(
         description='Data catalog crawler used by the SCDMS experiment.')
parser.add_argument('-c', action='store', dest='config',
                    help='Path to TOML based configuration file.')
args = parser.parse_args()

if not args.config: 
    parser.error('[ crawler ] A config file needs to be specified.')

config = None
with open(args.config, 'rb') as f: 
    config = tomli.load(f)

dc_config = None
if 'config' in config['catalog']: 
    dc_config = config['catalog']['config']

dc = CDMSDataCatalog(config_file=dc_config)
crawler = Crawler(dc, config)

while True: 
    paths = []
    for path in dc.ls():

        paths.extend(dc.ls(path))

    for path in paths:
        logging.info('Processing %s', path)
        crawler.crawl(path)

