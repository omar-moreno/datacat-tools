# DataCat-Tools

This repo contains a collection of python tools used to manage the SuperCDMS data catalog.

### Crawler

### Watcher

The `watcher` is a python app that launches an instance of the data crawler in response to
changes in a given directory. Internally, the user specified directories are passed to 
the python package [`watchdog`](https://pypi.org/project/watchdog/) which provides callbacks
when files are changed, created and deleted. If a change is detected, the 
SuperCDMS data catalog entries associated with the parent directory of the changed file are 
retrieved and updated accordingly.  

#### Requirements
Outside of the DataCat package, all requirements can be installed via your operating systems
package manager or pip.  Docker is only needed if running off a provided docker image or 
if a docker image is built from the provided context.

* [python > 3.8](https://www.python.org/downloads/)
* [DataCat](https://gitlab.com/supercdms/DataHandling/DataCat)
* [watchdog](https://pythonhosted.org/watchdog/installation.html)
* [Docker](https://docs.docker.com/engine/install/) (if you want to use/generate the included image)

#### Configuration

The configuration format is based on the toml language and includes the following parameters:
* `paths`: A list of paths that will be listened to for changes.
* `config`: Path to the DataCat client config..
* `site`: The site (e.g. SLAC, SNOLAB) of the dataset that will be updated.

The following is an example configuration used to watch for changes to the path that contains
CUTE Run 37.
```
[listener]
paths = [ "/sdf/group/supercdms/data/CDMS/CUTE/R37" ]

[catalog]
config = "/path/to/config/prod.cfg"

[crawler]
site = "SLAC"
```

#### Starting the Watcher

##### Locally
Once all dependencies have been installled, the crawler can be started by issuing the following 
command within the top level directory of the repo
```
cd datacat-tools
python3 watcher -c config.toml
```

##### SLAC
The watcher at SLAC is run via docker as follows
```
docker run -v $(pwd):/local -v /sdf:/sdf watcher:0.1
```
The above assumes that the docker image has already been pulled from the repo and that the 
toml configuration is in the current working directory.
