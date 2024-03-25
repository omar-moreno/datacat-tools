# DataCat-Tools

This repo contains a collection of python tools used to manage the SuperCDMS data catalog.

### Crawler

### Watcher

The `watcher` is a python app that launches an instance of the data crawler in response to
changes in a given directory. Internally, the user specified directories are passed to 
the python package [`watchdog`](https://pypi.org/project/watchdog/) which provides callbacks
when files are changed, created and deleted. If a change is detected, the 
SuperCDMS data catalog entries associated with the parent directory of the file that was
changed are retrieved and updated accordingly.  

#### Requirements
* Python > 3.8
* DataCat
* watchdog
* Docker (if you want to use/generate the included image)

#### Configuration

The configuration is based on the toml language and includes the following parameters
`paths`: A list of paths that will be listened to for changes
`config`: Path to the DataCat client config
`site`: The site (e.g. SLAC, SNOLAB) of dataset that will be looked at.

An example configuration can be found below.

#### Starting the Watcher
