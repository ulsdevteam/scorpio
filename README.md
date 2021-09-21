# scorpio

A microservice application to merge and index Collections, Objects, Agents and Terms.

scorpio is part of [Project Electron](https://github.com/RockefellerArchiveCenter/project_electron), an initiative to build sustainable, open and user-centered infrastructure for the archival management of digital records at the [Rockefeller Archive Center](http://rockarch.org/).

[![Build Status](https://travis-ci.org/RockefellerArchiveCenter/scorpio.svg?branch=base)](https://travis-ci.org/RockefellerArchiveCenter/scorpio)

## Setup

Install [git](https://git-scm.com/) and clone the repository

    $ git clone git@github.com:RockefellerArchiveCenter/scorpio.git

Install [Docker](https://store.docker.com/search?type=edition&offering=community) and run docker-compose from the root directory

    $ cd scorpio
    $ docker-compose up

Once the application starts successfully, you should be able to access the application in your browser at `http://localhost:8000`

When you're done, shut down docker-compose

    $ docker-compose down

Or, if you want to remove all data

    $ docker-compose down -v


## Configuring

Scorpio configurations are stored in `/scorpio/config.py`. This file is excluded from version control, and you will need to update this file with values for your local instance.

The first time the container is started, the example config file (`/scorpio/config.py.example`) will be copied to create the config file if it doesn't already exist.


## Services

scorpio has three services:
- Merge: merges DataObjects it receives by matching them with existing DataObjects.
- Add to index: Adds new or updated DataObjects to the index.
- Delete from index: Removes deleted DataObjects from its index


### Routes

| Method | URL | Parameters | Response  | Behavior  |
|--------|-----|---|---|---|
|GET, PUT, POST, DELETE|/objects||200|Returns data about DataObjects|
|POST|/index/add/|`clean` - whether or not to perform a clean index (i.e. index everything)|200|Adds new data to index|
|POST|/index/delete/|`source` - a source of the DataObject</br>`identifier` - the source's identifier for the DataObject|200|Deletes data from index|
|POST|/merge/||200|Merges DataObjects|
|GET|/status/||200|Return the status of the service|
|GET|/schema/||200|Returns the OpenAPI schema for this service|


## Development

This repository contains a configuration file for git [pre-commit](https://pre-commit.com/) hooks which help ensure that code is linted before it is checked into version control. It is strongly recommended that you install these hooks locally by installing pre-commit and running `pre-commit install`.


## License

This code is released under an [MIT License](LICENSE).
