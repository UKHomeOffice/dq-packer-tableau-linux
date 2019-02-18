# This script publishes the required tableau artefacts

# First it reads a flag to decide what needs to be published, either:
# 1. Nothing
# 2. Everything from a specific site
# 3. Specific elements (in comma separated list)

# All artefacts are found in Git
# Assume Git structure:
#REPO
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


# Global vars
if len(sys.argv) == 2:
    site = sys.argv[1]
else:
    print "Usage: " + sys.argv[0] + " [SITE]"
    sys.exit(1)
home_dir = os.environ['HOME']



# Define a function to read ALL artefacts from Git REPO
def read_artefacts_all(repo_name):
    # Get all DataSource Projects
    ds_list = []

    print ("repo name = <" + repo_name + ">")
    for proj_ds in listdir(os.path.join(home_dir, repo_name, 'datasources')):
        print ("proj = <" + proj_ds + ">")
        for ds in listdir(os.path.join(home_dir, repo_name, 'datasources', proj_ds)):
            print ("ds = <" + ds + ">")
            full_ds = []
            full_ds.append(site)
            full_ds.append(proj_ds)
            full_ds.append(ds)
            ds_list.append(full_ds)

        print ds_list


# Define a function to read Specific artefacts from environment variable
def read_artefacts_specific():
    pass

# Start here
# Create an array of DataSources
# Read OS Env var to determine operation
ds_to_pub = os.environ["DATASOURCES_TO_PUBLISH"]

if ds_to_pub == '':
    import sys
    sys.exit(0)
elif ds_to_pub.upper() == 'ALL':
    read_artefacts_all(os.environ["TAB_INT_REPO_NAME"])
else:
    read_artefacts_specific()

# Log in to Tableau Server (with helper script)
#return_code = subprocess.call("~/scripts/tableau-login.sh")

# Iterate through each array calling helper script to publish each element
