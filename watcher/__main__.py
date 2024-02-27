
import argparse
import tomli

from listener import Listener

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

listener = Listener(config)
listener.run()



