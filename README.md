# datacat-tools

This repo contains a collection of tools used to manage the SuperCDMS data catalog. 

### watcher

The `watcher` is a python tool use to launch an instance of the data crawler whenever a
change in a given directory is observed.  

#### Requirements


#### Configuration

The configuration is based on the toml language and includes the following parameters
`paths`: A list of paths that will be listened to for changes
`config`: Path to the DataCat client config
`site`: The site (e.g. SLAC, SNOLAB) of dataset that will be looked at.

An example configuration can be found below.

#### Starting the Watcher
