# Select the temporary image and name it.
FROM python:3.8 as intermediate

MAINTAINER Omar Moreno <omoreno@slac.stanford.edu>

# Add a label that identifies this as an intermediate layer.
LABEL stage=intermediate

# The SSH key is passed as a build argument.
ARG SSH_KEY

# * Create an SSH directory.
# * Populate the private key file.
# * Set the correct permissions.
# * Add gitlab to the list of known host.
RUN mkdir -p /root/.ssh/ && \
    echo "$SSH_KEY" > /root/.ssh/id_ed25519 && \
    chmod -R 600 /root/.ssh/ && \
    ssh-keyscan -t ed25519 gitlab.com >> /root/.ssh/known_hosts

# Clone the data catalog repo into the itermediate image.
RUN git clone git@gitlab.com:supercdms/DataHandling/DataCat.git

# This is final base image
FROM python:3.8

# Update the image and install dependencies.
RUN apt-get update &&  \
    apt-get install -y \ 
        openssl

# Install python dependencies.
RUN pip install \
    tomli \
    watchdog

# Install all external packages into /opt.
WORKDIR /opt

# Copy the data catalog repo from the intermediate image.
COPY --from=intermediate /DataCat DataCat

# Install the data catalog module.
RUN cd DataCat && \
    pip install .

# Clone the crawler into /opt.
WORKDIR /opt
RUN git clone https://github.com/omar-moreno/datacat-tools.git 

# Start the crawler when the container is run. The directory /local is expected
# to point to the current working directory from which the container is run.
WORKDIR datacat-tools
CMD [ "python", "watcher", "-c", "/local/config.toml"]
