# dq-packer-tableau-linux

This repo is used to build a Linux based EC2 instance running Tableau server.

## Features

### `.drone.yml`
This file drives the build and deployment of the EC2 image to be built.

### `packer.json`
This file contains a wrap up for Ansible script to be run inside a Centos Linux image.

### `playbook.yml`
Ansible playbook installing the following:
- Various packages as dependencies
- Add bash scripts
- Create users and cronjobs
- Install a number of applications eg. Tableau
- Setup Cloudwatch agent

#### `tableau-scripts`
- an assortment of various bash scripts to be used by the Tableau user upon build and initial configuration
- some of the scripts are one off but others can be reused for troubleshooting/maintenance purposes

### `config`
- Tableau template document

### `scripts`
- Bash script that runs the Cloudwatch agent

## Deploying / Publishing
Drone min ver 0.5 is needed to deploy with `.drone.yaml` file

## Licensing
The code in this project is licensed under this [`LICENSE`](./LICENSE)
