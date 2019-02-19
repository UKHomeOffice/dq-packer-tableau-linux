# This script publishes the required tableau artefacts

# First it reads a flag to decide what needs to be published, either:
# 1. Nothing
# 2. Everything from a specific site
# 3. Specific elements (in comma separated list)

# All artefacts are found in Git
# Assume Git structure:
# REPO
# |-- README.md
# |-- datasources
# |   |-- Project1
# |   |   |-- DataSource1
# |   |   |-- DataSource2
# |   |-- Project2
# |   |   |-- DataSource1
# |   |   |-- DataSource2
# |-- workbooks
# |   |-- Project1
# |   |   |-- WorkBook1
# |   |   |-- WorkBook2
# |   |-- Project2
# |   |   |-- WorkBook1
# |   |   |-- WorkBook2

# imports
import sys
import os
from os import listdir
import subprocess


# Define a function to read ALL artefacts from Git REPO
# Assume that all artefacts are for the SITE passed in to this python script
# Future enhancement: Site will be the highest level directory within repo
def read_artefacts_all(repo_name):
    # Get all DataSource Projects
    ds_list = []

    if verbose >= 1:
        print ("repo name = <" + repo_name + ">")
    for proj_ds in listdir(os.path.join(repo_name, 'datasources')):
        if verbose >=1:
            print ("proj = <" + proj_ds + ">")
        for ds in listdir(os.path.join(repo_name, 'datasources', proj_ds)):
            if verbose >= 3:
                print ("ds = <" + ds + ">")
            full_ds = []
            full_ds.append(site)
            full_ds.append(proj_ds)
            full_ds.append(ds)
            ds_list.append(full_ds)
    if verbose >= 2:
        print ds_list
    return ds_list


# Define a function to read Specific artefacts from environment variable
def read_artefacts_specific():
    pass

# Define a function to publish all of the artefacts read previously
def publish_datasources(repo_name, ds_list_to_pub):
    for ds_to_pub in ds_list_to_pub:
        if verbose >= 2:
            print "ds_to_pub = <"
            for elem in ds_to_pub:
                print elem
            print ">"
        project = ds_to_pub[1]
        ds_file = os.path.join(repo_name, 'datasources', project, ds_to_pub[2])
        if verbose >= 2:
            print "Calling tableau-pub-ds.sh with args " + project + ds_file
        return_code = subprocess.call([os.path.join(home_dir, "scripts", "tableau-pub-ds.sh"), project, ds_file])

# Define usage function
# Future enhancement: Site will be the highest level directory within repo - so, not passed in
def usage():
    print "Usage: " + sys.argv[0] + " [REPO] [SITE]"
    sys.exit(1)

##################
### START HERE ###
##################
# Global vars
home_dir = os.environ['HOME']
verbose = 1
# USAGE
if len(sys.argv) == 3:
    repo = sys.argv[1]
    if not os.path.isdir(repo):
        print "Cannot find repository (" + repo + ")"
        print "Please provide full path to repository directory."
        usage()
    site = sys.argv[2]
else:
    usage()


# Create an array of DataSources
# Read OS Env var to determine operation
ds_to_pub = os.environ["DATASOURCES_TO_PUBLISH"]

if ds_to_pub == '':
    import sys
    sys.exit(0)
elif ds_to_pub.upper() == 'ALL':
    ds_list = read_artefacts_all(repo)
else:
    ds_list = read_artefacts_specific()

# Log in to Tableau Server (with helper script)
return_code = subprocess.call([os.path.join(home_dir, "scripts", "tableau-login.sh"), site])
if return_code != 0:
    print "Error calling: " + os.path.join(home_dir, "scripts", "tableau-login.sh") + " " + site
    sys.exit(return_code)

# Iterate through each array calling helper script to publish each element
publish_datasources(repo, ds_list)
